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
corpus: oxbox-ask-grounding-v2
role: candidate
run: 2026-09-11T02-26-39Z
wall_s: 28
hits: 10
hits_of: 10
usd_model: 0
usd_total: 0
---

# gpt-oss 20B, local, on ask-grounding at the v2 parameters, second run: 10 of 10 in 28 seconds, and this time it declined the timeout

**What happened** — `oxbox-ask-grounding-v2` (`ox` at `6072d56`, 39,467 B,
`--mode ask`, effort medium, 8,000 tokens, temperature 1.0) put to
`gpt-oss:20b` through its `gpt-oss:20b-64k` tag served by ollama 0.34.0 on
argenta, a second time seven minutes after the first
(`2026-09-11-gpt-oss-20b-local-candidate-ask-grounding-v2-9-of-10-in-22-seconds-and-it-took-the-timeout-bait.md`).
The repeat was not planned: a batch driver that should have been stopped
ran the first pass, and its replacement ran the second; both are valid
runs at the task's parameters and both are recorded. Ten of ten. Question
9 this time: "The source code does not specify how long the provider takes
to generate 100,000 completion tokens; this depends on the external
provider and is not reported by `ox`." The first run had opened the same
answer with "Up to 15 minutes."

## Evidence

Log `logs/2026-09-11T02-26-39Z`, `context_bytes` 39467, `finish_reason`
stop, 9,539 prompt, 1,250 completion, 3,616 characters of reasoning. The
scorer: all five executable facts match the key; 1, 3, 4, 5, 8 and 9
correct mechanically; 2, 6, 7 and 10 for a reader. By hand: 2 names
`NoRedirects` turning the 302 into an `HTTPError` with the header not
forwarded; 6 is "400 000 bytes"; 7 says ox terminates on the first error
and tries no other entry; 10 says the source does not mention retention
or training. All four the key's answers. 10 of 10.

## So what

Two runs of the same model at the same parameters, seven minutes apart,
scored 9 and 10, and the difference is the opening clause of one answer.
At temperature 1.0 that is what a single run is worth on a ten-question
quiz with three traps, and it is the reason the fixture was demoted to a
smoke test: it tells you the model grounds and does not fabricate wholesale,
and a one-point difference between runs is noise.

## Cost

Nothing billed; mechanically scored, so `usd_total` equals `usd_model`.
