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
run: 2026-09-10T19-37-06Z
harness_model: claude-opus-5
harness_venue: openrouter
harness_window: 2026-09-10T19:46Z..2026-09-10T19:47Z
harness_seconds: 62
harness_in: 16960
harness_out: 4521
harness_usd: 0.197825
harness_note: metered; one `oxbox send --mode ask --force` request through OpenRouter with the verifier contract (amended 2026-09-06) and the five pinned files at 6302b12, log 2026-09-10T19-46-04Z; harness_usd is the venue_cost OpenRouter billed
---

# Opus 5, metered, checks Gemini 3.8 Flash's zero-defect control run: GFL1 confirmed, GFL2 refuted, 20 cents, 62 seconds

**What happened** — The Opus 5 half of the metered pair on Gemini 3.8
Flash's baseline clean-control run (`2026-09-10T19-37-06Z`, two findings):
the verifier contract, the two findings as a JSON batch, and the five
pinned files, one `--mode ask` request through OpenRouter. 16,960 prompt
tokens, 4,521 completion (3,587 reasoning), 62 seconds, $0.1978 billed.

GFL1 CONFIRMED, Linux only: `/etc` is ro-bound into the bubblewrap jail, so
`os.stat("/etc/shadow")` succeeds and the oracle records a FAIL "despite
intact containment"; reachable on "a minimal container/CI home" with none
of the home-relative paths and no `.env`; the finding's "sorted first"
clause is wrong and the failure is in the safe direction. GFL2 REFUTED: the
launcher replaces the environment wholesale on both backends, so no parent
variable reaches the jail, and a non-empty leaked key would still trip the
check. Fable 5.1's check of the same batch reached the same two verdicts
with the same reasons.

## Evidence

Log `logs/2026-09-10T19-46-04Z`, `venue_cost` 0.197825, `finish_reason`
stop, context 36,731 B, sent with `--force` for the two fixture strings in
`guardtest.py`. Verdicts as returned, in `content.md`.

## So what

Both checkers confirmed a finding whose stated reason was half wrong,
because its other half named a state the pin produces. That is the reading
the record applied to Opus 5's OPUS1 the same afternoon, where both
checkers went the other way on a finding with only the wrong half.
