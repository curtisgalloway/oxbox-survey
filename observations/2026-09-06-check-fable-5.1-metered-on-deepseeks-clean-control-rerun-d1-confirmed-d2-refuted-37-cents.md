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
run: 2026-09-07T00-06-45Z
harness_model: claude-fable-5-1
harness_venue: openrouter
harness_window: 2026-09-07T00:16Z..2026-09-07T00:18Z
harness_seconds: 49
harness_in: 17610
harness_out: 3806
harness_usd: 0.3664
harness_note: metered; one `oxbox send --mode ask` request through OpenRouter with the verification instructions and the five pinned files, log 2026-09-07T00-16-39Z; harness_usd is the venue_cost OpenRouter billed
---

# Fable 5.1, metered, checks DeepSeek's clean-control re-run: D1 confirmed as a safe-direction failure, D2 refuted, 37 cents, 49 seconds

**What happened** — The Fable 5.1 half of the metered pair on DeepSeek V4
Flash's clean-control re-run (run `2026-09-07T00-06-45Z`): the same two
findings, instructions and five files, one `--mode ask` request to
`anthropic/claude-fable-5.1` through OpenRouter. 17,610 prompt tokens, 3,806
completion (2,964 reasoning), 49 seconds, $0.3664 billed.

D1 CONFIRMED: on Linux with `/etc/shadow` alone in the list the stat
succeeds inside bwrap and jailtest exits 1 on an intact jail, with the note
that the finding mis-attributes the cause (stat needs only search
permission on `/etc`, so it fires at any uid and a root-only guard would
not fix it). The editor's ruling on the identical C3 claim is REFUTED, on
the reproduction: at uid 0 the jail really does expose the shadow file, so
the FAIL is not false, and the record follows the ruling. D2 REFUTED as
written: both backends deny the network unconditionally at this pin.

## Evidence

Log `logs/2026-09-07T00-16-39Z`, `venue_cost` 0.3664, `finish_reason` stop,
context 36,731 B. Sent with `--force` for the two fixture strings in
`guardtest.py`.

## So what

Fable confirms the C3 shape and Opus refutes it, for the third time, each
in the same direction as before. Fable's reading credits a mechanism it
verified from the source and marks the failure safe-direction; the ruling
turns on what the reproduction showed at uid 0, which a reader cannot see.
This is the cheapest and fastest check of the fixture so far, 3,806 output
tokens against 7,934 for the five-finding batch, and it is the one that
sets this row's cost digit as the ceiling checker's record.
