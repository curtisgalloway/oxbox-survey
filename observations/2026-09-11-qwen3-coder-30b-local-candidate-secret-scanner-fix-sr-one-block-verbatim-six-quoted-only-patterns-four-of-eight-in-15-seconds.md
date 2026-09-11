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
corpus: oxbox-secret-scanner-fix-sr
role: candidate
run: 2026-09-11T02-49-53Z
wall_s: 15
applies: true
hits: 4
hits_of: 8
self_hits: 0
usd_model: 0
usd_total: 0
---

# Qwen3-Coder 30B, local, on the secret-scanner fix (search/replace arm): one block, verbatim, six quoted-only patterns, four of eight, in 15 seconds

**What happened** — `oxbox-secret-scanner-fix-sr` (`ox` at `6072d56`,
39,467 B, `--mode ask` with the SEARCH/REPLACE delivery instruction, effort
medium, 16,000 tokens, temperature 1.0, the reasoning field dropped) put to
`qwen3-coder:30b` served by ollama 0.34.0 on argenta. Fifteen seconds, 653
completion tokens, exactly the contract: `ox`, one block, no prose. The
SEARCH is the entire `SECRET_PATTERNS` list, copied verbatim, and the
scorer applied it. The REPLACE keeps all eight entries and appends six new
patterns, one per sample in the task text, each naming the identifier
outright and each requiring a quoted value. Four of eight verdicts hold,
the same four as the diff arm; the patched list scans `ox` clean.

## Evidence

Log `logs/2026-09-11T02-49-53Z`, `context_bytes` 39467, `finish_reason`
stop. The scorer:

```
gate 1  APPLY   PASS  1 block(s), every SEARCH found once, verbatim
gate 2  SCAN    4 of 8 verdicts hold
        client_secret, DB_PASSWORD, token:, aws_secret_access_key    required hit   after miss
gate 3  SELF    PASS  zero hits over ox at the pin and as patched
scope   in contract: nothing outside SECRET_PATTERNS changed
RESULT  FAIL  (gate 2: 4 of 8 verdicts wrong)
```

## So what

The cleanest illustration of what the format buys and what it does not, on
one model in one minute: the diff arm's corrupt header is gone and the
block applied verbatim, and the four verdicts behind it are the same four
because the model read "unquoted" and wrote patterns that require quotes
both times. A delivery format fixes delivery. Three of the four local
models now have an applied search/replace block against a refused or
recounted diff; the fourth, Gemma, ran out of tokens reasoning about the
blocks.

## Cost

Nothing billed; mechanically scored, so `usd_total` equals `usd_model`.
