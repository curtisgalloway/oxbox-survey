<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-07
venue: openrouter
model: deepseek/deepseek-v4-flash
kind: availability
source: oxbox-run
agent: claude-fable-5-1
corpus: oxbox-clean-control
run: 2026-09-07T21-39-43Z, 2026-09-07T21-42-36Z
disqualifier: rate_limited
---

# DeepSeek V4 Flash pinned to DigitalOcean: refused 429 twice with fallbacks off, and the pin held instead of routing elsewhere

**What happened** — The first two attempts to send the `oxbox-clean-control`
payload to `deepseek/deepseek-v4-flash` with `provider: {"only":
["digitalocean"], "allow_fallbacks": false}` were refused by OpenRouter with
HTTP 429 in the same second they were sent, three minutes apart. The error
names the provider: `"provider_name": "DigitalOcean"`, `"limit_source":
"upstream_provider_shared_pool"`. A third attempt five minutes later was
served by DigitalOcean and answered (see the findings observation of the
same date). The disqualifier this records is cleared by that row and by the
StreamLake row of the same afternoon; it is filed because it is the first
refusal on this venue that can be attributed to a route.

## Evidence

Both refusals, `status.json` `ok: false`, `route: null`, no `response.json`,
`error.txt`:

```
429
{"error":{"message":"Provider returned error","code":429,"metadata":{"raw":"deepseek/deepseek-v4-flash is temporarily rate-limited upstream. Please retry shortly, or add your own key to accumulate your rate limits: https://openrouter.ai/settings/integrations","provider_name":"DigitalOcean","is_byok":false,"limit_source":"upstream_provider_shared_pool","remedy_hint":"Retry shortly, add your own provider key (https://openrouter.ai/settings/integrations), or route to another provider with provider routing: https://openrouter.ai/docs/features/provider-routing"}}}
```

| run | sent | answer | route |
|---|---|---|---|
| `2026-09-07T21-39-43Z` | 21:39:43Z | 429 in the same second | none; error names DigitalOcean |
| `2026-09-07T21-42-36Z` | 21:42:36Z | 429 in the same second | none; error names DigitalOcean |
| `2026-09-07T21-48-29Z` | 21:48:29Z | answered, 320 s | DigitalOcean |

Meanwhile the same payload pinned to StreamLake, sent at 21:39:41Z, was
answered in 151 seconds; and the endpoints listing at 21:43Z showed
DigitalOcean `status: 0`, `uptime_last_30m` 99.8. The shared-pool limit is
not visible in either signal.

## So what

`allow_fallbacks: false` did what the survey's fill rule wants it to do. With
the default routing, this request would have gone to one of fourteen other
endpoints and the 429 would never have been seen; the 2026-08-23
`upstream_provider_shared_pool` observation could not say *whose* pool was
full, and this one can. The remedy hint OpenRouter attaches — "route to
another provider with provider routing" — is the venue confirming the same
thing from its side: the limit is per provider, and a pin turns a silent
detour into a visible refusal. So a pinned entry in a manifest trades
availability for attribution, and the survey should say so when it publishes
one: probe mode on a pinned entry fails where an unpinned request would have
quietly succeeded somewhere else, at some other price.

The 120-second serial floor measured on the free pool on 2026-08-30 was not
enough here (the second attempt came 173 seconds after the first and was
refused); five minutes was.
