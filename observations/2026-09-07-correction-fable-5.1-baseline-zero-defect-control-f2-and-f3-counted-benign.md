<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-07
venue: openrouter
model: anthropic/claude-fable-5.1
kind: findings
source: manual
agent: claude-fable-5-1
corpus: oxbox-clean-control
role: baseline
corrects: 2026-09-06-fable-5.1-baseline-clean-control-five-findings-both-known-defects-hedged.md
benign: 2
---

# Correction: Fable 5.1's F2 and F3 on the zero-defect control are counted benign

**What changed** — The observation this corrects recorded findings F2 (the
`/etc/shadow` read probe is vacuous at every uid) and F3 (`probe()` drops the
list of leaked variables from the FAIL line) of run `2026-09-06T21-22-57Z` as
"true, negligible": confirmed by both checkers, the metered pair included,
reproducible, and with no consequence beyond a failure in the safe direction.
The record had no field for that category, so they counted nowhere. The
editor's ruling on 2026-09-07 (round 8, question 1): such findings count
separately. "A failure that isn't really a failure is a waste of time to
fix." This correction carries `benign: 2`; `real` stays 2 of 5 and the cost
divisor is unchanged. The original observation stays as written.
