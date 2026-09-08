<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-08
venue: openrouter
model: inclusionai/ling-3.0-flash-fin:free
kind: findings
source: manual
agent: claude-opus-5
corpus: oxbox-clean-control
role: candidate
corrects: 2026-09-08-ling-3.0-flash-fin-free-candidate-zero-defect-control-spent-its-whole-32k-cap-reasoning-and-returned-nothing.md
answered: false
---

# Correction: Ling 3.0 Flash Fin returned nothing on the zero-defect control, and the record now says so in a field

**What changed** — Nothing about the run. `answered: false` is a new field,
added 2026-09-08 with the editor's ruling on round 11 question 5, and this run
is one of the four in the record that needs it.

The ruling scores cost as a dash, not a 0, when a model answers a
zero-expected-findings fixture and correctly reports nothing. Applying it
required a distinction the frontmatter could not make. This run and Dots 3
Note Preview's on the same fixture the same night recorded identical measured
fields -- `findings: 0`, `real: 0`, `usd_model: 0` -- and mean opposite
things: Dots 3 gave the fixture's ideal answer, and this run spent 31,671 of
its 32,768-token completion cap reasoning and returned empty content with
`finish_reason: length`. Only the prose told them apart, so the ruling as
written would have given this run the ideal answer's dash.

`answered: false` says the model returned no content at all. It keeps the
quality 0 the empty-answer rule already gave this run and keeps its cost score
at 0. The original observation stays as written.
