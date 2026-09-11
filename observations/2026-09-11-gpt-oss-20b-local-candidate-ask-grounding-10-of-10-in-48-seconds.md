<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-11
venue: ollama
model: gpt-oss:20b
kind: findings
source: oxbox-run
agent: claude-fable-5-1
corpus: oxbox-ask-grounding
role: candidate
run: 2026-09-11T00-09-26Z-2
wall_s: 48
hits: 10
hits_of: 10
usd_model: 0
usd_total: 0
---

# gpt-oss 20B, local, as a candidate on ask-grounding: 10 of 10 in 48 seconds, and it answered question 8 from the source's silence

**What happened** — `oxbox-ask-grounding` (`ox` at `6072d56`, 39,467 B,
`--mode ask`, effort high, 100,000 tokens, temperature 0.2) put to
`gpt-oss:20b` served by ollama 0.34.0 on argenta (Mac Studio M3 Ultra,
60-core GPU, 96 GB), through the local setup described in
`2026-09-10-qwen3.8-27b-local-candidate-zero-defect-control-nothing-in-900-seconds-on-argenta.md`.
Ten of ten. 9,539 prompt tokens, 3,131 completion, 11,718 characters of
reasoning, 48 seconds. Its hosted sibling `openai/gpt-oss-120b` scored the
same on 2026-09-08 in 179 seconds through OpenRouter.

**Server settings** — ollama 0.34.0 with no `OLLAMA_CONTEXT_LENGTH` set, so the model loaded at `num_ctx` 131,072, its full architectural context (`/api/ps` `context_length` read while the same tag served the batch's patch run). The OpenAI-compatible endpoint takes no `num_ctx` from the request, so the fixture could not lower it. Read timeout 3,600 seconds (the release's is 900).

## Evidence

Log `logs/2026-09-11T00-09-26Z-2`, `context_bytes` 39467, `finish_reason`
stop. The scorer: all five executable facts match the key; 1, 3, 4, 5, 9 and
10 correct mechanically; 2, 6, 7 and 8 for a reader. Read by hand: 6 gives
"400 000 bytes" with a space where the pattern wanted a comma; 2 names
`NoRedirects` turning the 302 into an `HTTPError` with the header not
re-sent; 7 says ox exits immediately with the error and tries no other entry;
8 says ox does not wait or retry after a 429 and fails immediately, with no
interval invented, the shape GPT-5.6 Sol and GLM-5.3 Flash gave and the record
scored correct. 10 of 10.

## So what

A 14 GB model answers the grounding quiz in under a minute on a workstation,
and the same model spends 22 minutes looping on a 6 KB review prompt. The
fixture separates fabrication from grounding, not usable from unusable, and
this model is on the right side of the first and the wrong side of the second.

## Cost

Nothing billed; mechanically scored, so `usd_total` equals `usd_model`.
