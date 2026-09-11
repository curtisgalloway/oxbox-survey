<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-11
venue: ollama
model: gpt-oss:20b
kind: hygiene
source: oxbox-run
agent: claude-fable-5-1
corpus: oxbox-secret-scanner-fix-sr
role: candidate
run: 2026-09-11T02-27-55Z
wall_s: 36
applies: true
hits: 7
hits_of: 8
self_hits: 0
usd_model: 0
usd_total: 0
---

# gpt-oss 20B, local, on the secret-scanner fix (search/replace arm): one block, applied verbatim, seven of eight behind it, in 36 seconds

**What happened** — `oxbox-secret-scanner-fix-sr` (`ox` at `6072d56`,
39,467 B, `--mode ask` with the SEARCH/REPLACE delivery instruction, effort
medium, 16,000 tokens, temperature 1.0) put to `gpt-oss:20b` through its
`gpt-oss:20b-64k` tag served by ollama 0.34.0 on argenta, through the local
setup described in
`2026-09-10-qwen3.8-27b-local-candidate-zero-defect-control-nothing-in-900-seconds-on-argenta.md`.
The answer is exactly the contract: `ox`, one SEARCH/REPLACE block, no
prose, no fence. The SEARCH text is the two-line pattern entry copied
character for character; the scorer found it once and applied it. Behind
it, seven of eight verdicts hold and the patched list scans `ox` clean. The
miss is `aws_secret_access_key`: the new pattern is `\w*secret\b`, and the
`\b` after `secret` cannot fall before the underscore of `_access_key`. 36
seconds, 2,485 completion tokens. Thirty seconds earlier the same model on
the unified-diff arm produced a diff with no file header and nothing to
score.

## Evidence

Log `logs/2026-09-11T02-27-55Z`, `context_bytes` 39467, `finish_reason`
stop. The scorer:

```
gate 1  APPLY   PASS  1 block(s), every SEARCH found once, verbatim
gate 2  SCAN    7 of 8 verdicts hold
        aws_secret_access_key=…    required hit   after miss
gate 3  SELF    PASS  zero hits over ox at the pin and as patched
scope   in contract: nothing outside SECRET_PATTERNS changed
RESULT  FAIL  (gate 2: 1 of 8 verdicts wrong)
```

## So what

Same model, same task, same parameters, a minute apart: the diff arm gave
git nothing it could read, the search/replace arm gave the scorer a block
it applied verbatim and a pattern one word boundary short of the answer.
That is the difference the Diff-XYZ study measured on small open models and
the reason Aider strips line numbers, observed here on a 14 GB model in
under a minute. It does not make the pattern right, and the same
`\b`-after-`secret` mistake sank Gemma's diff-arm run too; the format moved
the failure from the delivery to the regex, which is where a reader can see
it.

## Cost

Nothing billed; mechanically scored, so `usd_total` equals `usd_model`.
