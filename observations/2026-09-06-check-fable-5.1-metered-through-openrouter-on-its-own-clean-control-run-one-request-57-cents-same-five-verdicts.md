<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-06
venue: openrouter
model: "-"
kind: efficiency
source: manual
agent: claude-fable-5-1
checkers: claude-fable-5-1
run: 2026-09-06T21-22-57Z
harness_model: claude-fable-5-1
harness_venue: openrouter
harness_window: 2026-09-07T00:10Z..2026-09-07T00:13Z
harness_seconds: 98
harness_in: 17402
harness_out: 7934
harness_usd: 0.57072
harness_note: metered; one `oxbox send --mode ask` request through OpenRouter carrying the same verification instructions and five pinned files the in-harness checker had, log 2026-09-07T00-10-47Z; harness_usd is the venue_cost OpenRouter billed
---

# Fable 5.1, metered through OpenRouter, checks its own clean-control run: one request, 57 cents, the same five verdicts as the in-harness check

**What happened** — The Fable 5.1 half of the metered pair (round 4,
question 3): the five findings Fable 5.1 emitted on `oxbox-clean-control`
(run `2026-09-06T21-22-57Z`), with the same instructions and five files at
`6302b12` the in-harness checkers had, sent to `anthropic/claude-fable-5.1`
through OpenRouter as one `--mode ask` request. 17,402 prompt tokens, 7,934
completion (6,035 reasoning), finish `stop`, 98 seconds, **$0.5707 billed**.

Verdicts: F1 REFUTED, F2 CONFIRMED, F3 CONFIRMED, F4 CONFIRMED, F5
CONFIRMED, identical to the in-harness Fable check of the same batch. On F4
it reads the source the finding said it could not see, settles that
`/etc/shadow` is appended last and that `/etc` is ro-bound, and confirms as a
host-state-dependent, safe-direction failure, which is the record's
position. On F5 it names the offline-network case explicitly as a false
green in the unsafe direction, on both platforms.

## Evidence

Log `logs/2026-09-07T00-10-47Z`, `venue_cost` 0.57072, `finish_reason` stop,
context 36,731 B, five files, sent with `--force` past ox's scanner for the
same two fixture strings in `guardtest.py`.

| checker | how | output tokens | USD | wall clock |
|---|---|---|---|---|
| Fable 5.1 | in-harness subagent, 8 tool calls | 9,744 (derived) | $1.46 at list | 152 s |
| Fable 5.1 | metered, one request | 7,934 | $0.5707 billed | 98 s |
| Opus 5 | in-harness subagent, 8 tool calls | unmeasured | $0.79 floor at list | 343 s |
| Opus 5 | metered, one request | 11,173 | $0.3663 billed | 142 s |

## So what

Same verdicts, a third of the price, two thirds of the time: the in-harness
check pays for cache writes and tool round trips that a single request never
incurs. Across the two metered requests Fable used 29 percent fewer output
tokens than Opus and finished 44 seconds sooner, and still cost 56 percent
more, because its list price is double; the editor's theory that Fable uses
fewer tokens holds and the bill does not follow it. The clean-control
ceiling was set from the in-harness Fable record and stands; a metered
ceiling would be lower, and the manifest should not move on a cheaper way
of asking the same question until the fixture's ceiling rule says which
kind of check it means.
