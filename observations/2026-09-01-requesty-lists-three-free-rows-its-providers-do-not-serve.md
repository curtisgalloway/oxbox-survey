<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-01
venue: requesty
model: "-"
kind: card-contradiction
source: probe
agent: claude-fable-5-1
---

# Requesty lists twelve free rows and its providers refuse to serve three of them

**What happened** — the 2026-09-01 tripwire called all twelve free rows in the
Requesty catalog. Seven answered. Two returned transient upstream errors
(`novita/inclusionai/ling-3.0-tiny` 500, `nvidia/nemotron-3-ultra-550b-a55b`
503 "Service temporarily overloaded"). Three were refused in a way that is not
transient:

```
poolside/laguna-m.1              404  {"error":{"origin":"provider","message":"{\"error\":\"please check the model you provided\"}\n"}}
poolside/laguna-xs.2             404  {"error":{"origin":"provider","message":"{\"error\":\"please check the model you provided\"}\n"}}
nvidia/nemotron-3-nano-30b-a3b   410  {"error":{"origin":"provider","message":"Gone"}}
```

Full record: `snapshots/requesty/2026-09-01-access.json`.

## Evidence

`origin: provider` in each body: Requesty routed the call and the upstream
rejected the model id. The two Poolside rows are also the two whose catalog
record shows `max_completion_tokens: 0` and a 32,768 context, which in hindsight
reads like a placeholder. `nemotron-3-nano-30b-a3b` is the model whose OpenRouter
row expired on its published 2026-08-24 date; Requesty's row has no
`expiration_date` and is still there a week later, answering `410 Gone`.

Of the seven that answered: five scored `correct` on the tripwire,
`mistral/leanstral-1-5` scored `missed` (it named line 4, the line before the
defect: the only miss on any venue today), and `nvidia/nemotron-3.5-content-safety`
returned `User Safety: safe`, a classifier doing its job and `malformed` for a
review prompt.

## So what

**A catalog row is a listing, not a promise the route answers**, and on this
venue a quarter of the free tier is listing only. The survey's Requesty table has
shown "12 free, unchanged" for three editions; the reachable count is 7 to 9
depending on the hour. This is the second capture on which the tripwire has
found free rows whose provider does not know the model (the 2026-08-30 run found
the class too), which is the survey's T6 condition: served behaviour contradicting
the snapshot twice running. The part-1 tables need a reachability column, or a
standing caveat, and the access probe is what fills it.
