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
corpus: oxbox-secret-scanner-fix-sr
role: candidate
run: 2026-09-11T02-22-18Z
wall_s: 176
answered: false
applies: false
hits: 0
hits_of: 8
usd_model: 0
usd_total: 0
---

# Gemma 4 26B, local, on the secret-scanner fix (search/replace arm): spent the whole 16,000-token cap reasoning about the blocks and returned none

**What happened** — `oxbox-secret-scanner-fix-sr` (`ox` at `6072d56`,
39,467 B, `--mode ask` with the SEARCH/REPLACE delivery instruction,
**effort medium, 16,000 tokens, temperature 1.0**) put to `gemma4:26b`
through its `gemma4:26b-64k` tag served by ollama 0.34.0 on argenta,
through the local setup described in
`2026-09-10-qwen3.8-27b-local-candidate-zero-defect-control-nothing-in-900-seconds-on-argenta.md`.
`finish_reason` `length`: 16,000 completion tokens, 41,608 characters of
reasoning, content empty, no blocks. Five minutes earlier the same model
delivered the same change as a unified diff in 11,180 tokens with room to
spare (`2026-09-11-gemma4-26b-local-candidate-secret-scanner-fix-v3-eight-of-eight-behind-a-hunk-header-git-refuses-and-a-pattern-that-refuses-ox-itself.md`).
The first run of this arm at the 8,000-token cap the research suggested had
done the same at 8,000, which is why both patch arms were raised to 16,000
before either was recorded; this is the run at the raised cap, and it
exhausted that too.

## Evidence

Log `logs/2026-09-11T02-22-18Z`, `context_bytes` 39467; `response.json`
`usage` prompt 11,059, completion 16,000; `message.content` `""`. The
scorer: "gate 1 APPLY FAIL no SEARCH/REPLACE block in content.md". The
driver's stderr:

```
oxbox-send: finish=length prompt_tokens=11059 completion_tokens=16000 reasoning_chars=41608
oxbox-send: model returned no content (finish=length)
```

## So what

The search/replace arm was added because the format carries no line counts
for a small model to get wrong; on this model the format cost it the
answer instead. Same task, same model, same parameters, and the diff arm
finished in 11k tokens while the search/replace arm ran past 16k. One run
each does not say why; the reasoning was not read for this record beyond
its length, and whether it loops or deliberates is a question for the
next run. What the row says is that a delivery format is not free to
change, and that the arm's cap may still be measuring the cap.

## Cost

Nothing billed; three minutes of a Mac Studio for no blocks.
