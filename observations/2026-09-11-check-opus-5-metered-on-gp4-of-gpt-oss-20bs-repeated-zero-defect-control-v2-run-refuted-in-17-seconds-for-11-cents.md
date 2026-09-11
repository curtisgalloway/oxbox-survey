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
run: 2026-09-11T02-25-14Z
harness_model: claude-opus-5
harness_venue: openrouter
harness_window: 2026-09-11T02:35Z..2026-09-11T02:36Z
harness_seconds: 17
harness_in: 16484
harness_out: 1223
harness_usd: 0.112995
harness_note: metered; one `oxbox send --mode ask --force` request through OpenRouter with the verifier contract and the five pinned files at 6302b12, carrying only GP4, the finding the pinned cheap refuter confirmed; log 2026-09-11T02-35-38Z; harness_usd is the venue_cost OpenRouter billed; the first frontier read under the checking order decided 2026-09-10
---

# Opus 5, metered, on GP4 of gpt-oss 20B's repeated zero-defect control run: refuted in 17 seconds for 11 cents

**What happened** — The third step of the checking order, run for the
first time: the one finding of the local `gpt-oss:20b` run
`2026-09-11T02-25-14Z` that the cheap refuter confirmed (GP4, the leftover
`jailtest-ok.txt` made read-only from outside), under the verifier contract
with the five pinned files, one `--mode ask` request to
`anthropic/claude-opus-5` through OpenRouter, route Claude Platform on
AWS. 16,484 prompt tokens, 1,223 completion (801 reasoning), 17 seconds,
$0.112995 billed.

Verdict: REFUTED. Evidence cited: `jailtest.py:118-125` (the two probes
open the file for writing, which truncates and rewrites it), the
launcher's env dict forcing `HOME` under the sandbox root, `.gitignore`
ignoring `sandbox/`, guardtest's note that it re-seeds `sandbox/work`, and
`profiles/jail.sb` granting `file-write*` on the work dir. Reason: nothing
in the tree makes the file read-only, so repeated runs are consistent on
both platforms; the stated failure needs an out-of-tree manual chmod inside
a gitignored, re-seeded directory; and even then the consequence is a
spurious FAIL, a false alarm in the safe direction, not a leak reported as
PASS.

## Evidence

Log `logs/2026-09-11T02-35-38Z`: `status.json` `venue_cost` 0.112995,
`prompt_tokens` 16484, `completion_tokens` 1223, `reasoning_tokens` 801,
`finish_reason` stop, `route` "Claude Platform on AWS". The response is a
single JSON object with one entry.

## So what

Eleven cents and seventeen seconds for one finding, against 34 to 41 cents
for batches of five to ten on 2026-09-10. The order's economics are what
they were designed to be: the frontier read is priced by what reaches it,
and on this run one finding did. Its verdict also says what the cheap
refuter missed, which is the contract's own clause: a mechanism that is
real and a scenario the tree cannot produce is refuted, and a check that
takes the scenario as given will confirm too much.
