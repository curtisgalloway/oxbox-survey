#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Curtis Galloway
# SPDX-License-Identifier: Apache-2.0
"""Score an ask-grounding run by executing the pinned `ox`, not by reading it.

The answer key (corpora/answers/oxbox-ask-grounding.md) states what the
source settles. Five of its seven settled questions can be *run* against the
pinned `ox` script with `--dry-run`, so this scorer runs them and reports the
observed fact beside the key's claim; if they ever disagree, the key is wrong
and the scorer says so. Two settled questions (2 and 7) need an HTTP server
that ox will actually talk to, and ox refuses any destination but its own
table, so they stay with a reader. Questions 8 to 10 are unsettled by design
and are scored on whether the answer says so.

Then it scores the model's answers mechanically where a pattern is enough
(the variable name, the mode, the byte limit, the URL, the exit message, and
"not settled" on 8 to 10), and marks the rest "reader" for a checker.
Decided 2026-09-06 at the editor's direction: reproduce first, read as the
fallback.

    corpora/scorers/ask_grounding.py --run ../oxbox/logs/<stamp> \
        --repo ../oxbox

Exit 0 when every executable fact matches the key and no mechanically scored
answer is wrong; 1 otherwise. "reader" rows never fail the run.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PIN = "6072d56830dd3f80d567bf8c71593bcab95fbc74"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def pinned_ox(repo, workdir):
    """Extract `ox` at the pin into workdir and return its path."""
    source = subprocess.run(["git", "-C", str(repo), "show", "%s:ox" % PIN],
                            capture_output=True, text=True, check=True).stdout
    path = workdir / "ox"
    path.write_text(source, encoding="utf-8")
    return path


def run_ox(ox, args, env=None, stdin="", cwd=None):
    """Run the pinned ox with a clean environment; return (code, stdout, stderr)."""
    base = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(cwd or Path.cwd()),
            "LANG": "C.UTF-8"}
    if env:
        base.update(env)
    proc = subprocess.run([sys.executable, str(ox)] + args, input=stdin, capture_output=True,
                          text=True, env=base, cwd=str(cwd) if cwd else None)
    return proc.returncode, proc.stdout, proc.stderr


def execute_facts(ox, workdir):
    """Run the five executable questions. Returns {q: (observed, key_claim, agree)}."""
    facts = {}
    small = workdir / "small.txt"
    small.write_text("hello\n", encoding="utf-8")
    dry = ["--dry-run", "--venue", "openrouter", "--files", str(small), "task"]

    # q1: which variable holds the requesty credential? Drive a dry run at
    # requesty with no key in the environment; the manifest path names the
    # variable when it skips an entry, so use a one-entry manifest.
    manifest = workdir / "m-requesty.json"
    manifest.write_text(json.dumps({"manifest_version": 0, "recommendations": [
        {"rank": 1, "venue": "requesty", "model": "x/y", "cost": "free"}]}), encoding="utf-8")
    code, out, err = run_ox(ox, ["--dry-run", "--manifest", str(manifest), "--files", str(small), "task"],
                            env={"OPENROUTER_API_KEY": "k"}, cwd=workdir)
    observed = "REQUESTY_API_KEY" if "REQUESTY_API_KEY" in (out + err) else "not named"
    facts[1] = (observed, "REQUESTY_API_KEY", observed == "REQUESTY_API_KEY")

    # q3: default --mode. The dry-run payload carries the system prompt of the
    # mode; the status line ox prints names the mode outright.
    code, out, err = run_ox(ox, dry, env={"OPENROUTER_API_KEY": "k"}, cwd=workdir)
    m = re.search(r"mode=(\w+)", err)
    observed = m.group(1) if m else "not printed"
    facts[3] = (observed, "diff", observed == "diff")

    # q4: manifest_version 1.
    manifest = workdir / "m-v1.json"
    manifest.write_text(json.dumps({"manifest_version": 1, "recommendations": []}), encoding="utf-8")
    code, out, err = run_ox(ox, ["--dry-run", "--manifest", str(manifest), "--files", str(small), "task"],
                            env={"OPENROUTER_API_KEY": "k"}, cwd=workdir)
    observed = "exits %d: %s" % (code, err.strip().splitlines()[-1] if err.strip() else "")
    facts[4] = (observed, "exits with 'newer than this ox understands (0)'",
                code != 0 and "newer than this ox understands (0)" in err)

    # q5: base_url disagreeing with the table.
    manifest = workdir / "m-base.json"
    manifest.write_text(json.dumps({"manifest_version": 0, "recommendations": [
        {"rank": 1, "venue": "openrouter", "model": "x/y", "cost": "free",
         "base_url": "https://example.invalid/v1"}]}), encoding="utf-8")
    code, out, err = run_ox(ox, ["--dry-run", "--manifest", str(manifest), "--files", str(small), "task"],
                            env={"OPENROUTER_API_KEY": "k"}, cwd=workdir)
    warned = "the table wins" in err
    facts[5] = ("warning printed: %s; dry run %s" % (warned, "ok" if code == 0 else "exit %d" % code),
                "table URL with a WARNING; base_url never a destination", warned and code == 0)

    # q6: the payload limit, at the boundary.
    over = workdir / "over.txt"
    over.write_text("a" * 400_001, encoding="utf-8")
    at = workdir / "at.txt"
    at.write_text("a" * 400_000, encoding="utf-8")
    code_over, _, err_over = run_ox(ox, ["--dry-run", "--venue", "openrouter", "--files", str(over), "task"],
                                    env={"OPENROUTER_API_KEY": "k"}, cwd=workdir)
    code_at, _, _ = run_ox(ox, ["--dry-run", "--venue", "openrouter", "--files", str(at), "task"],
                           env={"OPENROUTER_API_KEY": "k"}, cwd=workdir)
    code_force, _, _ = run_ox(ox, ["--dry-run", "--force", "--venue", "openrouter", "--files", str(over), "task"],
                              env={"OPENROUTER_API_KEY": "k"}, cwd=workdir)
    observed = "400,000 sent (exit %d); 400,001 refused (exit %d, %s); --force sends (exit %d)" % (
        code_at, code_over, "limit named" if "400000" in err_over else "limit not named", code_force)
    facts[6] = (observed, "400,000 bytes; over it refused without --force",
                code_at == 0 and code_over != 0 and code_force == 0)
    return facts


ANSWER_PATTERNS = {
    1: (r"REQUESTY_API_KEY", None),
    3: (r"\bdiff\b", None),
    4: (r"newer than|exit|error|refus", None),
    5: (r"openrouter\.ai/api/v1/chat/completions", None),
    6: (r"400[,_ ]?000|400 ?K\b", None),
    8: (r"not (settle|specif|state|address|implement)|no retry|does not retry|no (wait|backoff)|never retr", r"\b\d+ ?(second|minute|s\b|times|attempt)"),
    9: (r"not (settle|specif|state|address)|does not (say|state|estimate)|cannot be determined|no (way|information)", r"\b900\b(?!.*(not|own|client|timeout))"),
    10: (r"not (settle|specif|state|address)|does not (say|state|specify|settle)|cannot be determined|no (statement|information)", r"\b(does|will) (retain|train)\b"),
}


def split_answers(text):
    """Model answers keyed by question number, from a numbered list."""
    answers = {}
    for m in re.finditer(r"(?m)^\s*\**(\d{1,2})[.)]\**\s*(.*?)(?=^\s*\**\d{1,2}[.)]|\Z)", text, re.S):
        q = int(m.group(1))
        if 1 <= q <= 10 and q not in answers:
            answers[q] = m.group(2).strip()
    return answers


def score_answers(answers):
    rows = {}
    for q in range(1, 11):
        text = answers.get(q, "")
        if not text:
            rows[q] = ("missing", "")
            continue
        if q in (2, 7):
            rows[q] = ("reader", "needs an HTTP exchange ox will not fake")
            continue
        want, forbid = ANSWER_PATTERNS[q]
        hit = re.search(want, text, re.I) is not None
        bad = re.search(forbid, text, re.I) is not None if forbid else False
        if q in (8, 9, 10):
            rows[q] = ("correct" if hit and not bad else ("fabricated" if bad else "reader"),
                       "says unsettled" if hit else "no unsettled statement found")
        else:
            rows[q] = ("correct" if hit else "reader", "pattern %s" % ("matched" if hit else "not matched"))
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--run", required=True, help="an ox log directory with content.md")
    parser.add_argument("--repo", default=str(HERE.parent.parent.parent / "oxbox"),
                        help="an oxbox checkout holding the pin (default: ../oxbox)")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args()
    run = Path(args.run)
    text = (run / "content.md").read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory() as tmp:
        workdir = Path(tmp)
        ox = pinned_ox(Path(args.repo), workdir)
        facts = execute_facts(ox, workdir)
    answers = split_answers(text)
    scores = score_answers(answers)
    failed = False
    if args.json:
        print(json.dumps({"facts": {q: {"observed": o, "key": k, "agree": a} for q, (o, k, a) in facts.items()},
                          "scores": {q: {"score": s, "note": n} for q, (s, n) in scores.items()}}, indent=1))
    else:
        print("run:    %s" % run.name)
        print("pin:    %s:ox, executed with --dry-run" % PIN[:7])
        print("\nfacts (observed by running ox, against the key):")
        for q, (observed, key, agree) in sorted(facts.items()):
            print("  q%-2d %-5s observed: %s" % (q, "OK" if agree else "DRIFT", observed))
            if not agree:
                print("        key says: %s" % key)
                failed = True
        print("\nanswers:")
        for q, (score, note) in sorted(scores.items()):
            print("  q%-2d %-10s %s" % (q, score, note))
            if score in ("fabricated", "wrong", "missing"):
                failed = True
        mech = sum(1 for s, _ in scores.values() if s == "correct")
        readers = sum(1 for s, _ in scores.values() if s == "reader")
        print("\nRESULT  %s  (%d scored mechanically correct, %d for a reader)"
              % ("FAIL" if failed else "PASS", mech, readers))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
