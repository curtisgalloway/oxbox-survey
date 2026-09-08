<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-07
venue: openrouter
model: openai/gpt-5.6-sol
kind: findings
source: manual
agent: claude-fable-5-1
corpus: oxbox-clean-control
role: baseline
corrects: 2026-09-02-gpt-5.6-sol-baseline-clean-control-eight-findings-one-real-six-invented.md
benign: 1
---

# Correction: GPT-5.6 Sol's P3 on the zero-defect control is counted benign

**What changed** — Finding P3 of run `2026-09-03T02-41-51Z` (`getaddrinfo` can
succeed from `/etc/hosts`, reporting a DNS leak that is not one) was recorded
"true, negligible": the mechanism holds and the error is a false FAIL, the
safe direction. The verdict key accepts CONFIRMED or UNCERTAIN for it and
rejects REFUTED. Under the editor's ruling of 2026-09-07 (round 8, question 1)
it counts separately: `benign: 1`, with `real` unchanged at 1 of 8. The
original observation stays as written.
