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
run: 2026-09-06T21-22-57Z
harness_model: claude-opus-5
harness_window: 2026-09-06T22:46Z..2026-09-06T22:53Z
harness_seconds: 343
harness_in: 12
harness_cache_read: 345900
harness_cache_write: 99363
harness_unpriced: output unmeasured; the Agent tool's total (100,795) minus input and cache writes leaves 1,420, below the visible reply alone, so the derivation used elsewhere does not hold for this transcript
---

# Opus 5 checks Fable's clean-control run: agrees with Fable's checker on four of five, calls F4 uncertain on host state, and its output tokens cannot be derived

**What happened** — The Opus 5 half of the second matched checker pair, on
the five findings Fable 5.1 emitted on `oxbox-clean-control` (run
`2026-09-06T21-22-57Z`). Same instructions and files as the Fable checker of
the same batch. Six model calls, eight tool uses, 343 seconds,
harness-reported 100,795 tokens. Verdicts: F1 REFUTED, F2 CONFIRMED, F3
CONFIRMED, F4 UNCERTAIN, F5 CONFIRMED.

**The output figure is missing on purpose.** On the first pair, the Agent
tool's reported total minus the transcript's input and cache writes left a
residue of the right size for the visible reply plus thinking, and output was
derived from it with that assumption stated. Here the same subtraction leaves
1,420 tokens, and the final JSON alone is longer than that. So the total is
not input plus output plus cache writes, at least not always, and the
derivation is withdrawn for this record: `harness_out` is absent, the priced
window covers input and cache only, and `harness_unpriced` says so. The
same doubt now attaches to the two derived figures in the first pair, which
stay in the record with their notes; the survey has no way to read a
subagent's final output tokens and should say so wherever it quotes one.

## Evidence

Transcript `be37f5ce-2218-4a5c-b328-8de99b76b7a7/subagents/agent-a6927600d76b7fe99.jsonl`.
Input 12, cache read 345,900, cache write 99,363 over six messages.

| id | Opus | Fable's checker | recorded |
|---|---|---|---|
| F1 | REFUTED | REFUTED | invention |
| F2 | CONFIRMED, safe direction, Linux only | CONFIRMED | true, negligible |
| F3 | CONFIRMED, safe direction | CONFIRMED | true, negligible |
| F4 | UNCERTAIN: turns on the host's home contents at run time | CONFIRMED | real |
| F5 | CONFIRMED, both platforms; the standalone run is a false green, not safe-direction | CONFIRMED | real |

On F4 Opus is right that the trigger depends on host state and wrong that
the source cannot settle it: the finding says the state, an empty home, and
the same-day reproduction on dev produced it by pointing `HOME` at an empty
directory. Under the reproduce-first rule that is a CONFIRMED with a
reproduction attached, and a reader of the contract alone could not have
known it. On F5 Opus goes further than the record: a standalone
`python3 jailtest.py` on an offline host exits 0 with no jail at all, which
it calls a false green rather than a safe-direction failure, and that
reading is the stricter one.

## So what

Two checkers now agree on nine of ten verdicts across two batches, with
Opus the dissenter both times and, on the ruled case, the correct one. The
cost tables carry this check under its own row in the Opus table, with the
output share marked missing rather than guessed.
