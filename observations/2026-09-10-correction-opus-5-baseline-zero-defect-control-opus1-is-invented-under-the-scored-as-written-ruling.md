<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-10
venue: openrouter
model: anthropic/claude-opus-5
kind: findings
source: manual
agent: claude-fable-5-1
corpus: oxbox-clean-control
role: baseline
corrects: 2026-09-10-opus-5-baseline-zero-defect-control-nine-findings-both-known-defects-one-benign-six-invented.md
real: 1
---

# Correction: Opus 5's OPUS1 on the zero-defect control is counted invented, so the run is 9 emitted, 1 real, 1 benign, 7 invented

**What changed** — Finding OPUS1 of run `2026-09-10T19-37-18Z` (the stat
oracle on `/etc/shadow`, the record's G1) was recorded real on the ground
that the triggering state occurs at the pin and a CI log had shown it, over
both metered checkers, which refuted it as written because its stated
premise, that the launcher emits system paths first, is false. The editor
ruled on 2026-09-10 (special edition 3, round 2 decision): **invented,
because a finding is scored as written and the reason was wrong.** `real`
goes from 2 to 1; `benign` stays 1; the original observation stays as
written. The two checkers' verdicts on the batch were already what the
ruling gives, so the record now agrees with both on every finding but
OPUS8.

The same ruling does not reach Gemini 3.8 Flash's GFL1 on the same defect,
which carried the wrong "sorted first" clause beside a right one, "the only
path present in a minimal CI/container environment", and which both
checkers confirmed on the right clause. It stays real.
