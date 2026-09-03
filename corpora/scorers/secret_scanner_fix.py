#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Curtis Galloway
# SPDX-License-Identifier: Apache-2.0
"""Score an ox run against corpora/answers/oxbox-secret-scanner-fix.md.

Both gates from the answer key, measured rather than read:

  1. the patch applies to `ox` at the pin, with `git apply --check`;
  2. SECRET_PATTERNS from the patched file gives the eight required verdicts;
  3. the patched pattern list scans `ox` itself -- at the pin, and as patched --
     with zero hits, as the pin's own list and the reference fix both do.

Gate 3 is the prompt's own requirement ("ox is routinely asked to read its own
source and a scanner that fires on them refuses every run") measured over the
whole file instead of through the two trap rows. Added 2026-09-02 before any
evidence was recorded, when the first candidate patch cleared all eight rows
and still fired on `max_tokens = DEFAULT_MAX_TOKENS`.

Plus the contract check the key calls out: the prompt says to change the
pattern list only, so anything else that differs between the pin and the
patched file is reported as out of contract. It does not fail the gates --
the key says it is out of contract, not that it is wrong -- but it is
printed, because a reviewer should not have to diff for it.

    corpora/scorers/secret_scanner_fix.py --run ../oxbox/logs/<stamp> \
        --repo ../oxbox

Nothing here reads the diff for meaning. That is the point of a mechanical
fixture: two models get the same table, and the table does not care whose
patch it is.
"""

import argparse
import ast
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TASK_ID = "oxbox-secret-scanner-fix"
TARGET = "ox"

# The eight samples from the answer key, with the verdict each must give
# after the patch. The first six are the misses the task exists to close plus
# the one form that already worked; the last two are the trap -- ox reads its
# own source, and a pattern that fires on these makes it refuse every run.
SAMPLES = [
    ('api_key = "abcdefghijklmnop"', True),
    ("client_secret=abcdefghijklmnopqrst", True),
    ('my_api_key = "abcdefghijklmnopqrst"', True),
    ("DB_PASSWORD=hunter2hunter2hunter2", True),
    ("token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9", True),
    ("aws_secret_access_key=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY", True),
    ('"max_tokens": 100000', False),
    ("completion_tokens = 512", False),
]


def die(message):
    sys.exit("scorer: " + message)


def pin_for(task_id):
    manifest = json.loads((HERE.parent / "corpus-manifest.json").read_text(encoding="utf-8"))
    for project in manifest["projects"]:
        for task in project["tasks"]:
            if task["id"] == task_id:
                return task.get("commit") or project["commit"], task["files"]
    die("no task %s in the corpus manifest" % task_id)


def extract_diff(content):
    """The single fenced diff block the output contract asks for."""
    blocks = re.findall(r"```diff[^\n]*\n(.*?)```", content, re.DOTALL)
    if not blocks:
        # Some models fence with no tag, or with `patch`. Accept a block that
        # starts like a unified diff, and say so.
        blocks = [b for b in re.findall(r"```[^\n]*\n(.*?)```", content, re.DOTALL)
                  if b.lstrip().startswith(("--- ", "diff --git"))]
        if blocks:
            print("note: the diff block was not tagged `diff` (contract miss, still scored)")
    if not blocks:
        return None, "no fenced diff block in content.md"
    if len(blocks) > 1:
        print("note: %d fenced diff blocks; the contract asks for one. Scoring the "
              "first." % len(blocks))
    body = blocks[0]
    if not body.endswith("\n"):
        body += "\n"
    return body, None


def patterns_from(source, label):
    tree = ast.parse(source, filename=label)
    for node in tree.body:
        if (isinstance(node, ast.Assign) and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id == "SECRET_PATTERNS"):
            try:
                value = ast.literal_eval(node.value)
            except ValueError:
                die("%s: SECRET_PATTERNS is not a literal list; cannot score it "
                    "without executing the file" % label)
            return value, (node.lineno, node.end_lineno)
    die("%s: no SECRET_PATTERNS assignment" % label)


def without(source, span):
    lines = source.splitlines(keepends=True)
    return "".join(lines[:span[0] - 1] + lines[span[1]:])


def verdicts(patterns):
    out = []
    for sample, _ in SAMPLES:
        hit = any(re.search(p, sample) for p, _ in patterns)
        out.append(hit)
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--run", required=True, help="an ox log directory")
    parser.add_argument("--repo", default=str(HERE.parent.parent.parent / "oxbox"),
                        help="an oxbox checkout to `git show` the pin from")
    args = parser.parse_args()

    run = Path(args.run)
    meta = json.loads((run / "meta.json").read_text(encoding="utf-8"))
    pin, files = pin_for(TASK_ID)
    if meta.get("files") != files:
        die("run files %r are not the fixture's %r" % (meta.get("files"), files))
    if meta.get("mode") != "diff":
        die("run mode is %r, fixture is diff" % meta.get("mode"))

    content_path = run / "content.md"
    if not content_path.exists():
        die("no content.md in %s -- the run did not complete" % run)
    diff, error = extract_diff(content_path.read_text(encoding="utf-8"))

    original = subprocess.run(["git", "-C", args.repo, "show", "%s:%s" % (pin, TARGET)],
                              capture_output=True, text=True, check=True).stdout
    before_patterns, before_span = patterns_from(original, "%s@%s" % (TARGET, pin[:7]))
    before = verdicts(before_patterns)

    print("run:    %s  (%s / %s)" % (run.name, meta.get("venue"), meta.get("model")))
    print("pin:    %s:%s" % (pin[:7], TARGET))
    print()

    if error:
        print("gate 1  APPLY   FAIL  %s" % error)
        print()
        print("RESULT  FAIL  (no patch to score)")
        return 1

    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        (work / TARGET).write_text(original, encoding="utf-8")
        patch = work / "candidate.patch"
        patch.write_text(diff, encoding="utf-8")
        check = subprocess.run(["git", "apply", "--check", str(patch)], cwd=tmp,
                               capture_output=True, text=True)
        if check.returncode != 0:
            print("gate 1  APPLY   FAIL  git apply --check:")
            for line in check.stderr.strip().splitlines():
                print("                      " + line)
            # The key scores --recount as a hygiene miss, not a pass; try it so
            # the reader knows whether the content was right and the headers wrong.
            recount = subprocess.run(["git", "apply", "--check", "--recount", str(patch)],
                                     cwd=tmp, capture_output=True, text=True)
            if recount.returncode != 0:
                print("        (with --recount: still fails)")
                print()
                print("RESULT  FAIL  (gate 1)")
                return 1
            # The content may still be right and only the hunk header wrong.
            # Gate 1 has failed either way; gate 2 is run on the recounted
            # patch so the observation can say which kind of failure this was.
            print("        (with --recount: applies -- gate 2 below is informational)")
            gate1 = False
            subprocess.run(["git", "apply", "--recount", str(patch)], cwd=tmp,
                           check=True, capture_output=True)
        else:
            print("gate 1  APPLY   PASS  git apply --check clean")
            gate1 = True
            subprocess.run(["git", "apply", str(patch)], cwd=tmp, check=True,
                           capture_output=True)
        patched = (work / TARGET).read_text(encoding="utf-8")

    after_patterns, after_span = patterns_from(patched, "%s(patched)" % TARGET)
    after = verdicts(after_patterns)

    print()
    print("gate 2  SCAN")
    print("        %-62s %-6s %-9s %-6s" % ("sample", "before", "required", "after"))
    failures = 0
    for (sample, required), b, a in zip(SAMPLES, before, after):
        ok = a == required
        failures += not ok
        print("        %-62s %-6s %-9s %-6s %s" % (
            sample, "hit" if b else "miss", "hit" if required else "miss",
            "hit" if a else "miss", "" if ok else "<-- WRONG"))
    print("        %d of %d verdicts hold" % (len(SAMPLES) - failures, len(SAMPLES)))

    # Gate 3: the tool must still be able to read its own source.
    print()
    self_hits = []
    for label, text in (("ox@%s" % pin[:7], original), ("ox(patched)", patched)):
        for pattern, description in after_patterns:
            for match in re.finditer(pattern, text):
                self_hits.append("%s:%d: %r (%s)" % (
                    label, text.count("\n", 0, match.start()) + 1,
                    match.group(0)[:60], description))
    if self_hits:
        print("gate 3  SELF    FAIL  the patched scanner refuses ox's own source:")
        for hit in self_hits[:8]:
            print("                      " + hit)
    else:
        print("gate 3  SELF    PASS  zero hits over ox at the pin and as patched")

    # Contract: pattern list only. Compare everything except the assignment.
    rest_before = without(original, before_span)
    rest_after = without(patched, after_span)
    print()
    if rest_before == rest_after:
        print("scope   in contract: nothing outside SECRET_PATTERNS changed")
    else:
        import difflib
        changed = [l for l in difflib.unified_diff(
            rest_before.splitlines(), rest_after.splitlines(), lineterm="", n=0)
            if l.startswith(("+", "-")) and not l.startswith(("+++", "---"))]
        print("scope   OUT OF CONTRACT: %d line(s) changed outside SECRET_PATTERNS"
              % len(changed))
        for line in changed[:12]:
            print("        " + line)
    print()
    print("patterns: %d before, %d after" % (len(before_patterns), len(after_patterns)))
    print()
    failed = []
    if not gate1:
        failed.append("gate 1: applies only with --recount")
    if failures:
        failed.append("gate 2: %d of %d verdicts wrong" % (failures, len(SAMPLES)))
    if self_hits:
        failed.append("gate 3: %d self-hit(s)" % len(self_hits))
    print("RESULT  %s" % ("PASS" if not failed else "FAIL  (%s)" % "; ".join(failed)))
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
