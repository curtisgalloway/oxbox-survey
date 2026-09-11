<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-11
venue: ollama
model: gemma4:26b
kind: hygiene
source: oxbox-run
agent: claude-fable-5-1
corpus: oxbox-secret-scanner-fix-v3
role: candidate
run: 2026-09-11T02-20-20Z
wall_s: 117
applies: false
hits: 8
hits_of: 8
self_hits: 2
usd_model: 0
usd_total: 0
---

# Gemma 4 26B, local, on the secret-scanner fix (unified-diff arm, v3): eight of eight behind a hunk header git refuses, and a pattern that refuses ox itself

**What happened** — `oxbox-secret-scanner-fix-v3` (`ox` at `6072d56`,
39,467 B, `--mode diff`, **effort medium, 16,000 tokens, temperature 1.0**)
put to `gemma4:26b` through its `gemma4:26b-64k` tag served by ollama
0.34.0 on argenta, through the local setup described in
`2026-09-10-qwen3.8-27b-local-candidate-zero-defect-control-nothing-in-900-seconds-on-argenta.md`.
One fenced diff and a numbered explanation in 117 seconds, 11,180
completion tokens, 29,087 characters of reasoning. Two of three gates fail.
`git apply --check` refuses the hunk header (`@@ -83,8 +83,8 @@` on a hunk
with six context lines and one line changed each way); with `--recount` it
applies, and behind it every one of the eight verdicts holds, the first
local pattern to do that on either arm at any parameters. Then gate 3: the
new pattern wraps the keyword in `[\w-]*…[\w-]*`, so `token` matches inside
`max_tokens`, and `ox` line 734, `max_tokens = DEFAULT_MAX_TOKENS`, is an
18-character unquoted value after it. The patched scanner refuses ox's own
source, which the task text says makes it refuse every run. The two decoy
rows passed only because their values are numbers shorter than 16
characters. The explanation says the clean cases are unaffected "because
they do not contain any of the specified keywords"; `max_tokens` contains
`token`.

The same model on the same task at the v1 parameters looped to the cap and
produced nothing in 24 minutes.

## Evidence

Log `logs/2026-09-11T02-20-20Z`, `context_bytes` 39467, `finish_reason`
stop. The scorer:

```
gate 1  APPLY   FAIL  git apply --check
        (with --recount: applies -- gate 2 below is informational)
gate 2  SCAN    8 of 8 verdicts hold
gate 3  SELF    FAIL  the patched scanner refuses ox's own source:
                      ox@6072d56:734: 'max_tokens = DEFAULT_MAX_TOKENS' (hardcoded credential assignment)
                      ox(patched):734: 'max_tokens = DEFAULT_MAX_TOKENS' (hardcoded credential assignment)
scope   in contract: nothing outside SECRET_PATTERNS changed
RESULT  FAIL  (gate 1: applies only with --recount; gate 3: 2 self-hit(s))
```

Gate 3 was added on 2026-09-02 for exactly this patch shape, after the
first candidate patch cleared all eight rows and still fired on that line.

## So what

At the vendor's sampling and a cap the task fits, the model that could not
finish this task produced the right eight verdicts in two minutes, and lost
on the two things the answer key was built to catch: the line counts a
unified diff makes a model guess, and the trap in the file the scanner
guards. The search/replace arm, run next on the same model, removes the
first of those from the question; nothing in the format removes the second.

## Cost

Nothing billed; mechanically scored, so `usd_total` equals `usd_model`.
