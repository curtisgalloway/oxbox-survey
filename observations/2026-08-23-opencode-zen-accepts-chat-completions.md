<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-08-23
venue: opencode
model: "-"
kind: access
source: probe
agent: claude-opus-5
---

# OpenCode Zen accepts /chat/completions, despite the docs advertising /responses

**What happened** — the Zen docs list `/zen/v1/responses` (OpenAI Responses API)
and `/zen/v1/messages` (Anthropic-shaped) as the endpoints, which implied oxbox
would need a new request shape rather than just a new base URL. It does not:
`/zen/v1/chat/completions` works.

## Evidence

Three free models, standard chat-completions payload, `Authorization: Bearer`:

```
POST https://opencode.ai/zen/v1/chat/completions
{"model": "<id>", "max_tokens": 512, "messages": [{"role":"user","content":"Reply with exactly: OK"}]}

x-preview-f-free         200  content='OK'  completion_tokens=36
nemotron-3-ultra-free    200  content='OK'  completion_tokens=30
mimo-v2.5-free           200  content='OK'  completion_tokens=75
```

An earlier unauthenticated probe of the same route returned Cloudflare `403 error
code: 1010` for every path including ones the docs do document, so route
existence cannot be tested without a key — that 403 was bot filtering, not a
routing answer.

## So what

**`ox` needs only a `--base-url`, not a second request shape.** That was the main
cost estimated for widening beyond OpenRouter, and it does not apply to OpenCode.

Not established: whether billing details were required at signup. The key worked
on the first call with no `reject_no_credit` equivalent, unlike
[[2026-08-23-zenmux-free-tier-deposit-gate]] — but the account may already have
had billing attached. Someone who knows should confirm before this is quoted as
"no card required".
