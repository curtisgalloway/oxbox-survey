<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-08-23
venue: opencode
model: x-preview-f-free
kind: access
source: probe
agent: claude-opus-5
---

# Ox Alpha answers on OpenCode with no prompt-logging toggle

**What happened** — the same model that issue 0.1 documents as requiring
account-wide prompt logging on OpenRouter answered immediately through OpenCode
Zen, on a key minutes old, with no privacy settings touched.

## Evidence

```
POST https://opencode.ai/zen/v1/chat/completions   model=x-preview-f-free
200  content='OK'  completion_tokens=36
```

Issue 1, on the OpenRouter path to the same model:

> `404: No endpoints available matching your guardrail restrictions and data
> policy` — account-wide, reproduced across two keys. Fix is enabling prompt
> logging in OpenRouter privacy settings.

## So what

Two venues front the same cloaked model on materially different terms. The
OpenRouter path costs an account-wide privacy setting; the OpenCode path did not
ask. Under the public-code-only constraint neither is disqualifying, but the
survey should stop treating "Ox Alpha's terms" as one thing — the terms are a
property of the venue, not of the model.

This also means a venue column in the catalog is not cosmetic. The same model at
the same price can be gated differently depending on where it is reached, and the
gate is invisible in either catalog.

Caveat: it was not verified whether the OpenCode account carries billing details,
which could itself be the gate that OpenRouter expresses as a logging toggle. See
[[2026-08-23-opencode-zen-accepts-chat-completions]].
