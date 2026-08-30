<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
venue: zenmux
base_url: https://zenmux.ai/api/v1
catalog: https://zenmux.ai/api/v1/models
pricing_class: A
last_verified: 2026-08-23
---

# ZenMux

Multi-vendor gateway. Eight free models, and **all eight are unavailable free on
OpenRouter** `[M]` — the highest unique-model yield of any venue surveyed.

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

`z-ai/glm-5.3-free` is the model community fingerprinting suspects is behind Ox
Alpha. Having it free and callable makes the attribution question testable by
experiment — run both over one file and compare — rather than a guess to be
repeated each week. As of 2026-08-23 `ox --venue zenmux` reaches it, so the
experiment is runnable; it needs a review run, not more plumbing.
