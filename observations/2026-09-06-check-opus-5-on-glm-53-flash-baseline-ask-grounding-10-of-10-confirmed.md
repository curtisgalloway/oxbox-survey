<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-06
venue: claude-code
model: "-"
kind: efficiency
source: manual
agent: claude-fable-5-1
checkers: claude-opus-5
run: 2026-09-03T03-20-23Z
harness_model: claude-opus-5
harness_window: 2026-09-06T23:34Z..2026-09-06T23:37Z
harness_seconds: 61
harness_in: 16
harness_cache_read: 434642
harness_cache_write: 47340
harness_unpriced: output unmeasured; the Agent tool's total minus input and cache writes is not the output (see the same-day observation on the constant residue)
---

# Check record: Opus 5 scores the GLM-5.3 Flash baseline ask-grounding answers 10 of 10, confirming the record

**What happened** — Re-measuring the checking half of the 2026-09-02 baseline runs. A fresh Opus 5 subagent scored the ten answers GLM-5.3 Flash gave on `oxbox-ask-grounding` (run `2026-09-03T03-20-23Z`) against the answer key and the pinned `ox`, reading nothing else. Every answer correct, none wrong, none fabricated, each with the settling line cited. 61 seconds.

## Evidence

Transcript `be37f5ce-2218-4a5c-b328-8de99b76b7a7/subagents/agent-ab7ddf754c91cb2b1.jsonl`. Input 16, cache read 434,642, cache write 47,340; output unmeasured.

## So what

The record's 10 of 10 stands under an independent reader, and the checking half of this run is now measured for this checker rather than carried as an unpriced share.
