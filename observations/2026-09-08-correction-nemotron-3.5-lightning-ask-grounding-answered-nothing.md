<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-08
venue: openrouter
model: nvidia/nemotron-3.5-lightning
kind: findings
source: manual
agent: claude-opus-5
corpus: oxbox-ask-grounding
role: candidate
corrects: 2026-09-08-nemotron-3.5-lightning-candidate-ask-grounding-answered-with-nothing-in-3-seconds-every-token-reasoning.md
answered: false
---

# Correction: Nemotron 3.5 Lightning's empty ask-grounding answer carries the answered field

**What changed** — Nothing about the run. `answered: false` is a new field,
added 2026-09-08 with the editor's ruling on round 11 question 5, and this run
is the record's clearest case of the thing it names: an empty answer in 3
seconds, 519 completion tokens all reasoning, `finish_reason: stop`, 0 of 10.

The cost score here was already 0 by the divisor, so the field changes no
score on this row. It is recorded because the same ruling demoted
ask-grounding to a smoke test (round 11, question 8), where the question the
fixture now answers is exactly "did the model answer at all" -- and this is
the one run in thirteen where it did not.

The original observation stays as written.
