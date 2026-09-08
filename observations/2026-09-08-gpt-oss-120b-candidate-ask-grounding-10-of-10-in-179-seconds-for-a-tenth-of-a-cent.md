<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-08
venue: openrouter
model: openai/gpt-oss-120b
kind: findings
source: oxbox-run
agent: claude-fable-5-1
corpus: oxbox-ask-grounding
role: candidate
run: 2026-09-08T00-48-59Z-5
wall_s: 179
hits: 10
hits_of: 10
usd_model: 0.0009
usd_total: 0.0009
---

# gpt-oss-120b as a candidate on ask-grounding: 10 of 10 in 179 seconds for a tenth of a cent

**What happened** — `oxbox-ask-grounding` (`ox` at `6072d56`, 39,467 B, `--mode ask`, effort high, 100,000 tokens, temperature 0.2) put to `openai/gpt-oss-120b`. Run as a candidate in the try-next batch the editor approved in round 8 of the rating review (2026-09-07), seven models on the three fixtures, unpinned. Ten correct, each
answer quoting the identifier it rests on, and all three unsettled questions
declined ("the source code does not specify", "does not address"). 3,250
completion tokens, 2,959 of them reasoning, 179 seconds, route DeepInfra,
$0.0009 billed, the cheapest paid answer on this fixture with DeepSeek's.

Scored by `corpora/scorers/ask_grounding.py` (8 mechanically correct, 2 to a
reader) and the reader: q2 and q7 correct.

## Evidence

Log `logs/2026-09-08T00-48-59Z-5`, `finish_reason` stop, prompt 9,525,
completion 3,250, reasoning 2,959, `route` DeepInfra, `venue_cost` 0.0009.

## So what

As good as anything in the table on grounding, at DeepSeek's price, three
times slower than the field. Most of the time went to reasoning at the
fixture's fixed effort of high; the model's own default is medium, which the
manifest could pin if it is ever rated in.

## Cost

Scorer-verified, so `usd_total` equals `usd_model`. $0.0009 over 10 hits is
$0.00009 per hit against the $0.0276 ceiling: cost 5, quality 5, speed 3.
