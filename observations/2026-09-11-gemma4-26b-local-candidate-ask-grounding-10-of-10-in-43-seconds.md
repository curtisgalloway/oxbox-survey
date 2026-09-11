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
corpus: oxbox-ask-grounding
role: candidate
run: 2026-09-11T00-08-43Z
wall_s: 43
hits: 10
hits_of: 10
usd_model: 0
usd_total: 0
---

# Gemma 4 26B, local, as a candidate on ask-grounding: 10 of 10 in 43 seconds, terse, and it declined all three traps

**What happened** — `oxbox-ask-grounding` (`ox` at `6072d56`, 39,467 B,
`--mode ask`, effort high, 100,000 tokens, temperature 0.2) put to
`gemma4:26b` served by ollama 0.34.0 on argenta (Mac Studio M3 Ultra,
60-core GPU, 96 GB), through the local setup described in
`2026-09-10-qwen3.8-27b-local-candidate-zero-defect-control-nothing-in-900-seconds-on-argenta.md`.
Ten of ten: the seven settled questions right, in one line each, and "The
source does not say." on all three unsettled ones. 10,961 prompt tokens, 2,676
completion, 9,513 characters of reasoning, 43 seconds. The same model spent
21 minutes looping to nothing on the zero-defect control an hour earlier.

**Server settings** — ollama 0.34.0 with no `OLLAMA_CONTEXT_LENGTH` set, so the model loaded at `num_ctx` 262,144, its full architectural context (`/api/ps` `context_length` read during the run). The OpenAI-compatible endpoint takes no `num_ctx` from the request, so the fixture could not lower it. Read timeout 3,600 seconds (the release's is 900).

## Evidence

Log `logs/2026-09-11T00-08-43Z`, `context_bytes` 39467, `finish_reason`
stop. `corpora/scorers/ask_grounding.py --run … --repo <pin>`: all five
executable facts match the key; answers 1, 3, 4, 5, 6, 9 and 10 scored
correct mechanically, 2, 7 and 8 marked for a reader. Read by hand: 2 says the
redirect is refused and the `Authorization` header is not re-sent, which is
the key's answer; 7 says ox exits with the failure's message, which is the
key's answer; 8 says the source does not say, which the key accepts and the
scorer's pattern did not match. 10 of 10.

## So what

The cheapest answer on this fixture so far in wall-clock terms among the
local models, and the terse shape the key rewards. The fixture is a smoke test
since 2026-09-08 and this is what it is for: the model answers, and it does not
fabricate under a trap. It says nothing about the review loop the same model
fell into on the control.

## Cost

Nothing billed; mechanically scored, so `usd_total` equals `usd_model`.
