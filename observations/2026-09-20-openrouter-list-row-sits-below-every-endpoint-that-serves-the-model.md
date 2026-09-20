<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-20
venue: openrouter
model: "-"
kind: card-contradiction
source: probe
agent: claude-opus-5
---

# OpenRouter's list row can sit below every endpoint that serves the model, which makes a max_price set from it match nothing

**What happened** — the catalog row this survey has been pinning `max_price`
from is not the price of any route. For `z-ai/glm-5.3-flash` it is below all 29
endpoints that serve the model, so a guard at the list row filters every one of
them and the request 404s before it is sent. The same mechanism has been
quietly degrading the second manifest entry, where the guard excludes two of
its three pinned routes instead of the one it names.

## Evidence

`https://openrouter.ai/api/v1/models/<slug>/endpoints` returns a per-provider
price. Against the 2026-09-10 catalog row each manifest entry was pinned from:

| model | catalog row (per M) | cheapest live endpoint | pinned routes, live |
|---|---|---|---|
| `z-ai/glm-5.3-flash` | 0.0700 / 0.2333 | `deepinfra/fp4` 0.0750 / 0.2500 | z-ai 0.15/0.50, gmicloud 0.105/0.35, streamlake 0.141/0.47, siliconflow 0.15/0.50 |
| `deepseek/deepseek-v4-flash` | 0.0886 / 0.1772 | `streamlake/fp8` 0.0372 / 0.0745 | digitalocean 0.098/0.196, streamlake 0.0372/0.0745, novita 0.14/0.28 |

For glm-5.3-flash the row is under the cheapest endpoint, so nothing survives
the filter. Reproduced with the 2026-09-10 pin verbatim:

```
oxbox-send: HTTP 404: {"error":{"message":"No endpoints found that satisfy the
max price for this request","code":404,"metadata":{"routing_funnel":[{"step":
"Initial Endpoints","endpoint_count":29}],"failed_routing_step":
"Filter by Max Price"}}}
```

29 endpoints in, zero out — the same funnel the 2026-09-19 observation recorded,
still reproducing nine days on.

For deepseek-v4-flash the row is above one pinned route and below the other
two, so the entry routes but has been running on StreamLake alone. Probing it
pinned to DigitalOcean at the 2026-09-10 guard:

```
"routing_funnel":[{"step":"Initial Endpoints","endpoint_count":16},
                  {"step":"Filter by Max Price","endpoint_count":3}]
```

Three of sixteen survive the guard, and of the entry's three pinned routes only
StreamLake is among them. The entry's `why` says the guard is there to exclude
Novita until it prices at list; DigitalOcean was never meant to be excluded and
has been, since the day the entry was written.

Both corrected pins were probed and both route — glm-5.3-flash to GMICloud,
deepseek-v4-flash to StreamLake — and the glm run's bill matched GMICloud's
endpoint row exactly.
[[2026-09-20-glm-5-3-flash-ask-grounding-10-of-10-on-the-repinned-routes]]

## So what

`max_price` is a guard against a route billing more than the survey measured,
and it can only do that job if it is set to a number some route actually
charges. The model's list row is not that number.

The 2026-09-20 catalog, taken hours after the rest of this observation, says
what the row is. It moved on both models without either one's endpoints
moving: glm-5.3-flash 0.0700/0.2333 → 0.0900/0.3000, deepseek-v4-flash
0.0886/0.1772 → 0.0372/0.0745. The second is StreamLake's endpoint price to
the digit, and the first is `relace`'s. Counting endpoints at or under the new
row: 3 of 29 for glm-5.3-flash, exactly 1 of 16 for deepseek-v4-flash.

So the row tracks the **cheapest** endpoint, and lags it. A `max_price` set
from it therefore admits at most the cheapest route, and when the row lags a
floor that has risen it admits none — which is the whole of both failures
above, in one sentence. Note that today's row would still break the glm
entry: none of its three pinned routes is among the three at or under
0.0900/0.3000. A list-row guard is not a guard with a stale number in it, it
is the wrong number.

There is a second lesson in the SiliconFlow case. The 2026-09-10 entry kept
SiliconFlow in `only` and relied on `max_price` to exclude it for billing 2x
list. Today SiliconFlow's endpoint row reads 0.15/0.50 — identical to
`z-ai/fp8` — so no price can separate them. An exclusion has to be an
exclusion: drop the provider from `only` and let `max_price` guard prices, not
identities.
