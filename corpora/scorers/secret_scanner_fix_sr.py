#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Curtis Galloway
# SPDX-License-Identifier: Apache-2.0
"""Score the search/replace arm of the scanner fix (oxbox-secret-scanner-fix-sr).

The same answer key and the same eight verdicts as secret_scanner_fix.py; only
the delivery differs. The model hands back SEARCH/REPLACE blocks instead of a
unified diff, the format Diff-XYZ (arXiv:2510.12487) measured at several times
the exact-match rate of a diff on small open-weight models, and that Aider and
OpenAI's apply_patch use because it carries no line numbers or hunk counts to
get wrong. Gate 1 here is that every block's SEARCH text occurs exactly once in
`ox` at the pin, character for character. A block that matches only after
trailing whitespace is stripped from every line is applied and reported, the
way secret_scanner_fix.py reports `--recount`: gate 1 fails, gates 2 and 3 are
still run so the observation can say whether the content was right.

    corpora/scorers/secret_scanner_fix_sr.py --run ../oxbox/logs/<stamp> \\
        --repo ../oxbox

Gates 2 and 3 and the scope check are imported from secret_scanner_fix.py so
the two arms cannot drift apart in what they measure.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import secret_scanner_fix as udiff  # noqa: E402  (the sibling scorer)

TASK_ID = "oxbox-secret-scanner-fix-sr"
TARGET = "ox"

BLOCK = re.compile(
    r"(?:^(?P<path>[^\n<>=]+)\n)?"
    r"^<{7} SEARCH\n(?P<search>.*?)\n?^={7}\n(?P<replace>.*?)\n?^>{7} REPLACE[ \t]*$",
    re.DOTALL | re.MULTILINE)


def extract_blocks(content):
    """Every SEARCH/REPLACE block in the answer, in order.

    Fences are tolerated and noted: the contract says no fences, and a model
    that wraps the blocks anyway has still delivered them.
    """
    if re.search(r"^```", content, re.MULTILINE):
        print("note: the answer carries code fences (contract miss, still scored)")
        content = re.sub(r"^```[^\n]*\n?", "", content, flags=re.MULTILINE)
    blocks = []
    for match in BLOCK.finditer(content):
        path = (match.group("path") or "").strip()
        if path and path != TARGET:
            print("note: block names %r, the fixture's file is %r" % (path, TARGET))
        blocks.append((match.group("search"), match.group("replace")))
    if not blocks:
        return None, "no SEARCH/REPLACE block in content.md"
    return blocks, None


def _strip_lines(text):
    return "\n".join(line.rstrip() for line in text.split("\n"))


def apply_blocks(original, blocks):
    """Apply each block in turn. Returns (text, exact, notes).

    exact is False when any block needed the lenient match or did not apply;
    a block that does not apply even leniently leaves the text unchanged and
    is reported, and the caller decides whether anything is left to score.
    """
    text = original
    exact = True
    notes = []
    for index, (search, replace) in enumerate(blocks, 1):
        if not search:
            exact = False
            notes.append("block %d: empty SEARCH" % index)
            continue
        count = text.count(search)
        if count == 1:
            text = text.replace(search, replace, 1)
            continue
        if count > 1:
            exact = False
            notes.append("block %d: SEARCH occurs %d times, applied to the first" % (index, count))
            text = text.replace(search, replace, 1)
            continue
        # Lenient: trailing whitespace only. Anything looser is a different edit.
        loose_text, loose_search = _strip_lines(text), _strip_lines(search)
        loose_count = loose_text.count(loose_search)
        if loose_count >= 1:
            exact = False
            notes.append("block %d: SEARCH matches only with trailing whitespace stripped"
                         "%s" % (index, "" if loose_count == 1 else " (%d times, first applied)" % loose_count))
            start = loose_text.index(loose_search)
            # Map the loose offset back onto the real text line by line.
            line_no = loose_text.count("\n", 0, start)
            lines = text.split("\n")
            n = loose_search.count("\n") + 1
            lines[line_no:line_no + n] = replace.split("\n")
            text = "\n".join(lines)
            continue
        exact = False
        notes.append("block %d: SEARCH not found at the pin" % index)
    return text, exact, notes


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--run", required=True, help="an oxbox log directory")
    parser.add_argument("--repo", default=str(HERE.parent.parent.parent / "oxbox"),
                        help="an oxbox checkout to `git show` the pin from")
    args = parser.parse_args()

    run = Path(args.run)
    meta = json.loads((run / "meta.json").read_text(encoding="utf-8"))
    pin, files = udiff.pin_for(TASK_ID)
    if meta.get("files") != files:
        udiff.die("run files %r are not the fixture's %r" % (meta.get("files"), files))
    if meta.get("mode") != "ask":
        udiff.die("run mode is %r, fixture is ask (the blocks are the answer)" % meta.get("mode"))

    content_path = run / "content.md"
    if not content_path.exists():
        udiff.die("no content.md in %s -- the run did not complete" % run)
    blocks, error = extract_blocks(content_path.read_text(encoding="utf-8"))

    original = subprocess.run(["git", "-C", args.repo, "show", "%s:%s" % (pin, TARGET)],
                              capture_output=True, text=True, check=True).stdout
    before_patterns, before_span = udiff.patterns_from(original, "%s@%s" % (TARGET, pin[:7]))
    before = udiff.verdicts(before_patterns)

    print("run:    %s  (%s / %s)" % (run.name, meta.get("venue"), meta.get("model")))
    print("pin:    %s:%s  (search/replace arm)" % (pin[:7], TARGET))
    print()

    if error:
        print("gate 1  APPLY   FAIL  %s" % error)
        print()
        print("RESULT  FAIL  (no blocks to score)")
        return 1

    patched, gate1, notes = apply_blocks(original, blocks)
    if gate1:
        print("gate 1  APPLY   PASS  %d block(s), every SEARCH found once, verbatim" % len(blocks))
    else:
        print("gate 1  APPLY   FAIL  %d block(s):" % len(blocks))
        for note in notes:
            print("                      " + note)
        if patched == original:
            print()
            print("RESULT  FAIL  (gate 1: nothing applied)")
            return 1
        print("        (some blocks applied -- gate 2 below is informational)")

    after_patterns, after_span = udiff.patterns_from(patched, "%s(patched)" % TARGET)
    after = udiff.verdicts(after_patterns)

    print()
    print("gate 2  SCAN")
    print("        %-62s %-6s %-9s %-6s" % ("sample", "before", "required", "after"))
    failures = 0
    for (sample, required), b, a in zip(udiff.SAMPLES, before, after):
        ok = a == required
        failures += not ok
        print("        %-62s %-6s %-9s %-6s %s" % (
            sample, "hit" if b else "miss", "hit" if required else "miss",
            "hit" if a else "miss", "" if ok else "<-- WRONG"))
    print("        %d of %d verdicts hold" % (len(udiff.SAMPLES) - failures, len(udiff.SAMPLES)))

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

    rest_before = udiff.without(original, before_span)
    rest_after = udiff.without(patched, after_span)
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
        failed.append("gate 1: blocks did not all apply verbatim")
    if failures:
        failed.append("gate 2: %d of %d verdicts wrong" % (failures, len(udiff.SAMPLES)))
    if self_hits:
        failed.append("gate 3: %d self-hit(s)" % len(self_hits))
    print("RESULT  %s" % ("PASS" if not failed else "FAIL  (%s)" % "; ".join(failed)))
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
