#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Curtis Galloway
# SPDX-License-Identifier: Apache-2.0
"""What actually happened when the manifest was used for a week of real work.

    ./usagereport.py                          # the last 7 days, sweeping ~/src
    ./usagereport.py --from 2026-08-24 --to 2026-08-30
    ./usagereport.py --root /Users/me/src --root /Users/me/work
    ./usagereport.py --mark                   # record that this window was read

Stage 6 of the survey cycle. The catalog says what is on offer, the corpus says
how a model did on a fixture, and neither says whether the thing was any use on
a Tuesday. This reads `ox`'s own run logs -- which carry the manifest path, its
sha256, and the full attempt list including skips -- and answers the questions
that decide next week's shortlist:

  - Which entry actually served the work? A manifest whose rank 1 is skipped
    every single time is mis-ranked for how ox is really invoked.
  - Which entries were never reached at all? An untested bench is not a bench.
  - What failed, what truncated, and what did it cost?

Three counting rules, each of which was wrong somewhere before it was written
down:

  - **A dry run is not a run.** It writes meta.json, request.json and
    status.json but never calls anyone. `status.json` says `dry_run`, and 61
    log dirs on the machine this was written against included several. Counting
    them inflates usage and, worse, reports a model as reachable on the
    strength of a request that was never sent.
  - **A skipped attempt is evidence, not noise.** `attempts[]` records every
    entry ox walked past and why. "cost=paid (pass --allow-paid to use it)"
    repeated forty times is the single most actionable line in the report.
  - **Logs must outlive the window.** Nothing in ox prunes them and nothing
    guarantees they survive, so --mark writes a watermark saying how far the
    survey has read. A pruner that respects it cannot delete unscraped runs.

Log discovery is a filesystem sweep, and the failure that matters is a silent
one: a repo missed is a week of usage reported as quieter than it was. Every
root swept and every directory skipped is printed, and --root is repeatable
rather than a single guess.
"""

import argparse
import json
import os
import sys
from pathlib import Path

import costcheck

DEFAULT_ROOTS = [Path.home() / "src"]
WATERMARK = ".oxsurvey-scraped.json"


def find_runs(roots):
    """Every ox log directory under the given roots, plus what was skipped."""
    runs, swept, skipped = [], [], []
    for root in roots:
        root = Path(root).expanduser()
        if not root.is_dir():
            skipped.append("%s: not a directory" % root)
            continue
        swept.append(str(root))
        # <root>/<repo>/logs/<stamp>/ is where ox puts them, because it anchors
        # ./logs at the working directory. A deeper sweep would find them in
        # nested checkouts too, at the cost of walking node_modules.
        # Discover by meta.json as well as status.json. ox writes meta.json
        # before it calls anyone and status.json after it has an answer or an
        # error, so a run killed in between -- a timeout the caller interrupted,
        # a crash, a machine that slept -- leaves meta.json and no status. Those
        # are exactly the runs worth counting: globbing only status.json made
        # them invisible rather than failed. Three paniolo runs on 2026-09-19
        # were in that state.
        for pattern in ("*/logs/*/status.json", "*/*/logs/*/status.json",
                        "*/logs/*/meta.json", "*/*/logs/*/meta.json"):
            for found in root.glob(pattern):
                runs.append(found.parent)
    return sorted(set(runs)), swept, skipped


def write_watermark(log_dir, through, scraped_from, runs):
    """Record how far the survey has read, in the form a pruner will compare.

    Two things here are not cosmetic.

    **scraped_through is a directory name, not an ISO timestamp.** ox names run
    directories 2026-08-30T16-05-13Z, with dashes in the time. A watermark
    written as 2026-08-30T16:05:13 cannot be compared against those by the
    obvious string comparison, and it fails in the dangerous direction: "-" is
    0x2D and ":" is 0x3A, so within the same hour every directory name sorts
    BELOW the watermark. A pruner would judge an unread run already read and
    delete it. Writing the same shape the directories use makes
    `dirname > scraped_through` correct with no parsing at all, which is what a
    shell script or a hand-pruner will actually do.

    **The write is atomic.** A half-written watermark is the case that breaks a
    pruner: it is neither absent (age governs) nor valid (the rule governs), and
    a reader that treats it as absent deletes evidence. Writing to a temporary
    file in the same directory and renaming means a reader sees the old file or
    the new one, never a fragment.
    """
    payload = {
        "scraped_through": through,
        "scraped_through_iso": stamp_to_iso(through),
        "scraped_from": scraped_from,
        "runs": runs,
        "contract": (
            "Do not delete a run directory whose name sorts above "
            "scraped_through; the survey has not read it yet, whatever its age. "
            "Compare directory names directly -- scraped_through is written in "
            "the same form ox names run directories. If this file is absent, no "
            "survey has read this directory and age alone governs. If it is "
            "present but unreadable, prune nothing: an unparseable watermark is "
            "not an absent one."),
    }
    temp = log_dir / (WATERMARK + ".tmp")
    temp.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    os.replace(str(temp), str(log_dir / WATERMARK))


def run_order(name):
    """Sort key for a run directory name, ordering the collision suffix numerically.

    `max()` over the raw names is lexicographic, and ox's suffix is a decimal
    counter with no padding (`claim_log_dir` increments until `create_dir`
    succeeds), so `...Z-10` sorts BELOW `...Z-2`. The watermark written from a
    lexicographic max therefore names an earlier directory than the one the
    survey actually read through, which is a false statement in a durable
    artifact even where it costs nothing.

    It costs nothing today because the suffix never changes which *second* a
    run belongs to -- `stamp_to_iso` drops it, so every run claiming the same
    second is inside or outside the window together, and the ones sorting below
    a lexicographic watermark have therefore already been read. That is why
    this is a correctness fix to the recorded value rather than a data-loss fix.
    Reported by an outside review of this file on 2026-09-20.
    """
    base, _, suffix = name.partition("Z-")
    if not suffix or not suffix.isdigit():
        return (name, 0)
    return (base + "Z", int(suffix))


def stamp_to_iso(name):
    """2026-08-30T16-05-13Z -> 2026-08-30T16:05:13, for a human reading it.

    A second run claimed in the same second is named 2026-08-30T16-05-13Z-2 by
    both oxbox implementations (see docs/log-contract.md). The suffix orders
    the directory names and is not part of the time, so everything after the
    Z is dropped here rather than turned into a fourth colon field.
    """
    bare = name.split("Z", 1)[0]
    return bare[:11] + bare[11:].replace("-", ":")


def read_status(run_dir):
    path = Path(run_dir) / "status.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def incomplete_status(run_dir):
    """A status record for a run that never wrote one, or None if it cannot.

    Built from meta.json and error.txt. It is marked `no_status` so a reader
    can tell a reconstructed record from one ox wrote, and it is never `ok`:
    a run that did not file a status did not finish, whatever else is true.
    `dry_run` is read from meta so a dry run stays excluded even here.
    """
    run_dir = Path(run_dir)
    try:
        meta = json.loads((run_dir / "meta.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    error = ""
    try:
        error = (run_dir / "error.txt").read_text(encoding="utf-8").strip()
    except OSError:
        pass
    return {
        "ok": False,
        "no_status": True,
        "dry_run": bool(meta.get("dry_run")),
        "model": meta.get("model"),
        "venue": meta.get("venue"),
        "mode": meta.get("mode"),
        "error": error or "no status.json and no error.txt: the run did not finish",
    }


def collect(run_dirs, start, end):
    """Split runs into real ones, dry runs, and those outside the window."""
    real, dry, outside, unreadable = [], [], 0, []
    for run_dir in run_dirs:
        status = read_status(run_dir)
        if status is None:
            status = incomplete_status(run_dir)
            if status is None:
                unreadable.append(str(run_dir))
                continue
        # The directory name is the run stamp; ox writes it as 2026-08-30T01-11-26Z
        # (or ...Z-2 on a same-second collision), so the time separators have to
        # come back, and the suffix go, before it compares.
        stamp = stamp_to_iso(run_dir.name)
        if (start and stamp < start) or (end and stamp > end):
            outside += 1
            continue
        record = dict(status)
        record["dir"] = run_dir
        record["repo"] = run_dir.parent.parent.name
        record["stamp"] = stamp
        (dry if status.get("dry_run") else real).append(record)
    return real, dry, outside, unreadable


def manifest_entries(records):
    """Every manifest named by a run, read back so unused entries show up.

    ox 0.5.0 keeps the bytes a run used as `manifest.json` beside its
    request, and names the manifest by URL when it fetched one. Prefer that
    copy over the recorded path: `latest.json` says something different each
    issue, and a file on disk may have been edited since the run. Two runs
    naming the same path with different digests used two manifests, and are
    listed as two.
    """
    manifests = {}
    for record in records:
        info = record.get("manifest") or {}
        path = info.get("path")
        if not path:
            continue
        sha = info.get("sha256")
        key = path
        seen = manifests.get(path)
        if seen is not None and sha and seen.get("sha_seen") not in (None, sha):
            key = "%s@%s" % (path, sha[:12])
        if key in manifests:
            continue
        copy = Path(record["dir"]) / "manifest.json"
        source = copy if copy.is_file() else Path(path)
        try:
            data = json.loads(source.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            manifests[key] = {"error": "unreadable now", "sha_seen": sha}
            continue
        manifests[key] = {
            "entries": [(rec.get("venue"), rec.get("model"), rec.get("cost"))
                        for rec in data.get("recommendations") or []],
            "sha_seen": sha,
        }
    return manifests


def tally(records):
    used, skips, failures, truncated = {}, {}, [], 0
    tokens = {}
    for record in records:
        for attempt in record.get("attempts") or []:
            key = (attempt.get("venue"), attempt.get("model"))
            if attempt.get("skipped"):
                skips.setdefault((key, attempt["skipped"]), 0)
                skips[(key, attempt["skipped"])] += 1
            else:
                used[key] = used.get(key, 0) + 1
        if not record.get("ok"):
            failures.append((record["stamp"], record.get("model"),
                             (record.get("error") or "")[:70]))
        if record.get("truncated"):
            truncated += 1
        model = record.get("model")
        row = tokens.setdefault(model, {"runs": 0, "prompt": 0, "completion": 0,
                                        "reasoning": 0})
        row["runs"] += 1
        for field in ("prompt", "completion", "reasoning"):
            row[field] += record.get(field + "_tokens") or 0
    return used, skips, failures, truncated, tokens


def render(real, dry, outside, unreadable, swept, skipped, window, manifests):
    out = []
    c = costcheck.commas
    out.append("### Usage")
    out.append("")
    out.append("Window: %s .. %s. Swept: %s.%s" % (
        window[0] or "start", window[1] or "end", ", ".join(swept) or "nothing",
        (" Skipped: %s." % "; ".join(skipped)) if skipped else ""))
    out.append("")
    if unreadable:
        out.append("**%d log directories could not be read** (%s) -- the window is "
                   "under-reported by that much." % (len(unreadable),
                                                     ", ".join(unreadable[:3])))
        out.append("")
    if not real:
        out.append("No real runs in the window. %d dry runs and %d runs outside it."
                   % (len(dry), outside))
        return "\n".join(out)

    used, skips, failures, truncated, tokens = tally(real)
    repos = sorted({r["repo"] for r in real})
    modes = sorted({r.get("mode") for r in real if r.get("mode")})
    out.append("%d runs across %s, modes %s. %d dry runs excluded; %d runs outside "
               "the window." % (len(real), ", ".join(repos), "/".join(modes),
                                len(dry), outside))
    out.append("")

    out.append("| model | runs | prompt | completion | reasoning |")
    out.append("|---|---|---|---|---|")
    for model in sorted(tokens):
        row = tokens[model]
        out.append("| `%s` | %s | %s | %s | %s |" % (
            model, row["runs"], c(row["prompt"]), c(row["completion"]),
            c(row["reasoning"])))
    out.append("")

    if skips:
        out.append("**Entries walked past**")
        out.append("")
        out.append("| entry | times | reason |")
        out.append("|---|---|---|")
        for ((venue, model), reason), count in sorted(
                skips.items(), key=lambda kv: -kv[1]):
            out.append("| `%s` / `%s` | %s | %s |" % (venue, model, count, reason))
        out.append("")

    # The bench nobody called. This is the line that should change next week's
    # manifest: an entry that was never reached has earned nothing, and an entry
    # that was never reached because the one above it always worked is a
    # different fact from one that was skipped on cost.
    for path, info in sorted(manifests.items()):
        if info.get("error"):
            out.append("Manifest `%s` is %s; unused entries cannot be listed."
                       % (path, info["error"]))
            continue
        touched = set(used) | {key for (key, _) in skips}
        never = [e for e in info["entries"] if (e[0], e[1]) not in touched]
        if never:
            out.append("**Never reached** in `%s`: %s." % (
                Path(path).name,
                ", ".join("`%s` (%s)" % (model, cost) for _, model, cost in never)))
            out.append("")

    reconstructed = [r for r in real if r.get("no_status")]
    if reconstructed:
        # Named separately because it is a different fact from a run that
        # failed and said so. A run with no status.json never got to file one,
        # so the reason is whatever error.txt holds -- or nothing at all, which
        # is the interesting case: the run simply stopped.
        silent = [r for r in reconstructed
                  if "did not finish" in (r.get("error") or "")]
        out.append("**%d run(s) never wrote a status.json** and are counted as "
                   "failures from meta.json and error.txt%s."
                   % (len(reconstructed),
                      "; %d of those left no error.txt either, so nothing "
                      "records why they stopped" % len(silent) if silent else ""))
        out.append("")

    if failures:
        out.append("**Failures**")
        out.append("")
        for stamp, model, error in failures:
            out.append("- `%s` %s -- %s" % (stamp, model, error or "no error text"))
        out.append("")
    out.append("%d of %d runs reported truncated output." % (truncated, len(real)))
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(
        description="What the manifest actually did for a week of real work.")
    parser.add_argument("--root", action="append", default=[],
                        help="directory holding repos to sweep; repeatable "
                             "(default: ~/src)")
    parser.add_argument("--from", dest="start", help="window start, UTC")
    parser.add_argument("--to", dest="end", help="window end, UTC")
    parser.add_argument("--mark", action="store_true",
                        help="after reporting, write %s into each swept root, "
                             "recording how far the survey has read so a pruner "
                             "cannot delete unscraped runs" % WATERMARK)
    args = parser.parse_args()

    roots = args.root or DEFAULT_ROOTS
    start, end = costcheck.parse_stamp(args.start), costcheck.parse_stamp(args.end)
    run_dirs, swept, skipped = find_runs(roots)
    real, dry, outside, unreadable = collect(run_dirs, start, end)
    manifests = manifest_entries(real)
    print(render(real, dry, outside, unreadable, swept, skipped, (start, end),
                 manifests))

    if args.mark:
        # One watermark per logs directory, not per sweep root: a pruner runs
        # inside the repo it is pruning, and it should find the contract next
        # to the runs it is about to delete rather than by walking upwards to
        # wherever the survey happened to be pointed.
        for log_dir in sorted({r["dir"].parent for r in real}):
            covered = [r for r in real if r["dir"].parent == log_dir]
            through = max((r["dir"].name for r in covered), key=run_order)
            write_watermark(log_dir, through, start, len(covered))
            print("\nwatermark -> %s" % (log_dir / WATERMARK))
        if not real:
            print("\nno runs in the window; no watermark written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
