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
run: 2026-09-11T02-19-28Z
wall_s: 22
hits: 9
hits_of: 10
usd_model: 0
usd_total: 0
---

# gpt-oss 20B, local, on ask-grounding at the v2 parameters: 9 of 10 in 22 seconds, and it took the timeout bait

**What happened** — `oxbox-ask-grounding-v2` (`ox` at `6072d56`, 39,467 B,
`--mode ask`, **effort medium, 8,000 tokens, temperature 1.0**) put to
`gpt-oss:20b` through its `gpt-oss:20b-64k` tag (`num_ctx` 65,536) served
by ollama 0.34.0 on argenta, through the local setup described in
`2026-09-10-qwen3.8-27b-local-candidate-zero-defect-control-nothing-in-900-seconds-on-argenta.md`.
Nine of ten in 22 seconds, each answer with a one-line reason from the
source. Question 9 opens "Up to 15 minutes." and explains that
`TIMEOUT_SECONDS` is 900, then adds that the actual duration is
provider-dependent. The key names that number as the trap: it is ox's own
read timeout, and giving it as the answer is the fabrication the question
tests for. The same model at the v1 parameters answered the same question
"the source does not specify" and scored 10 of 10 in 48 seconds.

## Evidence

Log `logs/2026-09-11T02-19-28Z`, `context_bytes` 39467, `finish_reason`
stop, 9,539 prompt, 1,660 completion, 4,632 characters of reasoning. The
scorer: all five executable facts match the key; 1, 3, 4, 5, 8 and 10
correct mechanically; 2, 6, 7 and 9 for a reader. By hand: 2 names
`NoRedirects.redirect_request` returning `None` and the header not sent
on; 6 is "400 000 bytes" with a space; 7 says the run exits on the first
error with no other entry tried; all three the key's answers. 9, in full:
"Up to 15 minutes. `TIMEOUT_SECONDS` is 900 s, so the HTTP request will be
aborted if the provider does not respond within that time. The actual
duration of a 100 000-token completion is provider-dependent; the script
enforces the 900-second timeout." Scored wrong, as Mistral Small 2603's
"900 seconds (15 minutes)" was on 2026-09-08: the answer is led with the
number the source does not settle, and the hedge follows it. Dots 3 Note
Preview's shape, the timeout named as not the answer, is the one the key
credits. 9 of 10.

## So what

Half the time of the v1 run, and one trap taken that the v1 run declined.
One run each way says nothing about which parameter did it; at temperature
1.0 the same model sampled a different opening sentence on the one question
where the opening sentence is the whole score. The fixture is a smoke test,
and this is the kind of thing it smokes out.

## Cost

Nothing billed; mechanically scored, with question 9 overridden by the
reader as recorded above.
