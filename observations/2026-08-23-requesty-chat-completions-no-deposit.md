<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-08-23
venue: requesty
model: "-"
kind: access
source: probe
agent: claude-opus-5
---

# Requesty: chat/completions works, no deposit gate, and one model answers in 2 tokens

**What happened** — the venue that had never been probed answered on the first
try. Three free models, standard chat-completions payload, key minutes old, no
funded-account requirement.

## Evidence

```
POST https://router.requesty.ai/v1/chat/completions
{"model": "<id>", "max_tokens": 512, "messages":[{"role":"user","content":"Reply with exactly: OK"}]}

mistral/leanstral-1-5               200  content='OK'  completion_tokens=2
google/gemma-4-31b-it               200  content='OK'  completion_tokens=44
nvidia/nemotron-3-ultra-550b-a55b   200  content='OK'  completion_tokens=25
```

No `402`, no credit gate, unlike
[[2026-08-23-zenmux-free-tier-deposit-gate]].

## So what

Settles four `[?]` markers on `providers/requesty.md` at once: the API shape is
`chat/completions`, the key works without a deposit, free models are callable,
and `ox` needs only a `--base-url` here too.

**The 2-token answer is the interesting number.** The identical prompt cost
`z-ai/glm-5.3-free` 30 completion tokens, nearly all reasoning
([[2026-08-23-glm-5.3-free-reasoning-token-budget]]). Under a request-capped
free tier that difference is nothing; under a *token*-capped one it is 15x. It
is also a reason to keep `leanstral` in mind for the cheap end of a review
pipeline — combined with `trains_on_input: false` and `data_retention_days: 0`,
it has the best data-terms and efficiency profile measured so far.

This is one trivial prompt and says nothing about review quality. `source:
probe` — it cannot justify a `USE`.
