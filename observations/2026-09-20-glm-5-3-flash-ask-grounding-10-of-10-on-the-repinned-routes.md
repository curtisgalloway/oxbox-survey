<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-20
venue: openrouter
model: z-ai/glm-5.3-flash
kind: findings
source: oxbox-run
agent: claude-opus-5
corpus: oxbox-ask-grounding-v2
role: candidate
run: 2026-09-20T01-01-29Z
wall_s: 8
hits: 10
hits_of: 10
usd_model: 0.0011
usd_total: 0.0011
---

# glm-5.3-flash answers ask-grounding 10 of 10 on the re-pinned routes, and GMICloud bills the endpoint row to the cent

**What happened** — the first run this model has served since 2026-09-08. The
re-pinned entry routes, the fixture scores 10 of 10 at the v2 parameters, and
the amount billed equals the price the endpoints API quotes for the route that
served it, to eight decimal places.

## Evidence

The pin, as `meta.json` recorded it — `max_price` from the endpoints API rather
than the model's list row, and `siliconflow/fp8` dropped from `only`:

```json
"provider": {"only": ["z-ai/fp8", "gmicloud/fp8", "streamlake/fp8"],
             "allow_fallbacks": false,
             "max_price": {"prompt": 0.15, "completion": 0.5}}
```

```
oxbox-send: venue=openrouter model=z-ai/glm-5.3-flash mode=ask effort=medium context=39467B files=1
oxbox-send: finish=stop prompt_tokens=9476 completion_tokens=392 reasoning_chars=0 route=GMICloud
```

Scored by `corpora/scorers/ask_grounding.py`, which executes the pinned `ox`:

```
RESULT  PASS  (8 scored mechanically correct, 2 for a reader)
```

q2 and q7 are the two the scorer hands to a reader because they need an HTTP
exchange it will not fake. Both were read against `6072d56:ox` and both are
correct: q2 names `NoRedirects.redirect_request` returning `None` (class at
line 114, opener built with it at 423) and says the `Authorization` header is
never re-sent; q7 says the run exits with the provider's message and does not
try a second entry, which is `if not args.failover: sys.exit(str(failure))` at
line 801. That is 10 of 10.

**The billed figure against the endpoints API.** GMICloud quotes
$0.105/$0.35 per M. The run sent 9,476 prompt tokens and took 392 completion
tokens back:

```
expected from endpoints API: 0.00113218
billed by OpenRouter:        0.00113218   (status.json venue_cost)
```

## So what

Two things, and the second is the reason to keep this row.

The model is fine. Its previous rating stands on its own runs, and the eight
days it spent unreachable were a pricing pin, not the model — this run is the
`findings` row that clears `price_filtered` and says so with a measurement
rather than an argument.

And the per-endpoint price is exact. The whole failure of the 2026-09-10 pin
was `max_price` set from a list row that no route charges; the fix is to set it
from the endpoints API, and this run is the check that the endpoints API is the
thing a bill can be predicted from. One route, one run — but an exact match at
eight decimals is not a coincidence, and it is the first time this survey has
tied a pinned number to a billed one.

## Cost

$0.0011 for the model's half. The checking half is this agent's session, which
carries no costcheck window: the scorer is mechanical and the two reader
questions were settled by reading four line ranges of the pinned file.
