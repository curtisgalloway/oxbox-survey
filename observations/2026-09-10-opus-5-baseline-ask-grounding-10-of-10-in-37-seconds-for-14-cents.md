<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-10
venue: openrouter
model: anthropic/claude-opus-5
kind: findings
source: oxbox-run
agent: claude-fable-5-1
corpus: oxbox-ask-grounding
role: baseline
run: 2026-09-10T19-36-41Z
wall_s: 37
hits: 10
hits_of: 10
usd_model: 0.14345
usd_total: 0.14345
---

# Opus 5 baseline on the grounding quiz: 10 of 10 in 37 seconds for 14 cents, and the scorer could not parse its headings

**What happened** — `oxbox-ask-grounding` (`ox` at `6072d56`, 39,467 B,
`--mode ask`, effort high, 100,000 tokens, temperature 0.2) put to
`anthropic/claude-opus-5` as a frontier baseline for the special edition
comparing cheap models against frontier ones. Ten of ten by a reader against
the answer key: the seven settled questions right with line-level mechanism,
and the three unsettled ones declined. On question 9 it cited
`TIMEOUT_SECONDS = 900` as ox's own patience and said the provider's latency
"is not stated and cannot be derived from this code", which is the form the
key credits. On question 10 it quoted the secret-scan refusal message and
said it is "ox's warning to the operator, not a description of any
provider's retention or training policy". 2,809 completion tokens, 1,107
reasoning, 37 seconds, $0.1435 billed, route Claude Platform on AWS.

## Evidence

Log `logs/2026-09-10T19-36-41Z`, `context_bytes` 39467, `finish_reason` stop,
`venue_cost` 0.14345, prompt 14,645 tokens.

`corpora/scorers/ask_grounding.py --run logs/2026-09-10T19-36-41Z` reproduced
all five executable facts against the pin and then reported every answer
`missing` and `RESULT FAIL (0 scored mechanically correct)`. The model wrote
each answer under a `## N. <title>` heading rather than as an `N.` line, and
the scorer's `split_answers` only recognizes the latter. The ten answers were
therefore read by hand against `corpora/answers/oxbox-ask-grounding.md`. The
scorer's verdict is a format artifact and is not the run's score.

## So what

The first Opus 5 run as a primary rather than a checker. Same score as every
cheap model that answered this fixture, at 143 times DeepSeek V4 Flash's
$0.0010 for the same ten answers and half of the Fable 5.1 ceiling ($0.2756
on 2026-09-06). The fixture does not separate frontier from cheap: it was
built to catch a model that guesses on the three unsettled questions, and the
only model in the record that did so is Mistral Small.

No marker and no rating: a baseline.

## Cost

Model half, billed: $0.14345 for 14,645 prompt and 2,809 completion tokens.
The checking half is the answer key, applied by a reader because the scorer
could not split this answer; no supervisor tokens were spent beyond the
session that wrote this file.
