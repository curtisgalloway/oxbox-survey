<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-07
venue: openrouter
model: z-ai/glm-5.3-flash
kind: findings
source: manual
agent: claude-fable-5-1
corpus: oxbox-clean-control
role: baseline
corrects: 2026-09-02-glm-5.3-flash-baseline-clean-control-four-findings-one-real-and-it-hedged-the-right-one.md
benign: 1
---

# Correction: GLM-5.3 Flash's L4 on the zero-defect control is counted benign

**What changed** — Finding L4 of run `2026-09-03T03-21-05Z` (`jailtest-ok.txt`
is never removed, so it dirties `git status` and accumulates) was recorded
"true, negligible": true, and with no consequence for containment. Under the
editor's ruling of 2026-09-07 (round 8, question 1) it counts separately:
`benign: 1`, with `real` unchanged at 1 of 4 (G1). The original observation
stays as written.
