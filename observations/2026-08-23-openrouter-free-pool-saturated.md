<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-08-23
venue: openrouter
model: "-"
kind: availability
source: probe
agent: claude-opus-5
---

# Two different free models, both 429 upstream, same evening

**What happened** — trivial 32-token requests to two unrelated free models both
failed with an upstream rate limit. Sunday evening, PDT. The key authenticated
fine; this was pool contention, not an account problem.

## Evidence

```
z-ai/glm-5.2:free          -> HTTP 429
  "z-ai/glm-5.2:free is temporarily rate-limited upstream. Please retry shortly,
   or add your own key to accumulate your rate limits"
  provider_name: "Decart", is_byok: false

google/gemma-4-31b-it:free -> HTTP 429
  "google/gemma-4-31b-it:free is temporarily rate-limited upstream..."
```

Two calls, two different underlying providers, both refused. No third attempt —
each probe spends one of the 50 requests/day the unfunded tier allows.

## So what

Confirms the `upstream_provider_shared_pool` failure class issue 0.1 documented,
and extends it: it is not specific to the stealth tier. On this evening the
*named* free tier was equally unusable.

Two consequences for the survey:

- **Availability is a property of the hour, not of the model.** A single probe
  cannot distinguish "this model is unreliable" from "the pool was busy at 5pm
  Sunday". Any access column built from probes needs a timestamp and should not
  be read as a durable property.
- **The 50/day unfunded cap makes probing expensive** — 22 models would be 44% of
  a day's budget, before any review runs. Probing is affordable at the 1,000/day
  funded tier and not really affordable below it.

OpenRouter's own suggested remedy in the error text is BYOK — "add your own key
to accumulate your rate limits" — which would mean holding a direct account with
each upstream provider. That is model-level commitment and out of scope.
