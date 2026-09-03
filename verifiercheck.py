#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Curtis Galloway
# SPDX-License-Identifier: Apache-2.0
"""Score the reviewing agent, the way the corpus scores the reviewed model.

    ./verifiercheck.py build --pin <dir>
    ./verifiercheck.py run --arm opus --all
    ./verifiercheck.py run --arm gemini --all
    ./verifiercheck.py score

costcheck.py established that verification is the expensive half of a run. This
asks the question that follows: does it have to be, and how would we know if a
cheaper verifier were good enough. It replays findings the survey has already
recorded verdicts for, puts them to two reviewing agents under the same
contract, and scores both against the record.

**An arm is a model AND a harness, and the pair is what gets measured.** The two
arms are separate CLIs, so a verdict gap is not attributable to the model alone.
What narrows it here is that neither arm gets tools: the pinned source is inlined
into the prompt and both run in an empty working directory, so the payload is
byte-identical and is the whole world. That is corpus-manifest.json's rule for
candidates applied one layer up, and it costs something real -- the evidence set
is fixed in advance instead of chosen by the verifier, which is not how the
standing supervisor works in production. Say which arm, not which model, in
anything written from this.

**The pin must be a history-free export, not a git worktree.** A worktree shares
.git with the parent, and in the oxbox case the very next commit after the pin
(0090c35) names both real defects in its subject line. Build the tree with
`git archive <pin> | tar -x -C <dir>`; `build` refuses a directory with a .git
in it.

**The key is not independent of the Claude arm.** The recorded verdicts were
reached by Claude agents. Agreement with them is therefore worth less on the
Claude side than on the other, and the number that carries real information is
the disagreement list -- the rows where the two arms differ, which a human reads
and settles. `score` prints that list first for exactly that reason.
"""

import argparse
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KEY = os.path.join(HERE, "corpora", "answers", "oxbox-clean-control-verdicts.json")
PROMPT = os.path.join(HERE, "corpora", "prompts", "verify-findings.txt")

# The evidence a verifier is allowed to reach, inlined into every batch. This
# list is the experiment's main compromise and is stated rather than hidden: a
# verifier that roams chooses its own evidence, and two verifiers that roam
# differently produce a verdict gap nobody can attribute. Fixing the set makes
# the payload byte-identical across arms -- corpus-manifest.json's rule for
# candidates, applied one layer up -- at the price of pre-deciding what is worth
# reading. The set is every file the recorded verdicts actually cite.
EVIDENCE = ["jailtest.py", "oxbox", "profiles/jail.sb", "guardtest.py", ".gitignore"]

# An arm is a command template plus how that CLI wants its prompt.
#
# Neither arm gets tools. Both run with an empty working directory, so even a
# tool call that slipped through would find nothing: the payload is the whole
# world. This is what makes a verdict difference the model's rather than the
# harness's -- and it is also the only shape agy runs in headlessly, since it
# reaches for a shell command to read a file and headless mode auto-denies the
# "command" permission with no way to prompt.
#
# The prompt goes to claude on stdin and to agy attached to --print. That is not
# a preference: agy's flag parser takes the next argv element as --print's value,
# so a bare --print eats whatever flag follows it and drops the real prompt.
ARMS = {
    "opus": {
        "model": "claude-opus-5",
        "harness": "claude-code-cli",
        "prompt": "stdin",
        "cmd": [
            "claude", "-p", "--model", "opus",
            "--permission-mode", "manual",
            "--permission-prompts", "none",
        ],
    },
    "gemini": {
        "model": "gemini-3.8-flash-medium",
        "harness": "agy-cli",
        "prompt": "--print={prompt}",
        "cmd": [
            "agy", "--model", "gemini-3.8-flash-medium",
            "--effort", "medium",
            "--output-format", "text",
            "--disable-slash-commands",
            "--print-timeout", "10m",
        ],
    },
}


def load_key():
    with open(KEY, encoding="utf-8") as handle:
        return json.load(handle)


def slug(model):
    """Short local name for a batch. Never sent to a verifier."""
    return model.split("/")[-1]


def build_evidence(pin):
    """The pinned source, inlined once and shared by every batch."""
    parts = ["-----8<----- begin source at the pin -----8<-----", ""]
    for name in EVIDENCE:
        path = os.path.join(pin, name)
        with open(path, encoding="utf-8") as handle:
            body = handle.read()
        parts.append("===== %s (%d bytes) =====" % (name, len(body.encode("utf-8"))))
        parts.append(body.rstrip())
        parts.append("")
    parts.append("-----8<----- end source -----8<-----")
    return "\n".join(parts) + "\n"


def build_batch(batch, logs):
    """The bytes a verifier sees: an id index, then the findings verbatim.

    The index exists so two arms segment the batch identically. Models number
    their findings inconsistently -- eight numbered items from one, a single
    unnumbered `### Defect:` heading from another -- and a verifier left to
    segment for itself produces a verdict list that cannot be lined up with
    another verifier's. The labels are neutral restatements of each claim and
    carry no verdict; the verbatim text below them is the authority.
    """
    content_path = os.path.join(logs, batch["content"].split("logs/")[-1])
    with open(content_path, encoding="utf-8") as handle:
        content = handle.read()

    lines = [
        "# Findings batch",
        "",
        "%d finding(s) from a code review of jailtest.py, whose source is included"
        % len(batch["findings"]),
        "below along with the launcher, the sandbox profile and the companion test",
        "the findings refer to. Return exactly one verdict for each id below, in",
        "this order:",
        "",
    ]
    if batch["findings"]:
        for finding in batch["findings"]:
            lines.append("  %s  %s" % (finding["id"], finding["label"]))
    else:
        lines.append("  (none -- the review reported no defects)")
        lines.append("")
        lines.append('Return {"verdicts": []} and nothing else.')
    lines += [
        "",
        "The reviewer's own words follow, unedited. The index above exists only to",
        "fix the ids and their order; where it and the text below differ, the text",
        "below is what you are verifying.",
        "",
        "-----8<----- begin review -----8<-----",
        content.rstrip(),
        "-----8<----- end review -----8<-----",
    ]
    return "\n".join(lines) + "\n"


def cmd_build(args):
    if os.path.isdir(os.path.join(args.pin, ".git")):
        sys.stderr.write(
            "verifiercheck: %s has a .git -- a verifier can read the fix commit "
            "there. Use `git archive <pin> | tar -x -C <dir>` instead.\n" % args.pin
        )
        return 2
    key = load_key()
    os.makedirs(args.work, exist_ok=True)
    with open(PROMPT, encoding="utf-8") as handle:
        contract = handle.read()
    evidence = build_evidence(args.pin)
    for batch in key["batches"]:
        name = slug(batch["model"])
        text = contract + "\n\n" + evidence + "\n" + build_batch(batch, args.logs)
        out = os.path.join(args.work, "batch-%s.txt" % name)
        with open(out, "w", encoding="utf-8") as handle:
            handle.write(text)
        print("%-22s %2d finding(s)  %6d B  %s"
              % (name, len(batch["findings"]), len(text), out))
    print("\npin: %s" % args.pin)
    return 0


def extract_json(text):
    """Pull the verdict object out of a reply that may be wrapped in prose."""
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.S)
    if fence:
        text = fence.group(1)
    start = text.find("{")
    while start != -1:
        depth, in_str, esc = 0, False, False
        for i in range(start, len(text)):
            ch = text[i]
            if in_str:
                if esc:
                    esc = False
                elif ch == "\\":
                    esc = True
                elif ch == '"':
                    in_str = False
                continue
            if ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[start:i + 1])
                    except ValueError:
                        break
        start = text.find("{", start + 1)
    return None


def cmd_run(args):
    key = load_key()
    arm = ARMS[args.arm]
    names = [slug(b["model"]) for b in key["batches"]]
    todo = names if args.all else [args.batch]
    unknown = [n for n in todo if n not in names]
    if unknown:
        sys.stderr.write("verifiercheck: no such batch: %s\n" % ", ".join(unknown))
        return 2

    os.makedirs(args.work, exist_ok=True)
    # Both arms run here: an empty directory, so a tool call that slipped past
    # the flags would still find nothing to read. The payload is the whole world.
    empty = os.path.join(args.work, "empty-cwd")
    os.makedirs(empty, exist_ok=True)
    failures = 0
    for name in todo:
        batch_path = os.path.join(args.work, "batch-%s.txt" % name)
        if not os.path.exists(batch_path):
            sys.stderr.write("verifiercheck: %s missing; run `build` first\n"
                             % batch_path)
            return 2
        with open(batch_path, encoding="utf-8") as handle:
            prompt = handle.read()
        cmd = list(arm["cmd"])
        stdin = None
        if arm["prompt"] == "stdin":
            stdin = prompt
        else:
            cmd.append(arm["prompt"].format(prompt=prompt))
        sys.stderr.write("verifiercheck: arm=%s batch=%s bytes=%d\n"
                         % (args.arm, name, len(prompt)))
        try:
            proc = subprocess.run(
                cmd, input=stdin, cwd=empty, capture_output=True,
                text=True, timeout=args.timeout, check=False,
            )
        except subprocess.TimeoutExpired:
            sys.stderr.write("verifiercheck: arm=%s batch=%s TIMEOUT after %ds\n"
                             % (args.arm, name, args.timeout))
            failures += 1
            continue

        stem = os.path.join(args.work, "%s-%s" % (args.arm, name))
        with open(stem + ".raw.txt", "w", encoding="utf-8") as handle:
            handle.write(proc.stdout)
        if proc.returncode != 0:
            with open(stem + ".stderr.txt", "w", encoding="utf-8") as handle:
                handle.write(proc.stderr)
            sys.stderr.write("verifiercheck: arm=%s batch=%s exit=%d, stderr kept\n"
                             % (args.arm, name, proc.returncode))
            failures += 1
            continue
        parsed = extract_json(proc.stdout)
        if parsed is None:
            sys.stderr.write("verifiercheck: arm=%s batch=%s produced no JSON; "
                             "raw reply kept at %s.raw.txt\n" % (args.arm, name, stem))
            failures += 1
            continue
        with open(stem + ".json", "w", encoding="utf-8") as handle:
            json.dump(parsed, handle, indent=2)
        print("%-8s %-22s %d verdict(s)"
              % (args.arm, name, len(parsed.get("verdicts", []))))
    return 1 if failures else 0


def read_arm(work, arm, name):
    path = os.path.join(work, "%s-%s.json" % (arm, name))
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    return {v.get("id"): v for v in data.get("verdicts", [])}


def cmd_score(args):
    key = load_key()
    arms = args.arms.split(",")
    rows, missing, extra = [], [], []
    for batch in key["batches"]:
        name = slug(batch["model"])
        got = {arm: read_arm(args.work, arm, name) for arm in arms}
        for arm, verdicts in got.items():
            if verdicts is None:
                missing.append("%s/%s" % (arm, name))
                continue
            ids = {f["id"] for f in batch["findings"]}
            for vid in verdicts:
                if vid not in ids:
                    extra.append("%s/%s invented id %r" % (arm, name, vid))
        for finding in batch["findings"]:
            row = {"batch": name, "id": finding["id"],
                   "accept": finding["accept"], "recorded": finding["recorded"]}
            for arm in arms:
                verdicts = got.get(arm) or {}
                entry = verdicts.get(finding["id"])
                row[arm] = (entry or {}).get("verdict", "-")
                row[arm + ":why"] = (entry or {}).get("reason", "")
            rows.append(row)

    # A row missing an arm's verdict is absent data, not a disagreement; counting
    # it as one turns an unfinished run into a finding.
    scorable = [r for r in rows if all(r[a] != "-" for a in arms)]
    disputed = [r for r in scorable if len({r[a] for a in arms}) > 1]
    print("## Disagreements  (%d of %d findings both arms scored)\n"
          % (len(disputed), len(scorable)))
    if not disputed:
        print("None. The two arms returned the same verdict on every finding.\n")
    for row in disputed:
        marks = "  ".join("%s=%s" % (a, row[a]) for a in arms)
        agrees = [a for a in arms if row[a] in row["accept"]]
        print("%-16s %-4s %s   key=%s (%s)"
              % (row["batch"], row["id"], marks,
                 "|".join(row["accept"]), row["recorded"]))
        print("   key agrees with: %s" % (", ".join(agrees) if agrees else "neither"))
        for arm in arms:
            if row[arm + ":why"]:
                print("   %-8s %s" % (arm, row[arm + ":why"][:300]))
        print("")

    print("## Against the recorded key\n")
    head = "%-10s %5s %5s %5s %5s" % ("arm", "n", "ok", "miss", "false")
    print(head)
    print("-" * len(head))
    for arm in arms:
        scored = [r for r in rows if r[arm] != "-"]
        ok = [r for r in scored if r[arm] in r["accept"]]
        # A miss is a real defect called REFUTED; a false is an invention
        # called CONFIRMED. They are not the same mistake and a single
        # accuracy number hides which one an arm makes.
        miss = [r for r in scored
                if "CONFIRMED" in r["accept"] and r[arm] == "REFUTED"]
        false = [r for r in scored
                 if r["accept"] == ["REFUTED"] and r[arm] == "CONFIRMED"]
        print("%-10s %5d %5d %5d %5d"
              % (arm, len(scored), len(ok), len(miss), len(false)))
    print("\nmiss  = a defect the key calls real, refuted by the arm")
    print("false = an invention the key refutes, confirmed by the arm")
    if missing:
        print("\nNOT RUN: %s" % ", ".join(missing))
    if extra:
        print("\nINVENTED IDS: %s" % "; ".join(extra))
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    default_work = os.environ.get("VERIFIERCHECK_WORK", "verifier-runs")
    parser.add_argument("--work", default=default_work,
                        help="directory for batches and replies "
                             "(default: %(default)s)")
    parser.add_argument("--logs", default=os.path.join(HERE, "..", "oxbox", "logs"),
                        help="oxbox run logs (default: %(default)s)")
    subs = parser.add_subparsers(dest="command", required=True)

    build = subs.add_parser("build", help="write the blinded batches")
    build.add_argument("--pin", required=True,
                       help="history-free export of the pinned tree")
    build.set_defaults(func=cmd_build)

    run = subs.add_parser("run", help="put one or all batches to one arm")
    run.add_argument("--arm", required=True, choices=sorted(ARMS))
    run.add_argument("--batch")
    run.add_argument("--all", action="store_true")
    run.add_argument("--timeout", type=int, default=900)
    run.set_defaults(func=cmd_run)

    score = subs.add_parser("score", help="disagreements first, then the key")
    score.add_argument("--arms", default="opus,gemini")
    score.set_defaults(func=cmd_score)

    args = parser.parse_args()
    if args.command == "run" and not args.all and not args.batch:
        parser.error("run needs --batch <name> or --all")
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
