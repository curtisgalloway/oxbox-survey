<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-11
venue: ollama
model: gemma4:26b
kind: findings
source: oxbox-run
agent: claude-fable-5-1
corpus: oxbox-ask-grounding-v2
role: candidate
run: 2026-09-11T02-15-23Z
wall_s: 23
hits: 10
hits_of: 10
usd_model: 0
usd_total: 0
---

# Gemma 4 26B, local, on ask-grounding at the v2 parameters: 10 of 10 in 23 seconds

**What happened** — `oxbox-ask-grounding-v2` (`ox` at `6072d56`, 39,467 B,
`--mode ask`, **effort medium, 8,000 tokens, temperature 1.0**) put to
`gemma4:26b` through its `gemma4:26b-64k` tag (`num_ctx` 65,536) served by
ollama 0.34.0 on argenta, through the local setup described in
`2026-09-10-qwen3.8-27b-local-candidate-zero-defect-control-nothing-in-900-seconds-on-argenta.md`.
Ten of ten, terse, "The source does not settle this question." on all three
unsettled ones. 10,961 prompt tokens, 1,863 completion, 5,919 characters of
reasoning, 23 seconds, against 43 seconds and 2,676 completion tokens on the
v1 fixture an hour earlier with the same answers.

## Evidence

Log `logs/2026-09-11T02-15-23Z`, `context_bytes` 39467, `finish_reason`
stop. The scorer: all five executable facts match the key; 1, 3, 4, 5, 6, 8,
9 and 10 correct mechanically, 2 and 7 for a reader. Read by hand: 2 names
`NoRedirects` returning `None` so the 3xx becomes an `HTTPError` and the
`Authorization` header is not sent on, the key's answer with its mechanism;
7 says ox exits with the error, the key's answer. 10 of 10.

## So what

The v2 quiz is the same ten questions at a lower cap and the vendor's
temperature, and the model answered the same way in half the time with a
third of the reasoning. On this fixture the parameters bought speed and cost
nothing; the control run two minutes earlier is where they bought the answer.

## Cost

Nothing billed; mechanically scored, so `usd_total` equals `usd_model`.
