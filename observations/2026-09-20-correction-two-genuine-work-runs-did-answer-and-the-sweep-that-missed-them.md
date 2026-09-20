<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-20
venue: openrouter
model: "-"
kind: access
source: manual
agent: claude-opus-5
corrects: 2026-09-20-twelve-genuine-work-review-attempts-in-ten-days-and-not-one-reached-a-model.md
---

# Correction: two genuine-work runs did answer, and the sweep that said otherwise was hand-rolled

**What changed** — the claim that not one genuine-work attempt reached a model
is false. Two did, on 2026-09-19, and they produced the first real-work review
output in the record. The count was wrong too: thirteen runs, not twelve. Both
errors come from the same cause, which is the part worth keeping.

## What the record should say

Genuine work in `curtisgalloway/paniolo` and `curtisgalloway/shoephone`,
2026-09-11 to 2026-09-20: **13 runs, 2 answered, 11 failed.**

| run | model | outcome |
|---|---|---|
| paniolo `2026-09-19T02-03-00Z-2` | deepseek-v4-flash via StreamLake | **answered** — `postinstall.sh` + its test, 1,643 in / 2,792 out, $0.00035 |
| paniolo `2026-09-19T02-03-48Z-2` | deepseek-v4-flash via StreamLake | **answered** — release-workflow excerpts, 4,201 in / 4,526 out, $0.00064 |

The first returned "The code is correct. No defects found." with a short
account of what it checked — the ideal answer on clean code, and the first time
this record has one from real work rather than the zero-defect fixture. The
second opened with a finding against an undefined `$HELPERS` in a bottle
verification loop. Neither has been adjudicated; both are adjudicable, and
under the 2026-09-20 rating rule they are the only genuine-work material that
exists.

The eleven failures stand as described: nine at `Filter by Max Price`, one
failover that refused at entry 1 and failed at entry 2, and one 900-second
timeout.

## Why the sweep was wrong

**Same-second collisions.** Both oxbox implementations name a second run
claimed in the same second `<stamp>Z-2` (`docs/log-contract.md`). Every `find`
pattern in the original sweep ended in `Z`, so every `-2` directory was
invisible — and all three answered-or-failover runs on paniolo live in `-2`
directories. The suffix is not an edge case here; it is what a failover
produces, because the second attempt claims a new log directory in the same
second as the first.

**`usagereport.py` already handles this, and I did not use it.** It is stage 6
of the survey cycle, it sweeps `~/src`, it reads exactly these logs, and its
`stamp_to_iso` drops the suffix on purpose with a comment explaining why. The
hand-rolled `find` was written because the tool was not checked for first. Run
it: `./usagereport.py --from 2026-09-11 --to 2026-09-20`.

**A related gap the tool has**, found while reconciling the two: three paniolo
directories — `01-47-58Z`, `02-03-00Z`, `02-03-48Z` — carry `meta.json`,
`request.json` and `error.txt` but **no `status.json`**, and `find_runs` skips
a directory without one. Each has a `-2` sibling that does carry the full
record, so nothing was lost here, but a run that dies before writing status is
invisible to the report rather than counted as a failure. Worth a look before
the sweep is relied on for weekly evidence.

## What also needs correcting

The sibling observation on the deepseek timeout opens by calling it "the only
run in the ten-day window that got past the `max_price` guard." That is
superseded: paniolo's two answered runs also reached entry 2, on 2026-09-19.
The timeout itself, its 900 seconds, its null token counts and its being the
first paid entry to time out on real work are all unchanged.
[[2026-09-20-deepseek-v4-flash-timed-out-at-900-seconds-on-a-real-32kb-review]]

## So what

The uncomfortable conclusion in the original — that the rating rule has an
empty corpus — softens but does not vanish. There are two real-work runs to
adjudicate rather than zero, both from one model on one afternoon on one
project. That is a start and not a week of evidence.

The durable lesson is the other one: a hand-rolled filesystem sweep got the
central fact of an observation wrong, in a repo that already had a tested tool
for that exact question. Check `usagereport.py` first.
