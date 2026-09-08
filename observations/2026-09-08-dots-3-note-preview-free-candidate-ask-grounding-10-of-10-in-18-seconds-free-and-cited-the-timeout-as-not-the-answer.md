<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-08
venue: openrouter
model: dots-studio/dots-3-note-preview:free
kind: findings
source: oxbox-run
agent: claude-fable-5-1
corpus: oxbox-ask-grounding
role: candidate
run: 2026-09-08T01-14-42Z
wall_s: 18
hits: 10
hits_of: 10
usd_model: 0
usd_total: 0
---

# Dots 3 Note Preview free as a candidate on ask-grounding: 10 of 10 in 18 seconds, free, and it cited the timeout as not the answer

**What happened** — `oxbox-ask-grounding` (`ox` at `6072d56`, 39,467 B, `--mode
ask`, effort high, 100,000 tokens, temperature 0.2) put to
`dots-studio/dots-3-note-preview:free`. Run as a candidate in the try-next
batch the editor approved in round 8 of the rating review (2026-09-07). Ten
correct with identifiers quoted, and the three unsettled questions declined
with the right reason each time: on question 9 it named `TIMEOUT_SECONDS =
900` as "only the maximum wait before ox gives up, not a measure of response
time", the key's correct case for the trap; on question 10 it quoted the
logging warning and said the file says nothing about retention or training.
1,631 completion tokens, 1,163 reasoning, 18 seconds, route AtlasCloud, $0
billed. The second free model to score on this fixture, the second at 10 of
10.

Scored by `corpora/scorers/ask_grounding.py` (8 mechanically correct, 2 to a
reader) and the reader: q2 names the redirect refusal and the header kept
back; q7 the immediate exit without failover.

## Evidence

Log `logs/2026-09-08T01-14-42Z`, `finish_reason` stop, prompt 9,535,
completion 1,631, reasoning 1,163, `route` AtlasCloud, `venue_cost` 0.

## So what

Grounded, fast and free, and it handled the trap the way the key describes
as the best answer. As with North Mini Code, ask-grounding shows the model
can read a file honestly; the two review fixtures decide the rest.

## Cost

Free; scorer-verified, so `usd_total` equals `usd_model`, $0. Against the
$0.0276-per-hit ceiling: cost 5, quality 5, speed 5.
