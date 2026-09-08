<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-08
venue: openrouter
model: deepseek/deepseek-v4-flash
kind: findings
source: manual
agent: claude-opus-5
corpus: oxbox-clean-control
role: candidate
corrects: 2026-09-06-deepseek-v4-flash-candidate-clean-control-spends-the-whole-budget-reasoning-and-returns-nothing-in-33-minutes.md
answered: false
---

# Correction: DeepSeek V4 Flash's 33-minute blowout returned nothing, and the record now says so in a field

**What changed** — Nothing about the run. `answered: false` is a new field,
added 2026-09-08 with the editor's ruling on round 11 question 5.

Run `2026-09-06T22-46-39Z` went to StreamLake and returned after 1,984 seconds
with 99,999 of 100,000 tokens spent reasoning and no content. Its measured
fields (`findings: 0`, `real: 0`) are the same ones a model writes when it
reads the fixture and correctly reports no defects, which is the answer this
fixture is looking for. Without a field to separate them, the ruling would
have scored this blowout's cost as a dash.

`answered: false` says the model returned no content at all, so the cost score
stays 0. The original observation stays as written.
