<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
venue: opencode
base_url: https://opencode.ai/zen/v1
catalog: https://opencode.ai/zen/v1/models
pricing_class: B
last_verified: 2026-09-01
---

# OpenCode Zen

The confirmed **second venue for cloaked models**. Edition 0.1 already recorded that
Ox Alpha shipped here as `x-preview-f-free` on the same day it appeared on
OpenRouter; `big-pickle` is a codename that has no OpenRouter listing at all.

## Getting in

- Sign in at `https://opencode.ai/auth` with Google or GitHub; the key is on the
  dashboard `[R]`.
- **This survey's account has billing and a $10 deposit** `[M]`, confirmed by the
  account holder 2026-08-26. Every OpenCode probe recorded here was made from a
  funded account, so **none of them tested the cardless path**.
  [[../observations/2026-08-26-opencode-account-carries-billing-and-a-deposit]]
- **Whether free models work without a card is untested and untestable from
  here** `[?]`. It needs a second account with no payment method. The vendor's
  own signup page describes adding a $20 balance (+$1.23 card processing fee,
  auto-replenishing at $5) and never mentions free models `[R, vendor]`; the docs
  say *"sign in, add your billing details, and copy your API key"* `[R, vendor]`;
  third-party write-ups say free-tagged models need no payment details `[R]`.
  Our evidence cannot separate these and must stop being cited as if it could.
- Free tier reportedly 100 requests/day `[R]`.

**Both gateways this survey can speak to were used from funded accounts.** ZenMux
enforces it at call time with `402 reject_no_credit`; OpenCode was never observed
unfunded. "Free" on a gateway has meant "free once you have money on file" every
time it has been checked here — worth saying plainly in any recommendation,
because it is the opposite of how these tiers are marketed.

## API

- Docs advertise `/zen/v1/responses` (OpenAI Responses API) and
  `/zen/v1/messages` (Anthropic-shaped), which implied oxbox would need a second
  request shape.
- **`/zen/v1/chat/completions` works** `[M]`. Three free models answered a
  standard chat-completions payload, so no second request shape was needed.
  Reachable as `ox --venue opencode` since 2026-08-23.
  [[../observations/2026-08-23-opencode-zen-accepts-chat-completions]]
- **Cloudflare rejects the default `Python-urllib` User-Agent** with `403 error
  code: 1010`, before the request reaches any route `[M]`. A client must send an
  explicit `User-Agent` or this venue is simply unreachable — this broke `ox`
  until curtisgalloway/oxbox#3. Same payload, one header changed: default UA →
  403, explicit UA → 200.
  [[../observations/2026-08-24-opencode-cloudflare-blocks-default-urllib-ua]]
- Unauthenticated POSTs are blocked the same way on every path, including
  documented ones `[M]`, so route existence cannot be probed without a key —
  that 403 is bot filtering, not a routing answer.
- The filtering makes this venue the one most likely to look "down" when it is
  merely refusing your client. Check the header before believing an outage.

## Catalog quirks

- **Class B: the roster carries no pricing.** `/models` returns `id`, `object`,
  `created`, `owned_by` and nothing else, so `free` is `null` for every record.
  The whole roster (63 models on 2026-09-01) is snapshotted so churn stays
  diffable. Recent churn: `x-preview-f-free` (Ox Alpha) left 2026-08-27,
  `ling-3.0-flash-fin-free` arrived by 2026-08-30, `hy3-free` left by 2026-09-01
  `[M]`; third-party listings had described `hy3-free` as available "for a
  limited time" `[R]`.
- The `-free` id suffix is **not** a reliable free predicate — `big-pickle` and
  `grok-code` carry no suffix and are free.
- models.dev has OpenCode pricing but is **demonstrably stale**: 20 of the 29
  models it lists as free here are absent from the live roster `[M]`. Use it for
  discovery, never as a source.

## Observed behavior

- `big-pickle` returns `503` from the upstream provider while sibling free models
  answer in the same minute `[M]`. The codename that motivated adding this venue
  is currently unreachable. A cloaked model that 503s is a `HOLD` at best, and if
  it stays down it is a delisting the snapshot diff will never catch, because the
  catalog entry persists.
  [[../observations/2026-08-23-big-pickle-upstream-unavailable]]
- **Ox Alpha answers here with no privacy toggle** `[M]`, where the OpenRouter
  path 404s until account-wide prompt logging is enabled. Same cloaked model, same
  $0, different gate — terms are a property of the venue, not the model.
  [[../observations/2026-08-23-ox-alpha-reachable-on-opencode-without-logging-toggle]]
- **`nemotron-3-ultra-free` completed a real review run** on 2026-08-30 `[M]`:
  27 KB payload, 4,872 completion tokens, 129 s, finish `stop`, no `provider`
  field in the response. 2 of its 10 findings held up; the one serious defect was
  filed UNCERTAIN and a false one filed critical. Reachability and format were
  clean; ranking was not.
  [[../observations/2026-08-30-nemotron-3-ultra-free-2-of-10-findings-real-on-the-exposure-gate]]
