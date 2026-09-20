<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-20
venue: openrouter
model: "-"
kind: access
source: probe
agent: claude-opus-5
---

# The US edge blocks Python urllib with Cloudflare 1010, and the global edge does not

**What happened** — the first attempt at the region sweep returned `403` for
all 27 models, including the two that a moment earlier had answered `200`
through curl. The body was not an OpenRouter error at all. It was Cloudflare
error 1010, a client-signature block, and it is applied on
`us.openrouter.ai` but not on `openrouter.ai`.

## Evidence

Identical request, identical key, two clients, seconds apart:

```
python3 urllib  -> us.openrouter.ai      403   "error code: 1010"
python3 urllib  -> openrouter.ai         200
curl            -> us.openrouter.ai      200
ureq (rustls)   -> us.openrouter.ai      200 in 840ms
oxbox send      -> us.openrouter.ai      200   (full endpoint URL)
```

Cloudflare 1010 is a browser-integrity refusal based on the client's
signature, not a rate limit and not an authorization failure. The message
carries no OpenRouter error object, no `routing_funnel`, and no model name —
which is how it was mistaken for a blanket 403 on every model until the body
was read.

The whole first sweep of 27 models was invalid and was thrown away. The
numbers in the region observation come from the curl re-run.
[[2026-09-20-us-only-routing-keeps-both-paid-entries-and-none-of-the-free-tier-and-breaks-both-published-pins]]

## So what

**A uniform status code across every model is a tool result, not a finding.**
27 of 27 failing identically should have been read as "the client is refused"
before "the region filter is total", and it was not. The tell was there in
the first line of the body. Recording it because the same shape will recur:
any sweep that returns one status for everything is measuring the sweep.

**It bounds which clients can reach the region endpoints.** curl, ureq and
oxbox all pass; Python's `urllib` does not. That matters directly for `ox`,
the pinned Python reference in this corpus, which builds its requests with
`urllib.request` — it could not talk to the US edge as written. It also means
any quick Python probe script aimed at the region endpoints needs to shell out
to curl or use a client Cloudflare accepts.

**Unknown:** whether a `User-Agent` alone lifts it, or whether the block keys
on the TLS fingerprint. Not chased, because curl settled the measurement that
was actually wanted. Worth ten minutes before anyone writes a Python tool
against these endpoints.
