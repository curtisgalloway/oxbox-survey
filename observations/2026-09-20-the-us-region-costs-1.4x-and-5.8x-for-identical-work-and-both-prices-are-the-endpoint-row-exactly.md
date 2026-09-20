<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-20
venue: openrouter
model: "-"
kind: efficiency
source: oxbox-run
agent: claude-opus-5
corpus: oxbox-ask-grounding-v2
run: 2026-09-20T16-58-32Z, 2026-09-20T16-58-50Z
wall_s: 31
---

# The US region costs 1.4x and 5.8x for identical work, and both US prices are the endpoint row exactly

**What happened** — the second half of the 2026-09-11 experiment: the same
fixture, the same parameters, the same day, run through both edges on the only
two models that reach the US one. Both scored 10 of 10 both ways. The US runs
cost 1.38x and 5.76x their global counterparts, and both US bills match the
published endpoint row to the last digit.

## Evidence

`oxbox-ask-grounding-v2`, `max_tokens` 8,000, temperature 1.0, effort medium,
`6072d56:ox` in every run. Unpinned, because `--base-url` refuses `--provider`
and the published pins do not survive the region filter in any case.
[[2026-09-20-us-only-routing-keeps-both-paid-entries-and-none-of-the-free-tier-and-breaks-both-published-pins]]

| model | edge | route | out | wall | cost | score |
|---|---|---|---|---|---|---|
| glm-5.3-flash | global | GMICloud | 392 | 8 s | $0.00113218 | 10/10 |
| glm-5.3-flash | **US** | Sail Research | 438 | 15 s | **$0.00155838** | 10/10 |
| deepseek-v4-flash | global | StreamLake | 1,704 | 26 s | $0.00049622 | 10/10 |
| deepseek-v4-flash | **US** | Azure | 1,383 | 31 s | **$0.00285705** | 10/10 |

Prompt tokens were identical within each pair (9,476 and 9,917), no cache hit
on any of the four.

**Both US bills are the endpoint row, exactly:**

```
deepseek US  9917 x $0.21/M + 1383 x $0.56/M   = 0.00285705   billed 0.00285705
glm      US  9476 x $0.1425/M + 438 x $0.475/M = 0.00155838   billed 0.00155838
```

That settles the loose end in the earlier region observation, which could not
reconcile Sail Research's price from a 13-token probe and said so. The probe
was the unreliable measurement; at nine thousand tokens the published
`sail-research/us` row is exact. Four exact matches now, across GMICloud,
StreamLake, Azure and Sail Research — the endpoints API predicts the bill, and
the model's list row still does not.

**Quality.** Both US runs are 10 of 10, adjudicated by hand against
`6072d56:ox` on q2, q7 and q9. One weakness worth naming rather than burying:
deepseek's US q9 leads with "The script sets a timeout of 900 seconds. The
provider may take up to that long to answer", and only then says the script
does not control the provider's speed. Its global answer that morning opened
with "The source does not specify how long a provider takes." Scored correct
under the key's rule — an answer that cites 900 while saying it answers a
different question is correct — but it is the weakest of the four and an
editor who reads it as attributing a latency bound to the provider would be
scoring it differently, not misreading it.

## So what

**The guarantee has a price and it is not uniform.** 1.4x on one entry and
5.8x on the other, for output that scores the same. The spread is the whole
story: it is not a regional surcharge, it is which providers happen to hold a
US deployment. glm keeps a mid-priced route; deepseek loses StreamLake at
0.0372/0.0745 and lands on Azure at 0.21/0.56, and the cheapest paid row in the
survey stops being cheap.

**Latency moves less than money.** 8 to 15 seconds and 26 to 31. Real, and
small beside 5.8x.

**Quality is not measured here, and the table should not be read as saying it
is.** ask-grounding-v2 is the smoke test demoted on 2026-09-08 and saturated
this week — seven models, seven scores of 10 of 10. Four more full marks
means the US routes are not broken. It does not mean Azure reviews like
StreamLake.

## What this is not, and why there are no catalog rows

These runs carry no `role` and become no rows. The record has one `venue`
field, `openrouter`, and filing a US run under it would put a Sail Research
result and a GMICloud result in the same cell with the region visible only in
prose. That is exactly what the 2026-09-11 decision wanted to avoid when it
called for a venue row rather than a flag: the region has to be a fact the
record carries. Until `openrouter-us` exists in oxbox's `VENUES` table, a US
run can be an `efficiency` observation and not a catalog row, and this one is.

## Cost

$0.00441543 for the two US runs, against $0.00162840 for the two global runs
they are compared with. No checking window: the scorer is mechanical and six
reader questions were settled by reading `6072d56:ox`.
