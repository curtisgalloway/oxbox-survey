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
checkers: claude-opus-5
run: 2026-09-08T01-49-14Z-2
harness_model: claude-opus-5
harness_venue: openrouter
harness_window: 2026-09-08T02:01Z..2026-09-08T02:04Z
harness_seconds: 130
harness_in: 18603
harness_out: 10587
harness_usd: 0.3577
harness_note: metered; one `oxbox send --mode ask --force` request through OpenRouter with the verifier contract (amended 2026-09-06) and the five pinned files at 6302b12, log 2026-09-08T02-01-21Z; harness_usd is the venue_cost OpenRouter billed
---

# Opus 5, metered, checks gpt-oss-120b's pinned zero-defect control run: twelve findings, eleven refuted and O3 confirmed

**What happened** — The Opus 5 half of the metered pair on gpt-oss-120b's pinned
zero-defect control run (`2026-09-08T01-49-14Z-2`, twelve findings): the
verifier contract as amended on 2026-09-06, the twelve findings as a JSON
batch, and the five pinned files at `6302b12`, one `--mode ask` request
through OpenRouter. 18,603 prompt tokens, 10,587 completion (7,512 reasoning), 130
seconds, $0.3577 billed. The largest batch a checker has read on this fixture.

Eleven REFUTED and O3 CONFIRMED: for every `expect_blocked=True` probe any exception whatsoever is recorded as containment, so a PASS does not depend on the jail, which is the case the amended contract names.

## Evidence

Log `logs/2026-09-08T02-01-21Z`, `venue_cost` 0.3577, `finish_reason` stop, sent with `--force`
for the two fixture strings in `guardtest.py`. Verdicts as returned, in
`content.md`.

## So what

Eleven of twelve verdicts agree across the two checkers, all refutations,
each naming the launcher-set state that makes the scenario unreachable. The
one split is the G1 shape again, and it splits the way G1 first did: Fable
scores the trigger as written and finds none, Opus scores the check's PASS
as independent of the property. The ruling decides it, not another read.
