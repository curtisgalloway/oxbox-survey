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
corpus: oxbox-secret-scanner-fix
role: candidate
run: 2026-09-11T00-39-05Z
wall_s: 1370
answered: false
applies: false
hits: 0
hits_of: 8
usd_model: 0
usd_total: 0
---

# gpt-oss 20B, local, as a candidate on the secret-scanner fix: drafted the same patch until the cap and returned nothing in 23 minutes

**What happened** — `oxbox-secret-scanner-fix` (`ox` at `6072d56`, 39,467 B,
`--mode diff`, effort high, 100,000 tokens, temperature 0.2) put to
`gpt-oss:20b` served by ollama 0.34.0 on argenta (Mac Studio M3 Ultra,
60-core GPU, 96 GB), through the local setup described in
`2026-09-10-qwen3.8-27b-local-candidate-zero-defect-control-nothing-in-900-seconds-on-argenta.md`.
`finish_reason` `length`: 100,000 completion tokens of reasoning, 469,390
characters, content empty, no patch. Its third fixture in this batch and its
second exhaustion; the grounding quiz it answered in 48 seconds.

**Server settings** — ollama 0.34.0 with no `OLLAMA_CONTEXT_LENGTH` set, so the
model loaded at `num_ctx` 131,072, its full architectural context (`/api/ps`
`context_length` read during this run). The OpenAI-compatible endpoint takes no
`num_ctx` from the request, so the fixture could not lower it. Read timeout
3,600 seconds (the release's is 900).

## Evidence

Log `logs/2026-09-11T00-39-05Z`, `context_bytes` 39467; `response.json`
`usage` prompt 9,635, completion 100,000; `message.content` `""`. The scorer:
"gate 1 APPLY FAIL no fenced diff block in content.md". The driver's stderr:

```
oxbox-send: finish=length prompt_tokens=9635 completion_tokens=100000 reasoning_chars=469390
oxbox-send: model returned no content (finish=length)
```

This loop has a different shape from the control's. The reasoning restates
the five missed forms correctly, drafts a pattern, and then drafts the whole
patch again: 180 distinct non-blank lines out of 497, and the two pattern
lines it keeps re-emitting, the private-key block and the Slack token, appear
57 and 55 times. The tail is a half-written `+` line of a unified diff. It had
the answer in hand for most of 23 minutes and never stopped writing it.

## So what

Three local reasoning runs at the v1 parameters exhausted the cap and one
answered. The prior-art review of the same day (`docs/prior-art-2026-09-10.md`)
puts this in its context: gpt-oss looping at reasoning `high` under ollama is
an open upstream issue since 2025-10, and the vendor's card sets temperature
1.0 where the fixture sent 0.2. The v2 fixtures run at the card's sampling and
a cap the task needs; this model's v2 rows are the test of whether that ends
it.

## Cost

Nothing billed; 23 minutes of a Mac Studio for no patch.
