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
corpus: oxbox-secret-scanner-fix-v3
role: candidate
run: 2026-09-11T02-49-39Z
wall_s: 14
applies: false
hits: 4
hits_of: 8
self_hits: 0
usd_model: 0
usd_total: 0
---

# Qwen3-Coder 30B, local, on the secret-scanner fix (unified-diff arm, v3): corrupt patch, four of eight behind it, in 14 seconds

**What happened** — `oxbox-secret-scanner-fix-v3` (`ox` at `6072d56`,
39,467 B, `--mode diff`, effort medium, 16,000 tokens, temperature 1.0, the
reasoning field dropped) put to `qwen3-coder:30b` served by ollama 0.34.0
on argenta. Fourteen seconds, 533 completion tokens. `git apply` reports
"corrupt patch at line 20"; with `--recount` it applies. The content keeps
the original quoted-only pattern and adds two more, both quoted-only: one
naming the four missed identifiers outright, one for `token:` with a
36-character quoted value. Every missed sample in the task is unquoted, so
four of eight verdicts hold: the one form that already worked, the quoted
`my_api_key`, and the two decoys. The v1 run of this model on the task was
the same shape in the same 14 seconds, with three of eight.

## Evidence

Log `logs/2026-09-11T02-49-39Z`, `context_bytes` 39467, `finish_reason`
stop. The scorer:

```
gate 1  APPLY   FAIL  git apply --check: error: corrupt patch at line 20
        (with --recount: applies -- gate 2 below is informational)
gate 2  SCAN    4 of 8 verdicts hold
        client_secret, DB_PASSWORD, token:, aws_secret_access_key    required hit   after miss
gate 3  SELF    PASS  zero hits over ox at the pin and as patched
scope   in contract: nothing outside SECRET_PATTERNS changed
RESULT  FAIL  (gate 1: applies only with --recount; gate 2: 4 of 8 verdicts wrong)
```

The plan above the diff says the changes "involve adding new regex
patterns to match unquoted assignment forms", and every pattern it added
requires quotes.

## So what

The parameters changed nothing here: same seconds, same corrupt header,
same quoted-only misreading of a task whose whole point is unquoted values.
This is the non-thinking model's floor on the task, and the search/replace
arm run fifteen seconds later shows what the format fixes and what it does
not.

## Cost

Nothing billed; mechanically scored, so `usd_total` equals `usd_model`.
