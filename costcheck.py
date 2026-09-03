#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Curtis Galloway
# SPDX-License-Identifier: Apache-2.0
"""Both halves of what a corpus run costs: the model's tokens, and ours.

Standard library only, which is why the timestamp handling is hand-rolled:
datetime.fromisoformat did not parse a Z suffix until 3.11 and the floor is 3.9.

    ./costcheck.py --run ../oxbox/logs/2026-08-30T01-11-26Z
    ./costcheck.py --run <dir> --from 2026-08-30T00:50Z --to 2026-08-30T02:10Z
    ./costcheck.py --session <uuid or path>        # whole-session totals

A free model is not free. It emits findings, and then something has to read
every one of them against the source and decide which are real -- that is the
expensive half, it is paid in the reviewing agent's tokens, and until now the
survey never counted it. A model that emits fifteen findings with two false
positives can cost more to use than a paid one that emits five clean.

So this prints two figures side by side:

  under test   prompt / completion / reasoning, from the ox run's response.json.
               Exact: it is the provider's own accounting of the request.
  harness      input / output / cache, from this agent's session transcript,
               summed over a stated window and split main-thread vs subagent.

**The harness figure is an upper bound, and the window is printed with it.**
Anything else the session did in that window is in the number. Narrow the
window with --from/--to when the session was doing more than one thing, and
say in the observation which window was used. A number without its window is
not a measurement.

Two things about the transcript that are easy to get wrong, and were:

  - **One API response appears as several records** -- one per content block
    (thinking, then text, then each tool_use), each repeating the *same* usage
    block in full. Summing records over-counts badly: 464 records for 175
    responses in the session this was written against, so a naive sum inflates
    the answer by 2.6x. Dedupe on message id.
  - **Cache reads are not input tokens.** They are counted and priced
    differently, and on a long agent session they dominate everything else by
    an order of magnitude. They are reported in their own column and never
    folded into input.

Transcript layout (~/.claude/projects/<cwd with / replaced by ->/<session>.jsonl)
is a harness-internal convention, not a published interface. If it moves, this
script says so and exits rather than guessing; --session takes an explicit path.
"""

import argparse
import json
import re
import sys
from pathlib import Path

TRANSCRIPT_ROOT = Path.home() / ".claude" / "projects"
CATALOG_ROOT = Path(__file__).resolve().parent / "catalogs"


def die(message):
    sys.exit("costcheck: " + message)


def project_key(path):
    """The transcript directory name for a working directory."""
    return str(Path(path).resolve()).replace("/", "-")


def parse_stamp(text):
    """Accept 2026-08-30T01:11:26Z, ...T01:11Z, or a whole day."""
    if text is None:
        return None
    raw = text.strip().replace("z", "Z")
    if re.match(r"^\d{4}-\d{2}-\d{2}$", raw):
        raw += "T00:00:00Z"
    elif re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}Z$", raw):
        raw = raw[:-1] + ":00Z"
    if not re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", raw):
        die("cannot read timestamp %r; use 2026-08-30T01:11:26Z" % text)
    # Lexicographic comparison is exact for this format, so no datetime needed
    # and no timezone can be got wrong: everything here is UTC and Z-suffixed.
    return raw[:19]


def newest_catalog(venue):
    """The most recent archived catalog for a venue, or None."""
    found = sorted((CATALOG_ROOT / venue).glob("*.json")) if venue else []
    return found[-1] if found else None


def price_from_catalog(catalog_path, model):
    """USD per token (prompt, completion) for a model, from an archived catalog.

    Only the OpenRouter shape is read: pricing.prompt / pricing.completion as
    decimal strings per token. Other venues' archives carry price differently
    or not at all, and a guess here would be a number nobody measured.
    """
    data = json.loads(Path(catalog_path).read_text(encoding="utf-8"))
    if data.get("venue") != "openrouter":
        return None
    rows = (data.get("payload") or {}).get("data") or []
    for row in rows:
        if row.get("id") == model:
            pricing = row.get("pricing") or {}
            try:
                return float(pricing.get("prompt")), float(pricing.get("completion"))
            except (TypeError, ValueError):
                return None
    return None


def price_run(run, catalog_path=None):
    """Attach a computed USD figure to a run, and say where the price came from.

    Computed, not billed: OpenRouter only returns the billed figure when the
    request asks for it, and ox does not. Reasoning tokens are inside the
    completion count and are billed as output, so completion * output price
    already covers them. Cached prompt tokens are priced lower and are not
    corrected for -- none of the corpus runs so far had any.
    """
    run["usd"], run["priced_from"] = None, None
    if run.get("prompt") is None or run.get("completion") is None:
        return run
    path = Path(catalog_path) if catalog_path else newest_catalog(run.get("venue"))
    if not path or not path.exists():
        return run
    prices = price_from_catalog(path, run.get("model"))
    if prices is None:
        return run
    run["usd"] = run["prompt"] * prices[0] + run["completion"] * prices[1]
    run["priced_from"] = path.name
    return run


def read_run(run_dir):
    """The model-under-test half, from an ox log directory."""
    run = Path(run_dir)
    meta_path, response_path = run / "meta.json", run / "response.json"
    if not meta_path.exists():
        die("no meta.json in %s -- is that an ox log directory?" % run)
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    out = {
        "model": meta.get("model"),
        "venue": meta.get("venue"),
        "mode": meta.get("mode"),
        "files": meta.get("files") or [],
        "context_bytes": meta.get("context_bytes"),
        "ox_version": meta.get("ox_version"),
        "timestamp": meta.get("timestamp"),
        "manifest": (meta.get("manifest") or {}).get("path"),
        "prompt": None, "completion": None, "reasoning": None,
        "cached": None, "cost": None, "usd": None, "priced_from": None,
    }
    if not response_path.exists():
        # Two very different things look identical here: a run that failed
        # before a reply, and a --dry-run that never sent one. status.json
        # tells them apart, and calling a dry run a failure would put a
        # phantom outage in the availability record.
        status = {}
        status_path = run / "status.json"
        if status_path.exists():
            try:
                status = json.loads(status_path.read_text(encoding="utf-8"))
            except ValueError:
                status = {}
        if status.get("dry_run"):
            out["error"] = "dry run -- the payload was built, nothing was sent"
        else:
            out["error"] = "no response.json -- the run did not complete"
        out["dry_run"] = bool(status.get("dry_run"))
        return out
    usage = json.loads(response_path.read_text(encoding="utf-8")).get("usage") or {}
    out["prompt"] = usage.get("prompt_tokens")
    out["completion"] = usage.get("completion_tokens")
    out["reasoning"] = (usage.get("completion_tokens_details") or {}).get("reasoning_tokens")
    out["cached"] = (usage.get("prompt_tokens_details") or {}).get("cached_tokens")
    out["cost"] = usage.get("cost")
    return out


def iter_turns(path):
    """Deduplicated assistant turns from one transcript.

    Yields one record per API response. See the module docstring: the same
    response is written once per content block, each copy carrying the full
    usage, so anything that does not dedupe is measuring content blocks.
    """
    seen = set()
    with Path(path).open(encoding="utf-8") as handle:
        for line in handle:
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            if rec.get("type") != "assistant":
                continue
            message = rec.get("message") or {}
            usage = message.get("usage")
            if not usage:
                continue
            key = message.get("id") or rec.get("requestId") or rec.get("uuid")
            if key in seen:
                continue
            seen.add(key)
            yield {
                "ts": (rec.get("timestamp") or "")[:19],
                "model": message.get("model") or "unknown",
                "sidechain": bool(rec.get("isSidechain")),
                "input": usage.get("input_tokens") or 0,
                "output": usage.get("output_tokens") or 0,
                "cache_read": usage.get("cache_read_input_tokens") or 0,
                "cache_write": usage.get("cache_creation_input_tokens") or 0,
                "thinking": (usage.get("output_tokens_details") or {}).get("thinking_tokens") or 0,
            }


def cost_state(path):
    """The harness's own session totals, if the transcript carries them."""
    with Path(path).open(encoding="utf-8") as handle:
        for line in handle:
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            if rec.get("type") == "cost-state":
                return rec
    return None


def find_transcripts(key):
    # The real keys start with a dash ("-Users-curtisg-src-oxbox"), which
    # argparse reads as another flag unless it is written --project=-Users-...
    # Accepting the key without its leading dash makes the plain form work too,
    # rather than leaving a documented invocation that cannot be typed.
    if not key.startswith("-"):
        key = "-" + key
    directory = TRANSCRIPT_ROOT / key
    if not directory.is_dir():
        die("no transcript directory for %s\n"
            "costcheck: looked in %s -- pass --session <path> if the harness "
            "has moved them" % (key, directory))
    found = sorted(directory.glob("*.jsonl"))
    if not found:
        die("no transcripts in %s" % directory)
    return found


def gather(paths, start, end):
    """Sum turns in [start, end] per model, split main thread vs subagent."""
    totals, span, dropped = {}, [], 0
    for path in paths:
        for turn in iter_turns(path):
            if (start and turn["ts"] < start) or (end and turn["ts"] > end):
                dropped += 1
                continue
            span.append(turn["ts"])
            lane = "subagent" if turn["sidechain"] else "main"
            row = totals.setdefault((turn["model"], lane),
                                    {"turns": 0, "input": 0, "output": 0,
                                     "cache_read": 0, "cache_write": 0, "thinking": 0})
            row["turns"] += 1
            for field in ("input", "output", "cache_read", "cache_write", "thinking"):
                row[field] += turn[field]
    return totals, (min(span), max(span)) if span else None, dropped


def commas(value):
    return "-" if value is None else "{:,}".format(value)


def dollars(run):
    if run.get("cost") == 0 or run.get("usd") == 0:
        return "free"
    if run.get("usd") is None:
        return "-"
    return "$%.4f" % run["usd"]


def render(runs, totals, span, window, state):
    lines = []
    under = {"prompt": 0, "completion": 0, "reasoning": 0}
    if runs:
        lines.append("### Under test")
        lines.append("")
        lines.append("| run | model | mode | context | prompt | completion | reasoning | usd |")
        lines.append("|---|---|---|---|---|---|---|---|")
        usd_total, priced_from = 0.0, set()
        for run in runs:
            for field in under:
                under[field] += run.get(field) or 0
            if run.get("usd") is not None:
                usd_total += run["usd"]
                priced_from.add(run["priced_from"])
            lines.append("| `%s` | `%s` | %s | %s B | %s | %s | %s | %s |" % (
                run.get("timestamp") or "?", run["model"], run["mode"],
                commas(run["context_bytes"]),
                commas(run["prompt"]), commas(run["completion"]), commas(run["reasoning"]),
                dollars(run)))
        if len(runs) > 1:
            lines.append("| **total** | | | | %s | %s | %s | %s |" % (
                commas(under["prompt"]), commas(under["completion"]),
                commas(under["reasoning"]),
                "$%.4f" % usd_total if priced_from else "-"))
        if priced_from:
            lines.append("")
            lines.append("usd is computed from the archived catalog price (%s), "
                         "not billed: OpenRouter returns the billed figure only when "
                         "asked, and ox does not ask. Reasoning tokens are inside "
                         "completion and priced as output." % ", ".join(sorted(priced_from)))
        for run in runs:
            if run.get("error"):
                lines.append("")
                lines.append("**%s: %s**" % (run.get("timestamp"), run["error"]))
        lines.append("")

    lines.append("### Harness")
    lines.append("")
    if not totals:
        lines.append("No assistant turns in the window.")
        return "\n".join(lines)
    lines.append("| model | lane | turns | input | output | thinking | cache read | cache write |")
    lines.append("|---|---|---|---|---|---|---|---|")
    grand = {"turns": 0, "input": 0, "output": 0, "cache_read": 0, "cache_write": 0, "thinking": 0}
    for (model, lane) in sorted(totals):
        row = totals[(model, lane)]
        for field in grand:
            grand[field] += row[field]
        lines.append("| `%s` | %s | %s | %s | %s | %s | %s | %s |" % (
            model, lane, commas(row["turns"]), commas(row["input"]), commas(row["output"]),
            commas(row["thinking"]), commas(row["cache_read"]), commas(row["cache_write"])))
    lines.append("| **total** | | %s | %s | %s | %s | %s | %s |" % (
        commas(grand["turns"]), commas(grand["input"]), commas(grand["output"]),
        commas(grand["thinking"]), commas(grand["cache_read"]), commas(grand["cache_write"])))
    lines.append("")

    if window[0] or window[1]:
        lines.append("Window: %s .. %s (given)." % (window[0] or "start", window[1] or "end"))
    else:
        lines.append("Window: the whole session, %s .. %s." % (span[0], span[1]))
    lines.append("Turns observed span %s .. %s." % (span[0], span[1]))
    lines.append("")
    lines.append("**Upper bound.** Anything else the session did in this window is "
                 "counted here too.")

    if under["completion"]:
        model_total = under["prompt"] + under["completion"]
        harness_total = grand["input"] + grand["output"]
        lines.append("")
        lines.append("Harness input+output is %.1fx the model's prompt+completion "
                     "(%s vs %s); with cache reads it is %.1fx (%s)." % (
                         harness_total / model_total, commas(harness_total),
                         commas(model_total),
                         (harness_total + grand["cache_read"]) / model_total,
                         commas(harness_total + grand["cache_read"])))

    if state:
        usd = state.get("totalCostUSD")
        lines.append("")
        lines.append("Session total from the harness's own record (whole session, "
                     "not this window): $%.2f across %s." % (
                         usd, ", ".join(sorted(state.get("modelUsage") or {}))))
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Token cost of a corpus run: the model's, and the harness's.")
    parser.add_argument("--run", action="append", default=[],
                        help="an ox log directory (holds meta.json); repeatable, "
                             "because one window usually covers several batches")
    parser.add_argument("--session", help="a transcript .jsonl, or a session uuid")
    parser.add_argument("--project", help="transcript directory name, with or "
                                          "without its leading dash, e.g. "
                                          "Users-curtisg-src-oxbox; the dashed "
                                          "form needs --project=-Users-...")
    parser.add_argument("--cwd", help="working directory whose transcripts to read; "
                                      "--project is derived from it")
    parser.add_argument("--from", dest="start", help="window start, UTC (2026-08-30T00:50Z)")
    parser.add_argument("--to", dest="end", help="window end, UTC")
    parser.add_argument("--catalog", help="an archived catalog to price the run's "
                                          "tokens from; default is the newest one "
                                          "under catalogs/<venue>/")
    args = parser.parse_args()

    if not args.run and not args.session and not args.project and not args.cwd:
        parser.error("give at least --run, --session, --project or --cwd")

    runs = [price_run(read_run(d), args.catalog) for d in args.run]
    start, end = parse_stamp(args.start), parse_stamp(args.end)

    paths, state = [], None
    if args.session:
        candidate = Path(args.session)
        if candidate.exists():
            paths = [candidate]
        else:
            matches = sorted(TRANSCRIPT_ROOT.glob("*/%s.jsonl" % args.session))
            if not matches:
                die("no transcript for session %s" % args.session)
            paths = matches[:1]
        state = cost_state(paths[0]) if not (start or end) else None
    else:
        key = args.project or project_key(args.cwd or ".")
        paths = find_transcripts(key)

    totals, span, _ = gather(paths, start, end)
    if not span:
        die("no assistant turns in %s%s" % (
            ", ".join(p.name for p in paths),
            " within the window" if (start or end) else ""))
    print(render(runs, totals, span, (start, end), state))
    return 0


if __name__ == "__main__":
    sys.exit(main())
