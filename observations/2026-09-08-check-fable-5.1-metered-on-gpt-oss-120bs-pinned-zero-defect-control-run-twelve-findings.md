<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-08
venue: openrouter
model: "-"
kind: efficiency
source: manual
agent: claude-fable-5-1
checkers: claude-fable-5-1
run: 2026-09-08T01-49-14Z-2
harness_model: claude-fable-5-1
harness_venue: openrouter
harness_window: 2026-09-08T02:01Z..2026-09-08T02:04Z
harness_seconds: 118
harness_in: 18605
harness_out: 9685
harness_usd: 0.6703
harness_note: metered; one `oxbox send --mode ask --force` request through OpenRouter with the verifier contract (amended 2026-09-06) and the five pinned files at 6302b12, log 2026-09-08T02-01-21Z-2; harness_usd is the venue_cost OpenRouter billed
---

# Fable 5.1, metered, checks gpt-oss-120b's pinned zero-defect control run: twelve findings, all refuted

**What happened** — The Fable 5.1 half of the metered pair on gpt-oss-120b's pinned
zero-defect control run (`2026-09-08T01-49-14Z-2`, twelve findings): the
verifier contract as amended on 2026-09-06, the twelve findings as a JSON
batch, and the five pinned files at `6302b12`, one `--mode ask` request
through OpenRouter. 18,605 prompt tokens, 9,685 completion (6,853 reasoning), 118
seconds, $0.6703 billed. The largest batch a checker has read on this fixture.

All twelve REFUTED. O3, the `except Exception` finding, refuted because its stated trigger, a programming error in a probe, does not exist at the pin on either platform; the mechanism is credited and the consequence called unreachable.

## Evidence

Log `logs/2026-09-08T02-01-21Z-2`, `venue_cost` 0.6703, `finish_reason` stop, sent with `--force`
for the two fixture strings in `guardtest.py`. Verdicts as returned, in
`content.md`.

## So what

Eleven of twelve verdicts agree across the two checkers, all refutations,
each naming the launcher-set state that makes the scenario unreachable. The
one split is the G1 shape again, and it splits the way G1 first did: Fable
scores the trigger as written and finds none, Opus scores the check's PASS
as independent of the property. The ruling decides it, not another read.
