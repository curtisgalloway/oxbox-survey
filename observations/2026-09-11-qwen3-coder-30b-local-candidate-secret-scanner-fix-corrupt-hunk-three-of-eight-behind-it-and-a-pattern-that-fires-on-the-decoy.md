<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-11
venue: ollama
model: qwen3-coder:30b
kind: hygiene
source: oxbox-run
agent: claude-fable-5-1
corpus: oxbox-secret-scanner-fix
role: candidate
run: 2026-09-11T02-12-51Z
wall_s: 14
applies: false
hits: 3
hits_of: 8
self_hits: 0
usd_model: 0
usd_total: 0
---

# Qwen3-Coder 30B, local, as a candidate on the secret-scanner fix: corrupt hunk, three of eight behind it, and a pattern that fires on the decoy

**What happened** — `oxbox-secret-scanner-fix` (`ox` at `6072d56`, 39,467 B,
`--mode diff`, 100,000 tokens, temperature 0.2, the reasoning field dropped
as described in
`2026-09-11-qwen3-coder-30b-local-candidate-zero-defect-control-a-thousand-findings-from-five-templates-zero-real-in-25-minutes.md`)
put to `qwen3-coder:30b` served by ollama 0.34.0 on argenta. Fourteen
seconds, 568 completion tokens, a paragraph of plan and one fenced diff.
`git apply --check` refuses it (the hunk header counts 7 lines before and 13
after for a hunk that is not that shape); with `--recount` it applies, and
the content behind it is wrong on five of eight verdicts. The model kept the
original quoted pattern unchanged and added two: an unquoted-value pattern
on the same four names, which cannot reach `client_secret`, `my_api_key`,
`DB_PASSWORD` or `aws_secret_access_key` because `\b` does not fall between
an underscore and a letter, and a third pattern that matches
`max_tokens`/`completion_tokens` assignments by name, which is a scanner rule
that fires on the decoy it was told to leave alone.

## Evidence

Log `logs/2026-09-11T02-12-51Z`, `context_bytes` 39467, `finish_reason`
stop. The scorer:

```
gate 1  APPLY   FAIL  git apply --check
        (with --recount: applies -- gate 2 below is informational)
gate 2  SCAN    3 of 8 verdicts hold
        client_secret=…            required hit   after miss
        my_api_key = "…"           required hit   after miss
        DB_PASSWORD=…              required hit   after miss
        aws_secret_access_key=…    required hit   after miss
        completion_tokens = 512    required miss  after hit
gate 3  SELF    PASS  zero hits over ox at the pin and as patched
scope   in contract: nothing outside SECRET_PATTERNS changed
RESULT  FAIL  (gate 1: applies only with --recount; gate 2: 5 of 8 verdicts wrong)
```

The plan above the diff names the two decoy forms as things that "should
NOT match", and the diff then adds a pattern named "non-secret numeric
assignment" that matches them, in a list where every entry is a reason to
refuse a run.

## So what

Fourteen seconds against qwen3.8's 46 minutes on the same task, and the
fast answer fails every gate the slow one passed. The hunk-header fault is
the one six of seven hosted cheap models made on 2026-09-08 and the
prior-art review explains: unified diffs carry line counts a small model has
no way to get right. The search/replace arm added the same day is the test
of whether that alone was the difference; the pattern logic behind the
header was wrong here too, and no format fixes that.

## Cost

Nothing billed; mechanically scored, so `usd_total` equals `usd_model`.
