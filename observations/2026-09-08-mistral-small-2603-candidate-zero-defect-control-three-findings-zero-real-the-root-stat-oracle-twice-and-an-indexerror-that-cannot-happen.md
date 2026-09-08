<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-08
venue: openrouter
model: mistralai/mistral-small-2603
kind: findings
source: oxbox-run
agent: claude-fable-5-1
corpus: oxbox-clean-control
role: candidate
run: 2026-09-08T00-49-36Z
wall_s: 45
findings: 3
real: 0
usd_model: 0.0056
usd_total: 0.4063
harness_model: claude-fable-5-1
harness_venue: openrouter
harness_window: 2026-09-08T00:55Z..2026-09-08T00:56Z
harness_seconds: 61
harness_in: 17053
harness_out: 4604
harness_usd: 0.4007
harness_note: metered; one `oxbox send --mode ask --force` request through OpenRouter with the verifier contract and the five pinned files, log 2026-09-08T00-55-06Z-2; usd_total is the model's bill plus this check's; the Opus 5 check of the same batch is its own record
---

# Mistral Small 2603 as a candidate on the zero-defect control: three findings, zero real, the root stat oracle twice and an IndexError that cannot happen

**What happened** — `oxbox-clean-control`, the zero-defect control
(`jailtest.py` at `6302b12`, 6,096 B, review mode, effort high, 100,000
tokens, temperature 0.2), put to `mistralai/mistral-small-2603`. Run as a candidate in the try-next batch the editor approved in round 8 of the rating review (2026-09-07), seven models on the three fixtures, unpinned. Three
findings in 45 seconds, 8,811 completion tokens, 8,602 reasoning, $0.0056
billed, route Mistral.

**M1** and **M2** are the root stat oracle, twice: the `stat_outside` probe
is not skipped for `/etc/shadow` at uid 0, so it "succeeds" and is reported
FAIL "even though the jail is working correctly". This is C3, D1 and
DigitalOcean's F1 in a fourth and fifth wording, and the editor's ruling on
C3 (2026-09-06, on the reproduction) holds: `/etc` is bound into the jail, the
stat succeeds at any uid, and at uid 0 the FAIL is true because root reads
the host's shadow file from inside the jail. The finding's premise, that the
jail is working correctly and the FAIL is spurious, is the false part. Both
metered checkers CONFIRMED the stated FAIL occurs on Linux and both said the
finding's cause is wrong (the stat needs only directory search permission;
uid has nothing to do with it); Opus added that the effect is "a spurious
failure in the safe direction". The record follows the ruling: inventions,
not benign, because the FAIL at uid 0 is not spurious. **M3**, an IndexError
when every path is skipped: REFUTED by both checkers and by reading, since the
stat probe sits inside `if EXISTING:`, skipping is a `continue` that removes
nothing, and `probe()` would swallow an IndexError anyway. Recorded 0 real of
3, 0 benign.

## Evidence

Log `logs/2026-09-08T00-49-36Z`, `finish_reason` stop, prompt 1,832,
completion 8,811, reasoning 8,602, `route` Mistral, `venue_cost` 0.0056.

| id | as stated | Fable 5.1, metered | Opus 5, metered | recorded |
|---|---|---|---|---|
| M1 | root stat of `/etc/shadow` is a false FAIL | CONFIRMED, cause wrong, Linux only | CONFIRMED, safe direction, cause wrong | invention, by the C3 ruling |
| M2 | the read skip has no stat counterpart | CONFIRMED, same scenario | CONFIRMED, same scenario | invention, by the C3 ruling |
| M3 | IndexError on `EXISTING[0]` when all paths skipped | REFUTED | REFUTED | invention |

The two checks are on the record as check records of this run: Fable 5.1
$0.4007 in 61 seconds, Opus 5 $0.2350 in 80 seconds.

## So what

Three findings and all three are the same file's most-invented shape or a
non-event: the fixture did what it was built for. The two checkers agreed
with each other on every verdict for the first time on this fixture, and
where they confirm the stated FAIL they both add that the finding explains
it wrongly, which is the reproduction's finding too. The gap between "the
FAIL happens" and "the FAIL is false" is exactly the C3 ruling, and a
checker that reads cannot close it; the record does.

## Cost

### Under test

| run | model | mode | context | prompt | completion | reasoning | usd |
|---|---|---|---|---|---|---|---|
| `2026-09-08T00-49-36Z` | `mistralai/mistral-small-2603` | review | 6,096 B | 1,832 | 8,811 | 8,602 | $0.0056 billed |

### Checking

Two metered check records, one per checker: Fable 5.1 $0.4007 in 61 seconds,
Opus 5 $0.2350 in 80 seconds. `usd_total` is the model's bill plus Fable's
check, the ceiling checker: $0.4063 for nothing real, so the cost score is
the floor by rule.
