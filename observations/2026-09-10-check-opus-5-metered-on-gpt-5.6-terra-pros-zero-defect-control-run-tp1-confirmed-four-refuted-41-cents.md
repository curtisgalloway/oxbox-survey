<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-10
venue: openrouter
model: "-"
kind: efficiency
source: manual
agent: claude-fable-5-1
checkers: claude-opus-5
run: 2026-09-10T19-37-06Z-2
harness_model: claude-opus-5
harness_venue: openrouter
harness_window: 2026-09-10T19:47Z..2026-09-10T19:49Z
harness_seconds: 167
harness_in: 17222
harness_out: 13150
harness_usd: 0.41486
harness_note: metered; one `oxbox send --mode ask --force` request through OpenRouter with the verifier contract (amended 2026-09-06) and the five pinned files at 6302b12, log 2026-09-10T19-47-06Z; harness_usd is the venue_cost OpenRouter billed
---

# Opus 5, metered, checks GPT-5.6 Terra Pro's zero-defect control run: TP1 confirmed, four refuted, 41 cents, 167 seconds

**What happened** — The Opus 5 half of the metered pair on GPT-5.6 Terra
Pro's baseline clean-control run (`2026-09-10T19-37-06Z-2`, five
findings): the verifier contract, the five findings as a JSON batch, and
the five pinned files, one `--mode ask` request through OpenRouter. 17,222
prompt tokens, 13,150 completion (11,137 reasoning), 167 seconds, $0.4149
billed, the longest and dearest check of the day.

TP1 CONFIRMED as the check-cannot-fail case on both backends. TP2 REFUTED:
"the coverage gap in the oracle is real, but the stated state — stat
denied on one home path while stat is allowed on another home path —
cannot arise here". TP3 and TP4 REFUTED on the launcher always setting the
variable and always replacing the environment. TP5 REFUTED: the write
target is "a disposable, gitignored, oxseed-seeded work dir", nothing
creates the test's reserved filename holding user data or read-only, and
the read-only variant "would additionally only produce a false FAIL".
Fable 5.1's check of the same batch confirmed TP2 and TP5, so the two
disagree on two of five; the record went with these verdicts, see the
run's own observation.

## Evidence

Log `logs/2026-09-10T19-47-06Z`, `venue_cost` 0.41486, `finish_reason`
stop, context 36,731 B, sent with `--force` for the two fixture strings in
`guardtest.py`. Verdicts as returned, in `content.md`.

## So what

The widest checker split of the day, two of five, on the batch whose
inventions each hinge on a state outside the tree. Where the C3 ruling
applies, Opus 5 applied it and Fable 5.1 reached past it, twice.
