<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-20
venue: openrouter
model: z-ai/glm-5.3-flash
kind: efficiency
source: oxbox-run
agent: claude-opus-5
corpus: oxbox-ask-grounding-v2
role: candidate
run: 2026-09-20T01-11-36Z
wall_s: 8
---

# GMICloud cached the repeated prompt and billed it at a rate the catalog row does not carry

**What happened** — the same fixture sent to the same model through the same
route ten minutes apart cost a third as much the second time. OpenRouter
reports 9,472 of 9,476 prompt tokens served from cache. The implicit discount
is real and large, and the rate billed for it is not the one the catalog
publishes.

This run is recorded as `efficiency`, not as a second quality row: it scored
10 of 10 like the first, and one fixture answered twice in ten minutes is one
measurement of quality, not two.

## Evidence

Two runs, `usage` verbatim from each `response.json`:

| | 01-01-29Z | 01-11-36Z |
|---|---|---|
| prompt tokens | 9,476 | 9,476 |
| `cached_tokens` | 0 | **9,472** |
| completion tokens | 392 | 479 |
| prompt cost | $0.00099498 | $0.000199332 |
| completion cost | $0.0001372 | $0.00016765 |
| total | $0.00113218 | $0.000366982 |

The second run produced *more* output and still cost 3.1x less. Backing the
cached rate out of the prompt cost: 4 uncached tokens at GMICloud's
$0.105/M leaves $0.000198912 for 9,472 cached tokens, or **$0.0210 per M** —
exactly one fifth of the prompt price.

The 2026-09-20 catalog row for this model publishes
`input_cache_read: 0.000000014`, which is $0.0140 per M. That is not what was
billed. The route charges 0.2x its own prompt price; the catalog quotes a
figure 1.5x cheaper that no part of this transaction used.

## So what

Same lesson as the pricing pin, in a second place: the catalog row describes
the model, and the bill comes from the route. A cost model built on
`input_cache_read` from the catalog would have under-predicted this run's
prompt cost by a third, in the optimistic direction, which is the direction
that matters for a budget.

It is also a real efficiency finding a reader can use. Repeated review runs
over an unchanged codebase are the common case for this survey's own work, and
on a route with implicit caching the second and later runs cost a fraction of
the first with no flag to set and nothing in the manifest to change. The
survey's cost-per-real-defect figures are all first-run figures, so they are
the pessimistic end of what a repeated batch costs.

Not yet known: how long the cache lives, whether it survives a gap of hours,
and whether the other two routes this entry permits do the same. One route,
one repeat, ten minutes apart.

## Cost

$0.000366982 for the model's half, against $0.00113218 for the identical
request ten minutes earlier. No checking window: the comparison is two
`usage` blocks.
