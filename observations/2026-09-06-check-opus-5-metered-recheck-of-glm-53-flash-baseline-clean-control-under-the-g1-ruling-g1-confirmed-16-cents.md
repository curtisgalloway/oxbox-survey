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
checkers: claude-opus-5
run: 2026-09-03T03-21-05Z
harness_model: claude-opus-5
harness_venue: openrouter
harness_window: 2026-09-07T01:35Z..2026-09-07T01:36Z
harness_seconds: 38
harness_in: 17416
harness_out: 2903
harness_usd: 0.159655
harness_note: metered; one `oxbox send --mode ask` request through OpenRouter carrying the amended verifier contract (the G1 exception, 2026-09-06 night) and the five pinned files, log 2026-09-07T01-35-09Z; the control for the ruling. harness_usd is the venue_cost OpenRouter billed
---

# Opus 5, metered, re-checks GLM-5.3 Flash's baseline clean-control batch under the G1 ruling: G1 confirmed, G2 to G4 refuted, 16 cents, 38 seconds

**What happened** — The control the G1 ruling called for. The four findings
GLM-5.3 Flash emitted on `oxbox-clean-control` as a 2026-09-02 baseline (run
`2026-09-03T03-21-05Z`) were sent to `anthropic/claude-opus-5` through
OpenRouter as one `--mode ask` request, with the verifier contract as amended
tonight (a check whose PASS does not depend on the property it certifies is
CONFIRMED whether or not the property holds today) and the same five files at
`6302b12`. 17,416 prompt tokens, 2,903 completion (1,737 reasoning), 38
seconds, $0.1597 billed.

Verdicts: **G1 CONFIRMED**, naming the exception by its wording ("the check's
PASS does not depend on the property it certifies") and both platforms; G2,
G3, G4 REFUTED, each for the reason the record already holds. The in-harness
Opus check of this batch on 2026-09-06 had confirmed G1 too, so for Opus the
amendment changed nothing; its value is that both checkers now agree (see the
Fable record of the same request).

## Evidence

Log `logs/2026-09-07T01-35-09Z`, `venue_cost` 0.159655, `finish_reason` stop,
context 36,731 B. Sent with `--force` for the two fixture strings in
`guardtest.py`.

| id | Opus 5, in-harness (old contract) | Opus 5, metered (amended) | key |
|---|---|---|---|
| G1 | CONFIRMED | CONFIRMED | CONFIRMED |
| G2 | REFUTED | REFUTED | REFUTED |
| G3 | REFUTED | REFUTED | REFUTED |
| G4 | REFUTED | REFUTED | REFUTED |

## So what

Four of four against the key, for a sixth of a dollar, in under a minute.
This is the cheapest check of the fixture on the record, and it agrees with
the key on every row, including the one the ruling was about.
