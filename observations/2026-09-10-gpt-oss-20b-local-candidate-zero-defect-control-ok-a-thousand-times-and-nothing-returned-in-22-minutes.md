<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-10
venue: ollama
model: gpt-oss:20b
kind: findings
source: oxbox-run
agent: claude-fable-5-1
corpus: oxbox-clean-control
role: candidate
run: 2026-09-10T23-20-42Z-2
wall_s: 1322
answered: false
findings: 0
real: 0
usd_model: 0
usd_total: 0
---

# gpt-oss 20B, local, as a candidate on the zero-defect control: "Ok." a thousand times and nothing returned in 22 minutes

**What happened** — `oxbox-clean-control` (`jailtest.py` at `6302b12`,
6,096 B, review mode, effort high, 100,000 tokens, temperature 0.2) put to
`gpt-oss:20b` (MXFP4, 13.8 GB) served by ollama 0.34.0 on argenta (Mac Studio
M3 Ultra, 60-core GPU, 96 GB), through the local setup described in
`2026-09-10-qwen3.8-27b-local-candidate-zero-defect-control-nothing-in-900-seconds-on-argenta.md`,
with the read timeout raised to 3,600 seconds. `finish_reason` `length`: all
100,000 completion tokens went to reasoning, 436,059 characters, content
empty. Its hosted sibling `openai/gpt-oss-120b` timed out at 900 seconds on
this fixture on 2026-09-08 and then, pinned to DeepInfra, emitted twelve
findings with one real.

**Server settings** — ollama 0.34.0 with no `OLLAMA_CONTEXT_LENGTH` set, so the model loaded at `num_ctx` 131,072, its full architectural context (`/api/ps` `context_length` read while the same tag served the batch's patch run). The OpenAI-compatible endpoint takes no `num_ctx` from the request, so the fixture could not lower it. Read timeout 3,600 seconds (the release's is 900).

## Evidence

Log `logs/2026-09-10T23-20-42Z-2`: `response.json` `usage` prompt 1,795,
completion 100,000; `message.content` `""`, `message.reasoning` 436,059
characters. The driver's stderr:

```
oxbox-send: finish=length prompt_tokens=1795 completion_tokens=100000 reasoning_chars=436059
oxbox-send: model returned no content (finish=length)
```

The reasoning is a loop: 240 distinct non-blank lines out of 2,783. "Ok."
appears 1,000 times. The four next most common lines, 138 to 141 times each,
are the same sentence with one word changed: "Now potential bug: The code
uses `probe` to test reading a path. But if the path is a symlink to a
{directory, file} that is {accessible, not accessible} …". It never leaves the
symlink question. 100,000 tokens in 1,322 seconds is 76 tokens per second.

## So what

Two of the three local reasoning models exhausted the cap on a 6 KB file with
nothing to show, and the loops differ: Gemma re-checks every function, gpt-oss
circles one hypothetical. Neither is the shared-pool stall the hosted timeouts
were; both are the model failing to stop. On ask-grounding the same model
answered 10 of 10 in 48 seconds
(`2026-09-11-gpt-oss-20b-local-candidate-ask-grounding-10-of-10-in-48-seconds.md`).

## Cost

Nothing billed, nothing to read. 22 minutes of a Mac Studio.
