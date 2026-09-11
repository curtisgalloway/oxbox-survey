<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-11
venue: openrouter
model: "-"
kind: efficiency
source: manual
agent: claude-fable-5-1
checkers: claude-opus-5
run: 2026-09-11T02-49-04Z
harness_model: claude-opus-5
harness_venue: openrouter
harness_window: 2026-09-11T02:53Z..2026-09-11T02:54Z
harness_seconds: 37
harness_in: 16408
harness_out: 2922
harness_usd: 0.15509
harness_note: metered; one `oxbox send --mode ask --force` request through OpenRouter with the verifier contract and the five pinned files at 6302b12, carrying only QC1, the finding the pinned cheap refuter confirmed; log 2026-09-11T02-53-10Z; harness_usd is the venue_cost OpenRouter billed
---

# Opus 5, metered, on QC1 of Qwen3-Coder 30B's zero-defect control run: confirmed in 37 seconds for 16 cents

**What happened** — The frontier read of the checking order for the one
finding the cheap refuter confirmed in the local `qwen3-coder:30b` run
`2026-09-11T02-49-04Z`: QC1, that `probe()` scores any exception as
containment. One `--mode ask` request to `anthropic/claude-opus-5` through
OpenRouter, route Claude Platform on AWS, with the verifier contract and
the five pinned files. 16,408 prompt tokens, 2,922 completion (2,294
reasoning), 37 seconds, $0.15509 billed.

Verdict: CONFIRMED. Evidence: `jailtest.py:48-54`, the `probe` body, and
the three network probe calls with `expect_blocked` defaulting to true.
Reason, shortened: because any exception counts as containment, the three
network probes' PASS does not depend on the jail blocking anything; a host
with no route, a resolver with no DNS, or a 5-second `settimeout` expiry
raises, is caught, and is scored blocked, so an absent jail (a seatbelt
profile without `deny network*`, or the script run outside oxbox) certifies
as contained, the silent false-negative direction. It noted that the
finding's cited line 35 is `IS_ROOT` rather than `probe()`, and that its
wording inverts the detail string, and scored the substance.

## Evidence

Log `logs/2026-09-11T02-53-10Z`: `status.json` `venue_cost` 0.15509,
`prompt_tokens` 16408, `completion_tokens` 2922, `reasoning_tokens` 2294,
`finish_reason` stop, `route` "Claude Platform on AWS". One JSON entry.

## So what

The record's L1, confirmed under the same narrow exception that confirmed
it for GLM-5.3 Flash and GPT-5.6 Sol on 2026-09-02, from a finding a
non-thinking coder model wrote in 21 seconds with the wrong line number.
Sixteen cents for one finding is dearer per finding than the 34 to 41 cents
per batch of the day before, and cheaper per batch, because the order
sent one where it would have sent seven.
