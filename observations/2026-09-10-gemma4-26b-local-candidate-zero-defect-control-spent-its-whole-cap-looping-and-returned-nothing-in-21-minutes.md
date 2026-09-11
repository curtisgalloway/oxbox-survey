<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-10
venue: ollama
model: gemma4:26b
kind: findings
source: oxbox-run
agent: claude-fable-5-1
corpus: oxbox-clean-control
role: candidate
run: 2026-09-10T22-59-23Z
wall_s: 1279
answered: false
findings: 0
real: 0
usd_model: 0
usd_total: 0
---

# Gemma 4 26B, local, as a candidate on the zero-defect control: spent its whole 100,000-token cap looping and returned nothing in 21 minutes

**What happened** — `oxbox-clean-control` (`jailtest.py` at `6302b12`,
6,096 B, review mode, effort high, 100,000 tokens, temperature 0.2) put to
`gemma4:26b` (26B-A4B, Q4_K_M, 18.6 GB) served by ollama 0.34.0 on argenta
(Mac Studio M3 Ultra, 60-core GPU, 96 GB), through the local setup described
in `2026-09-10-qwen3.8-27b-local-candidate-zero-defect-control-nothing-in-900-seconds-on-argenta.md`,
with the read timeout raised to 3,600 seconds. `finish_reason` `length`: all
100,000 completion tokens went to reasoning, 352,682 characters of it, and the
content was empty. The same shape as DeepSeek V4 Flash's exhausted run on
2026-09-06 and Ling 3.0 Flash Fin's on 2026-09-08.

**Server settings** — ollama 0.34.0 with no `OLLAMA_CONTEXT_LENGTH` set, so the model loaded at `num_ctx` 262,144, its full architectural context (`/api/ps` `context_length` read during the run). The OpenAI-compatible endpoint takes no `num_ctx` from the request, so the fixture could not lower it. Read timeout 3,600 seconds (the release's is 900).

## Evidence

Log `logs/2026-09-10T22-59-23Z`: `response.json` `usage` prompt 1,969,
completion 100,000; `message.content` `""`, `message.reasoning` 352,682
characters. The driver's stderr:

```
oxbox-send: finish=length prompt_tokens=1969 completion_tokens=100000 reasoning_chars=352682
oxbox-send: model returned no content (finish=length)
```

The reasoning is a loop. Split on newlines, 336 distinct non-blank lines out of
7,194. The most repeated:

| count | line |
|---|---|
| 288 | `` `expect_blocked` is `True`. `` |
| 197 | `This is correct.` |
| 196 | `def action():` |
| 196 | `return action` |

It opens with a sound plan (goal, environment, the probes by name) and by the
end is re-reading `write_probe` and `tcp_connect` with "*Wait, I found a
potential issue in …*" and concluding "Correct." each time. 100,000 tokens in
1,279 seconds is 78 tokens per second, which matches the iac benchmark for this
model on argenta.

## So what

Cheap and fast per token and still 21 minutes for no answer, because nothing
stops the reasoning. The fixture's parameters are the survey's standard ones;
a reader who wants an answer from this model on a review prompt needs a
completion cap well under 100,000 or a lower reasoning setting, and neither
was measured here. On ask-grounding the same model answered 10 of 10 in 43
seconds (`2026-09-11-gemma4-26b-local-candidate-ask-grounding-10-of-10-in-43-seconds.md`),
so the loop is the review prompt's, not the model's in general.

## Cost

Nothing billed, nothing to read. 21 minutes of a Mac Studio.
