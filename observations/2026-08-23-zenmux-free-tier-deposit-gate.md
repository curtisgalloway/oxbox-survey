<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-08-23
venue: zenmux
model: "-"
kind: access
source: probe
agent: claude-opus-5
---

# ZenMux free models are gated on a funded account, not on spending

**What happened** — a model the catalog prices at zero returned `402
reject_no_credit` on an unfunded account. The same key against the same model
returned `200` after any balance was added. No credits are deducted by the call.

## Evidence

Before funding:

```
POST https://zenmux.ai/api/v1/chat/completions
{"model":"z-ai/glm-5.3-free","max_tokens":32,"messages":[{"role":"user","content":"Reply with exactly: OK"}]}

HTTP 402
{"code": "402", "type": "reject_no_credit",
 "message": "Welcome to try this free model. To prevent abuse, your account must
             have a balance greater than $0 — no credits will be deducted when using it."}
```

After funding, identical request:

```
HTTP 200
model: z-ai/glm-5.3-free   finish_reason: stop   content: 'OK'
```

The failure was `402`, not `401` — the key authenticated in both cases. This is
an account-balance gate, not an auth problem.

## So what

The snapshot's free predicate measures **price**, not **access**, and this is the
first measured case of the two diverging. `zenmux/z-ai/glm-5.3-free` would have
appeared in a catalog table as free and unqualified while being uncallable.

Three separate gates exist and `oxsurvey` currently tests only the first:

1. priced at zero — what the catalog reports
2. callable at all — this observation
3. callable right now — see [[2026-08-23-openrouter-free-pool-saturated]]

Structurally this is the same arrangement as OpenRouter's $10-for-1000-req/day: a
platform-level deposit that unlocks free usage without per-model commitment. Two
venues out of two follow the pattern, which suggests the catalog table needs an
"access" column sourced from a probe rather than from pricing.
