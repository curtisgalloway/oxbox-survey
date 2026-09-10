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
run: 2026-09-10T19-37-18Z
harness_model: claude-opus-5
harness_venue: openrouter
harness_window: 2026-09-10T19:42Z..2026-09-10T19:45Z
harness_seconds: 143
harness_in: 19245
harness_out: 11207
harness_usd: 0.3764
harness_note: metered; one `oxbox send --mode ask --force` request through OpenRouter with the verifier contract (amended 2026-09-06) and the five pinned files at 6302b12, log 2026-09-10T19-42-49Z; harness_usd is the venue_cost OpenRouter billed
---

# Opus 5, metered, checks its own zero-defect control run: OPUS4, OPUS8 and OPUS9 confirmed, six refuted, 38 cents, 143 seconds

**What happened** — The Opus 5 half of the metered pair on the Opus 5
baseline clean-control run (`2026-09-10T19-37-18Z`, nine findings): the
verifier contract, the nine findings as a JSON batch, and the five pinned
files, one `--mode ask` request through OpenRouter. 19,245 prompt tokens,
11,207 completion (8,658 reasoning), 143 seconds, $0.3764 billed.

Verdicts: OPUS1 REFUTED on the ordering premise ("/etc/shadow is appended
last, and not at all on macOS"); OPUS2, 3, 5, 6, 7 REFUTED with the
launcher lines that block each; OPUS4 CONFIRMED as the check-cannot-fail
case on both platforms; OPUS8 CONFIRMED under the same exception, with the
concession that "no such variable actually crosses" at this pin and "an
empty-valued key leaks no secret material"; OPUS9 CONFIRMED, "limited /
safe-direction". Against Fable 5.1's check of the same batch it agrees on
seven of nine and differs on OPUS8, which Fable refuted. The record holds
OPUS1 real on the state being producible, OPUS8 invented with Fable, and
OPUS9 benign; see the run's own observation.

## Evidence

Log `logs/2026-09-10T19-42-49Z`, `venue_cost` 0.3764, `finish_reason` stop,
context 36,731 B, sent with `--force` for the two fixture strings in
`guardtest.py`. Verdicts as returned, in `content.md`.

## So what

A model checking its own review confirmed three of its nine findings and
refuted six, which is the record's own count to within one. Self-checking
did not flatter the run. It cost more than the run did.
