<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-11
venue: ollama
model: qwen3-coder:30b
kind: findings
source: oxbox-run
agent: claude-fable-5-1
corpus: oxbox-ask-grounding
role: candidate
run: 2026-09-11T02-12-37Z
wall_s: 13
hits: 9
hits_of: 10
usd_model: 0
usd_total: 0
---

# Qwen3-Coder 30B, local, as a candidate on ask-grounding: 9 of 10 in 13 seconds, and it invented a retry

**What happened** — `oxbox-ask-grounding` (`ox` at `6072d56`, 39,467 B,
`--mode ask`, 100,000 tokens, temperature 0.2, the reasoning field dropped
as described in
`2026-09-11-qwen3-coder-30b-local-candidate-zero-defect-control-a-thousand-findings-from-five-templates-zero-real-in-25-minutes.md`)
put to `qwen3-coder:30b` served by ollama 0.34.0 on argenta. Thirteen seconds
end to end, the fastest run on this fixture in the record, hosted or local.
Nine of ten. Question 8, in full: "After a 429 (Too Many Requests), `ox`
waits before retrying, but the source does not specify how long it waits or
how many times it tries." The source has no retry and no wait; the answer
asserts both and hedges only the numbers.

## Evidence

Log `logs/2026-09-11T02-12-37Z`, `context_bytes` 39467, `finish_reason`
stop. The scorer: all five executable facts match the key; 1, 3, 4, 5, 6, 8,
9 and 10 correct mechanically, 2 and 7 for a reader; **8 passed the pattern
because the sentence contains "does not specify"**. Read by hand, 2 says the
redirect is refused and the header not forwarded, 7 says ox exits with an
error, both the key's answers. 8 is scored wrong: the key says "ox has no
retry logic at all" and that the correct answer says the source does not
answer; "ox waits before retrying" is a mechanism the file does not contain,
which is the fabrication the question exists to catch, and Mistral Small
2603's "900 seconds" on question 9 was scored wrong on 2026-09-08 for the
same reason. 9 of 10.

## So what

The scorer's pattern for question 8 accepts a hedge wrapped around an
invented mechanism; this is the first answer in the record to take that
shape, and it is noted here for the scorer rather than fixed in it, since a
pattern change would re-score every archived run. The fixture is a smoke
test and the row reads as it should: answers fast, grounds well, and once
filled a gap in the source with something plausible.

## Cost

Nothing billed; mechanically scored, with question 8 overridden by the
reader as recorded above.
