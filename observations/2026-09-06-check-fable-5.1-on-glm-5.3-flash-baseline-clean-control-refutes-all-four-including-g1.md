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
checkers: claude-fable-5-1
run: 2026-09-03T03-21-05Z
harness_model: claude-fable-5-1
harness_window: 2026-09-06T23:34Z..2026-09-06T23:37Z
harness_seconds: 90
harness_in: 66
harness_cache_read: 114659
harness_cache_write: 75485
harness_unpriced: output unmeasured; the Agent tool's total minus input and cache writes is not the output (see the same-day observation on the constant residue)
---

# Check record: Fable 5.1 on the GLM-5.3 Flash baseline clean-control run refutes all four findings, dissenting from the record on G1

**What happened** — Re-measuring the checking half of the 2026-09-02 baseline runs, whose verification ran in an unmeasured Opus subagent. A fresh Fable 5.1 subagent verified the four findings GLM-5.3 Flash emitted on `oxbox-clean-control` as a baseline (run `2026-09-03T03-21-05Z`), same contract and files as every checker today, both platforms named. Three model calls, six tool uses, 90 seconds. Verdicts: G1 REFUTED, G2 REFUTED, G3 REFUTED, G4 REFUTED.

The record has G1 as real (the verdict key's L1, the offline-host defect, fixed upstream in `0090c35`) and the other three as inventions or negligible. Fable's checker refutes G1 as written: the stated consequence, an offline host certifying "a jail that actually permits full outbound egress", needs a jail that permits egress, and no jail this tree launches does. The same-day reproduction on dev showed the mechanism live, `ENETUNREACH` raised as `OSError` inside a working jail, so the checker is not wrong about the code; it is applying "as written" to the consequence, the way the C3 ruling did. The Opus checker of the same batch confirmed G1 and the record stands until the editor says otherwise.

## Evidence

Transcript `be37f5ce-2218-4a5c-b328-8de99b76b7a7/subagents/agent-a21f9155c55413b75.jsonl`. Input 66, cache read 114,659, cache write 75,485; output unmeasured.

## So what

This record replaces, for the Fable table, the write-up window the run's own observation recorded, and it carries no unpriced share: the check is the whole of what Fable spent on this run, except for the output tokens no tool can read. The G1 dissent is the second time today the two checkers split on a right-mechanism, unreachable-consequence finding, and the first time Fable was the stricter one.
