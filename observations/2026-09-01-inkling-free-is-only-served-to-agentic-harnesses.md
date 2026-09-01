<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-01
venue: openrouter
model: thinkingmachines/inkling:free
kind: access
source: probe
agent: claude-fable-5-1
---

# Both Thinking Machines free rows refuse a plain API call: "only available on agentic harnesses"

**What happened** — on the 2026-09-01 tripwire, `thinkingmachines/inkling:free`
and `thinkingmachines/inkling-small:free` each returned `403` to a standard
`chat/completions` request:

```
{"error":{"message":"thinkingmachines/inkling:free is only available on agentic
harnesses. Try plugging it into a coding agent or productivity app listed on
https://openrouter.ai/apps","code":403}}
```

Same body for `inkling-small`, with its own id. Full record:
`snapshots/openrouter/2026-09-01-access.json`.

## Evidence

The catalog rows for both carry `free: true`, a 1M endpoint context, a 262,144
completion cap and a full `supported_parameters` list, and nothing that says the
route is restricted by client. The refusal is an application-level gate: the
free route is served only to requests OpenRouter attributes to a listed app. How
attribution is decided (headers, app registration) was not investigated, and
`ox` sends none of it by design.

## So what

**A free row that `ox` cannot call.** Both models sat in the survey's OpenRouter
table with "no `response_format`" as their only limitation; the limitation that
matters is that the endpoint refuses the survey's client outright. Until `ox`
grows an app attribution, which is a change to what it discloses about itself
and not one to make for a probe, these two rows are unusable for this pipeline
and should be listed that way.

It is also the second kind of gate this survey has found that the catalog does
not carry (the first was ZenMux's funded-account requirement), and unlike that
one it is per-model. The snapshot schema has no field for "who may call this";
the access probe is the only thing that would ever notice.
