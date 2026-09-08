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
run: 2026-09-08T00-49-36Z
harness_model: claude-opus-5
harness_venue: openrouter
harness_window: 2026-09-08T00:55Z..2026-09-08T00:57Z
harness_seconds: 80
harness_in: 17051
harness_out: 5988
harness_usd: 0.235
harness_note: metered; one `oxbox send --mode ask --force` request through OpenRouter with the verifier contract (amended 2026-09-06) and the five pinned files at 6302b12, log 2026-09-08T00-55-06Z; harness_usd is the venue_cost OpenRouter billed
---

# Opus 5, metered, checks Mistral Small's zero-defect control run: M1 and M2 confirmed as safe-direction failures with the cause wrong, M3 refuted, 23 cents, 80 seconds

**What happened** — The Opus 5 half of the metered pair on Mistral Small 2603's
zero-defect control run (`2026-09-08T00-49-36Z`, three findings): the
verifier contract as amended on 2026-09-06, the three findings as a JSON
batch, and the five pinned files (`jailtest.py`, `oxbox`, `profiles/jail.sb`,
`guardtest.py`, `.gitignore` at `6302b12`), one `--mode ask` request through
OpenRouter. 17,051 prompt tokens, 5,988 completion (4,716 reasoning), 80 seconds, $0.2350
billed.

M1 CONFIRMED: on Linux, a root account with none of the home-relative paths
and no `.env` gives `OXBOX_EXISTING_PATHS` of exactly `/etc/shadow`, the read
probe is skipped, the stat oracle runs on a path that is `--ro-bind`-mounted
into the jail, `os.stat` succeeds and the suite prints FAIL and exits 1; the
checker adds that the stat succeeds at any uid because it needs only search
permission, so the finding's cause is wrong. M2 CONFIRMED on the same
scenario, the guard asymmetry being real in the code. M3 REFUTED: the stat
probe is inside `if EXISTING:`, skipping does not shrink the list, and
`probe()` would swallow an IndexError as a vacuous PASS. The record holds M1
and M2 as inventions under the editor's C3 ruling, because at uid 0 the FAIL
the finding calls false is true.

## Evidence

Log `logs/2026-09-08T00-55-06Z`, `venue_cost` 0.2350, `finish_reason` stop, context 36,731 B,
sent with `--force` for the two fixture strings in `guardtest.py`. Verdicts
as returned, in `content.md`.

## So what

The first batch on this fixture where the two checkers agree on every
verdict, including the direction of the C3 shape: both now say the stated
FAIL occurs and both say the finding misattributes it. That is the amended
contract doing its work, and it leaves the one thing a reader cannot see,
whether the FAIL is false, to the reproduction and the ruling.
