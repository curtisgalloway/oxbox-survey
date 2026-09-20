<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-19
venue: openrouter
model: z-ai/glm-5.3-flash
kind: access
source: oxbox-run
agent: claude-opus-5
run: 2026-09-19T01-44-41Z, 2026-09-19T01-44-43Z, 2026-09-19T01-44-53Z
wall_s: 1
answered: false
disqualifier: price_filtered
---

# glm-5.3-flash's max_price guard has matched no endpoint since the issue that set it

**What happened** — three review batches against a real codebase were refused
before a byte was sent. OpenRouter filtered all 29 candidate endpoints out at
the max-price step, so the manifest's first recommendation could not be reached
at all. The same refusal is in the logs from 2026-09-11, the day after the
issue that introduced the guard, and the last run this model actually served
was 2026-09-08 — under the previous issue's price pin.

## Evidence

```
oxbox-send: HTTP 404: {"error":{"message":"No endpoints found that satisfy the
max price for this request","code":404,"metadata":{"routing_funnel":[{"step":
"Initial Endpoints","endpoint_count":29}],"failed_routing_step":
"Filter by Max Price"}}}
```

The pin the runs archived, from entry 1 of the 2026-09-10 issue
(`manifest.sha256 d53048d3b873…`, `entry_position 1`):

```json
"max_price": {"prompt": 0.07, "completion": 0.2333}
"provider": {"only": ["z-ai/fp8", "gmicloud/fp8", "streamlake/fp8", "siliconflow/fp8"]}
```

That is exactly what the issue's own note says it did: *"z-ai/glm-5.3-flash's
list price on OpenRouter fell to $0.07/$0.2333 per M in the 2026-09-10 catalog,
and its max_price guard follows the new list so a route still billing the old
price is skipped."*

Run history for this model in one project's `logs/`, oldest first:

| run | outcome |
|---|---|
| 2026-09-08T00-32-12Z | ok |
| 2026-09-11T00-31-56Z | 404, Filter by Max Price |
| 2026-09-11T00-32-00Z | 404, Filter by Max Price |
| 2026-09-19T01-44-41Z / -43Z / -53Z | 404, Filter by Max Price |

The failure is instant and deterministic: one attempt, ~1 s wall, and
`oxreview.py` classifies it "the run failed for a reason retrying will not
change" rather than queueing a retry. Re-running the same batches with
`--failover` moved them to entry 2 (`deepseek/deepseek-v4-flash`,
`max_price` 0.0886/0.1772), which routed.

## So what

The guard was set to the new, lower list price on the assumption that the
routes would price at list and only stragglers would be skipped. No route has
priced at or below it since, so entry 1 has been unroutable for the entire life
of the issue — eight days — and every run that did not pass `--failover` failed
outright. That is worth separating from a model verdict: nothing here says
glm-5.3-flash got worse, and the model never saw a single one of these requests.
It is a pricing-pin observation about the manifest, and the catalog should read
it that way. The practical effect on a consumer is that the survey's *first*
recommendation is the one that cannot be used, so a caller who follows the
manifest in order and does not opt into failover gets no review at all.

Two things would each have caught it before it reached a user: a routability
check on each entry at issue time, and a max_price set from what routes
actually bill rather than from the catalog's list row, which the 2026-09-10
note shows was already known to differ for two providers on this very entry.
