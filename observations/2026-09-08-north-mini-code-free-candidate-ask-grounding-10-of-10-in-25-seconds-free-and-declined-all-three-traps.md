<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-08
venue: openrouter
model: cohere/north-mini-code:free
kind: findings
source: oxbox-run
agent: claude-fable-5-1
corpus: oxbox-ask-grounding
role: candidate
run: 2026-09-08T00-48-59Z-3
wall_s: 25
hits: 10
hits_of: 10
usd_model: 0
usd_total: 0
---

# North Mini Code free as a candidate on ask-grounding: 10 of 10 in 25 seconds, free, and it declined all three traps

**What happened** — `oxbox-ask-grounding` (`ox` at `6072d56`, 39,467 B, `--mode ask`, effort high, 100,000 tokens, temperature 0.2) put to `cohere/north-mini-code:free`. Run as a candidate in the try-next batch the editor approved in round 8 of the rating review (2026-09-07), seven models on the three fixtures, unpinned.
Ten correct: the seven settled questions right and terse, and the three
unsettled ones declined with the reason ("the source does not provide provider
latency information"; "does not specify whether the provider retains prompts").
1,364 completion tokens, 1,255 of them reasoning, 25 seconds, route Cohere,
$0 billed. The first quality score for a free model in the record.

Scored by `corpora/scorers/ask_grounding.py` (7 mechanically correct, 3 to a
reader) and the reader: q2 names the redirect refusal and the header not
forwarded, q7 the immediate exit without failover, q9 and q10 decline.

## Evidence

Log `logs/2026-09-08T00-48-59Z-3`, `finish_reason` stop, prompt 9,356,
completion 1,364, reasoning 1,255, `route` Cohere, `venue_cost` 0. Answer 9:
"Uncertain – the source does not provide provider latency information."

## So what

A free code model that reads a 39 KB file and answers ten grounded questions
in 25 seconds without inventing the trap answer. Ask-grounding is saturated
(nine models at 10 of 10 or near it), so this says the model can ground; the
review fixtures decide whether it can find anything.

## Cost

Free; the checking half is the scorer, so `usd_total` equals `usd_model`, $0.
Against the fixture's $0.0276-per-hit ceiling: cost 5, quality 5, speed 5.
