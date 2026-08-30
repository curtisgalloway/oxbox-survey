<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
venue: requesty
base_url: https://router.requesty.ai/v1
catalog: https://router.requesty.ai/v1/models
pricing_class: A
last_verified: 2026-08-24
---

# Requesty

676 models, 12 free, 5 of them free nowhere else `[M]`. Its distinguishing
feature is not the model list — it is that **Requesty publishes data terms as
structured fields**, which is the only place in this survey where the data-terms
axis is Measured rather than read off a terms page.

## Getting in

- **No credit card required** `[R, vendor]`. Requesty's own pricing page states
  "No credit card required" against a free tier of **200 requests/day** covering
  "all free models", with pay-as-you-go beyond that at a 5% markup on provider
  rates. First-party and unambiguous, which is as far as this can be taken
  without inspecting an account.
- **No deposit gate** `[M]`. Free models answered on a minutes-old key with no
  balance requirement — unlike ZenMux, which returns 402 until funded.
  [[../observations/2026-08-23-requesty-chat-completions-no-deposit]]

## API

- **`chat/completions` confirmed working** `[M]`, `Authorization: Bearer`. Three
  free models answered. Reachable as `ox --venue requesty`.
  [[../observations/2026-08-23-requesty-chat-completions-no-deposit]]

## Catalog quirks

- **Pricing is tiered**: a `pricing` array of
  `{prompt_tokens_threshold, input_price, output_price}` rows. A model can be
  free below a threshold and priced above it, so the adapter treats a model as
  free only when **every** tier is zero.
- Capabilities are `supports_*` booleans rather than a parameter list. The
  adapter renames `supports_tool_calling`, `supports_reasoning`, and
  `supports_output_json_object`/`_schema` into the common
  `supported_parameters` vocabulary — a translation of what the venue asserts,
  not an inference about what it supports.
- **`data_used_for_training` and `data_retention_days` are fields** `[M]`.
  Captured into every Requesty snapshot as `trains_on_input` and
  `data_retention_days`. Null elsewhere, because no other venue says.
- No marking for cloaked listings; `is_stealth` is null.

## Notable free entries

`mistral/leanstral-1-5` — 262K context, `trains_on_input: false`,
`data_retention_days: 0` `[M]`. The cleanest data-terms profile in the entire
survey, on a model OpenRouter does not offer free at all. Under the
public-code-only constraint that advantage is smaller than it looks, but it is
the one entry where the data answer is "no" rather than "acceptable".

It also answered the probe prompt in **2 completion tokens**, against 30 for
`z-ai/glm-5.3-free` on the identical prompt `[M]` — no reasoning overhead at
all. Irrelevant under a request-capped tier, 15x under a token-capped one.

Seven of the twelve free entries are NVIDIA Nemotron variants, all
`trains_on_input: true`, retention 30 days `[M]`.
