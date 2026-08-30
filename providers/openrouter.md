<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
venue: openrouter
base_url: https://openrouter.ai/api/v1
catalog: https://openrouter.ai/api/v1/models
pricing_class: A
last_verified: 2026-08-23
---

# OpenRouter

The venue this survey started with, and still the largest free tier: 22 free
models, 14 of which exist free nowhere else `[M]`. The only venue that **marks
its own cloaked listings**, via the `stealth/` id prefix — which is why
`is_stealth` is Measured here and null everywhere else.

## Getting in

- No card for the free tier `[R]`.
- Rate limits: 20 req/min; **50 req/day unfunded, 1,000/day after a one-time $10
  credit purchase that never expires** `[R]`. The purchase is platform-level and
  commits you to no model.
- **Some models 404 until account-wide prompt logging is enabled** `[R]` —
  `404: No endpoints available matching your guardrail restrictions and data
  policy`, reproduced across two keys per issue 0.1. This is the toggle that makes
  Ox Alpha resolve, and it is account-wide, not per-model. The same model is
  reachable on OpenCode without it — see [opencode](opencode.md).

## API

- `chat/completions`. This is the endpoint `ox` hardcodes as `API_URL`.
- The catalog paginates via `links.next`; `oxsurvey` follows it with a 20-page
  guard.

## Catalog quirks

- Pricing is per-token strings plus an optional `request` price. A
  request-priced model is not free even at zero per-token, and the adapter
  rejects those.
- Advertised `context_length` and served `top_provider.context_length`
  **routinely disagree** — GLM 5.2 advertises 1M and serves 256K. Always budget
  against the endpoint figure.
- `expiration_date` is present but not trustworthy in isolation:
  `stealth/ox-alpha` carries `2098-12-31` while issue 0.1 states the free window
  closes around Aug 27. The field records what OpenRouter published, not what is
  true, and T9 will never fire on a model with a 2098 date.

## Observed behavior

- Two unrelated free models both returned `429 ... temporarily rate-limited
  upstream` within minutes on a Sunday evening `[M]`. The
  `upstream_provider_shared_pool` failure class from issue 0.1 is **not** specific
  to the stealth tier; the named free tier was equally unusable.
  [[../observations/2026-08-23-openrouter-free-pool-saturated]]
- OpenRouter's own suggested remedy is BYOK — *"add your own key to accumulate
  your rate limits"* — which means holding accounts with each upstream provider.
  That is model-level commitment and out of scope.

## Watch

Acquisition by Stripe is pending as of issue 0.1. The free tier is a subsidy line,
and subsidy lines are the first thing a new owner reprices — trigger T9.
