<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
venue: openrouter
base_url: https://openrouter.ai/api/v1
catalog: https://openrouter.ai/api/v1/models
pricing_class: A
last_verified: 2026-09-01
---

# OpenRouter

The venue this survey started with, and still the largest free tier: 21 free
models on 2026-09-01, unchanged since 2026-08-27 `[M]`. The only venue that **marks
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
- **On this survey's account, 8 of the 21 free rows return that same 404** `[M]`
  (2026-09-01 tripwire: `liquid/lfm-2.5-2.6b`, five NVIDIA Nemotron rows, both
  Poolside Laguna rows) while 6 answer. The message names the account's privacy
  settings, not the model, so this is a gate and not evidence that the route is
  unserved; whether looser settings clear it is untested `[?]`.
  [[../observations/2026-09-01-openrouter-eight-free-rows-404-on-this-accounts-data-policy]]
- **Both Thinking Machines free rows refuse plain API calls** `[M]`: `403:
  thinkingmachines/inkling:free is only available on agentic harnesses. Try
  plugging it into a coding agent or productivity app listed on
  https://openrouter.ai/apps`. The catalog carries no field for this gate.
  [[../observations/2026-09-01-inkling-free-is-only-served-to-agentic-harnesses]]

## API

- `chat/completions`. This is the endpoint `oxbox send` binds to the
  `openrouter` venue in its own table; a manifest's `base_url` is documentation
  it cross-checks and never honors.
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
  true, and T9 will never fire on a model with a 2098 date. It did, however, hold
  for the three Nemotron nanos, which left on their published 2026-08-24 `[M]`.
- **A single capture can catch the paid tier mid-change** `[M]`: the 2026-08-30
  archive had 396 rows and 60 under `openai/` against 417/93 three days earlier
  and 419/89 two days later. Diff a paid-tier claim against two captures before
  writing it up.
  [[../observations/2026-09-01-openrouter-paid-catalog-dropped-21-rows-for-one-capture-and-got-them-back]]
- **The stealth page lags the catalog** `[M]`: it still showed Ox Alpha as the
  current stealth model on 2026-09-01, five days after the row left the catalog
  and six after the reveal. The catalog is the source of truth for listings.

## Observed behavior

- Two unrelated free models both returned `429 ... temporarily rate-limited
  upstream` within minutes on a Sunday evening `[M]`. The
  `upstream_provider_shared_pool` failure class from issue 0.1 is **not** specific
  to the stealth tier; the named free tier was equally unusable.
  [[../observations/2026-08-23-openrouter-free-pool-saturated]]
- OpenRouter's own suggested remedy is BYOK — *"add your own key to accumulate
  your rate limits"* — which means holding accounts with each upstream provider.
  That is model-level commitment and out of scope.
- **A model id is a pool of endpoints, and the price is the price of a route.**
  The public listing `GET /api/v1/models/<model>/endpoints` showed fifteen
  endpoints for `deepseek/deepseek-v4-flash` and twenty-three for
  `z-ai/glm-5.3-flash` on 2026-09-06, priced from list to 5x list, with output
  caps from 2,048 to 943,718 tokens and fp4 to bf16 weights, and the default
  routing picks one per request. Seven DeepSeek runs went to three providers and
  six GLM runs to four; one GLM run was billed at double the catalog row, and the
  same DeepSeek payload returned nothing in 33 minutes from one provider and a
  full review in 47 seconds from another `[M]`. The request-body `provider`
  object (`order`, `only`, `allow_fallbacks`, `max_price`, `quantizations`) pins
  a route. **oxbox 1.1.0 (released 2026-09-07) passes it through**: `oxbox send
  --provider '<json>'` and an optional `provider` key on a manifest entry, sent
  verbatim, honored on this venue only and refused elsewhere rather than dropped
  ([oxbox#50](https://github.com/curtisgalloway/oxbox/issues/50), filed
  2026-09-06, shipped in 1.1.0; **requires oxbox >= 1.1.0**). The record has
  been there since 0.7.0: `status.json` and every `attempts` entry carry the
  venue's `provider` verbatim as **`route`**, null when the venue names none,
  and from 1.1.0 `meta.json` carries the pin that was sent as `provider`. Every
  observation on this venue names the `route`; an unpinned run's catalog price
  is a floor, and only a pinned run can tell a model's failure from a route's.
  The first pinned runs were made the day the release shipped `[M]`: the
  DeepSeek clean-control payload to `streamlake/fp8` answered in 151 s (the
  route that returned nothing in 33 minutes the day before), and to
  `digitalocean` was refused 429 twice with `allow_fallbacks: false` — the
  error naming DigitalOcean's shared pool — before answering on the third try,
  five minutes on. A pin trades availability for attribution: a refusal that
  default routing would have hidden becomes visible, and the route that
  answers is the one that was asked for. The survey's manifests carry no
  `provider` until a pin is backed by rated runs (rule in the skill).
  [[../observations/2026-09-07-deepseek-v4-flash-candidate-clean-control-pinned-to-streamlake-one-finding-zero-real-in-151-seconds]]
  [[../observations/2026-09-07-deepseek-v4-flash-pinned-to-digitalocean-refused-429-twice-with-fallbacks-off-the-pin-held]]
  [[../observations/2026-09-06-deepseek-v4-flash-candidate-clean-control-rerun-two-findings-in-47-seconds-from-a-fourth-provider-the-blowout-was-the-route]]

## Watch

Stripe agreed to acquire OpenRouter on 2026-08-19, "subject to customary closing
conditions", expecting to close "in the coming weeks"; no closing had been
reported by 2026-09-01 `[R]`. The announcement promises "same mission, same
name, same product, same roadmap" and says nothing about pricing or the free
tier. The free tier is a subsidy line, and subsidy lines are the first thing a
new owner reprices — trigger T9. Rate limits re-read 2026-09-01: 20/min, 50/day,
1,000/day after a $10 purchase, unchanged `[R]`.
