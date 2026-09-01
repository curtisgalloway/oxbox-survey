<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
venue: zenmux
base_url: https://zenmux.ai/api/v1
catalog: https://zenmux.ai/api/v1/models
pricing_class: A
last_verified: 2026-09-01
---

# ZenMux

Multi-vendor gateway. Five free models as of 2026-09-01, and **all five are
unavailable free on OpenRouter** `[M]` — still the highest unique-model yield of
any venue surveyed, and shrinking: eight on 2026-08-24, six on 2026-08-27 after
`z-ai/glm-5.3-free` and `sapiens-ai/agnes-2.0-flash` left, five by 2026-08-30
after `deepseek/deepseek-v4-flash-vision-exp-free`, its largest (1M context,
image input), was delisted with no expiration date ever published `[M]`. None of
the remaining five is above 524K.

## Getting in

- Signup gives **two keys, and they are not interchangeable** `[M]`:
  - **PAYG**, `sk-ai-…` — inference, `POST /api/v1/chat/completions`
  - **Platform**, `sk-mg-…` — management API: usage, billing, key administration
  Using the platform key for inference will not work. Both are in 1Password as
  separate items; `.env.example` names them.
- **Free models require a funded account** `[M]`. An unfunded account gets
  `402 reject_no_credit`: *"your account must have a balance greater than $0 —
  no credits will be deducted when using it."* Any balance clears it, and calls
  genuinely cost nothing after that. Evidence:
  [[../observations/2026-08-23-zenmux-free-tier-deposit-gate]]
- The gate is platform-level, not per-model, so it does not commit you to a
  model. Structurally the same arrangement as OpenRouter's $10-for-1000/day.

## API

- `chat/completions`, standard OpenAI shape, `Authorization: Bearer` `[M]`.
- Rate limits: not documented anywhere found, not probed `[?]`.

## Catalog quirks

- Pricing is nested as `{field: [{value, unit, currency}, …]}` — a **list** per
  field, not a scalar. A naive `float(pricing["prompt"])` yields nothing and
  silently reports zero free models. The adapter in `oxsurvey` handles it.
- Publishes `publish_time` (a listing date) and no expiration field. Do not let
  the start date stand in for an end date.
- **No marking for cloaked listings.** `is_stealth` is null for every ZenMux
  record; spotting a codename here is a judgment call for the issue writer.
- One context figure per model, which is the served one, so there is no
  advertised-vs-endpoint gap to report.

## Observed behavior

- `z-ai/glm-5.3-free` spends 29–30 reasoning tokens on any prompt, and reasoning
  counts against `max_tokens` — an under-budgeted call returns **HTTP 200 with
  empty content and no error** `[M]`.
  [[../observations/2026-08-23-glm-5.3-free-reasoning-token-budget]]

## Why it matters to the survey

`z-ai/glm-5.3-free` was the model community fingerprinting suspected behind Ox
Alpha, and having it free and callable here is what made the attribution
testable by experiment (edition 0.2's matched run). The question closed on
2026-08-26 when Zhipu revealed Ox Alpha as GLM-5.3-Flash, a different sibling,
and the free GLM-5.3 route left this venue in the same window. What ZenMux
still offers the survey is its unique-model yield: nothing free here is free
anywhere else surveyed.
