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
corpus: oxbox-secret-scanner-fix
role: candidate
run: 2026-09-11T00-15-06Z
wall_s: 1438
answered: false
applies: false
hits: 0
hits_of: 8
usd_model: 0
usd_total: 0
---

# Gemma 4 26B, local, as a candidate on the secret-scanner fix: re-read the missed list 434 times and returned nothing in 24 minutes

**What happened** — `oxbox-secret-scanner-fix` (`ox` at `6072d56`, 39,467 B,
`--mode diff`, effort high, 100,000 tokens, temperature 0.2) put to
`gemma4:26b` served by ollama 0.34.0 on argenta (Mac Studio M3 Ultra,
60-core GPU, 96 GB), through the local setup described in
`2026-09-10-qwen3.8-27b-local-candidate-zero-defect-control-nothing-in-900-seconds-on-argenta.md`.
`finish_reason` `length`: 100,000 completion tokens of reasoning, 275,914
characters, content empty, no patch. The second of this model's two review
and diff runs to exhaust the cap the same way; the one fixture it answered was
the grounding quiz, in 43 seconds.

**Server settings** — ollama 0.34.0 with no `OLLAMA_CONTEXT_LENGTH` set, so the
model loaded at `num_ctx` 262,144, its full architectural context (`/api/ps`
`context_length` read during the run). The OpenAI-compatible endpoint takes no
`num_ctx` from the request, so the fixture could not lower it. Read timeout
3,600 seconds (the release's is 900).

## Evidence

Log `logs/2026-09-11T00-15-06Z`, `context_bytes` 39467; `response.json`
`usage` prompt 11,083, completion 100,000; `message.content` `""`. The
scorer: "gate 1 APPLY FAIL no fenced diff block in content.md", no patch to
score. The driver's stderr:

```
oxbox-send: finish=length prompt_tokens=11083 completion_tokens=100000 reasoning_chars=275914
oxbox-send: model returned no content (finish=length)
```

The reasoning opens with a correct restatement of the task, the caught form
and the five missed forms, and then re-reads that list: 636 distinct
non-blank lines out of 4,232, and each of the five `missed` rows appears 434
or 435 times, always after "Wait, I'll check the `missed` list one more
time." It ends mid-regex. 100,000 tokens in 1,438 seconds is 70 tokens per
second with the 11k-token prompt in front.

## So what

The loop is not specific to the review prompt: on a patch task with a
five-line checklist the model checks the checklist until the cap. Two
fixtures, two exhaustions, one loop shape. Batch 2 re-runs this model on the
control at effort `medium` on a 64k tag to see whether either setting ends it.

## Cost

Nothing billed; 24 minutes of a Mac Studio for no patch.
