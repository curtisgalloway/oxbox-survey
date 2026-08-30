<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-08-23
venue: opencode
model: big-pickle
kind: availability
source: probe
agent: claude-opus-5
---

# big-pickle returns 503 upstream while its sibling free models answer

**What happened** — `big-pickle`, the cloaked listing that motivated adding
OpenCode Zen to the survey at all, is unreachable. Three other free models on the
same venue, same key, same request, answered normally in the same minute.

## Evidence

```
big-pickle             503  {"error":{"type":"server_error","message":
                             "Error from provider (Console): Upstream request failed:
                              Endpoint is unavailable."}}
x-preview-f-free       200  content='OK'
nemotron-3-ultra-free  200  content='OK'
mimo-v2.5-free         200  content='OK'
```

The error names the provider (`Console`) and attributes the failure upstream, so
this is the model's backend, not the gateway and not the key.

## So what

The catalog lists `big-pickle` as free and available; it is neither, right now.
A second measured case of the catalog and reality diverging, and unlike
[[2026-08-23-zenmux-free-tier-deposit-gate]] this one is not fixable by the
account holder.

Whether this is a dead listing or a transient outage is unknown from one probe.
Worth re-checking before it appears in an issue — a cloaked model that 503s is a
`HOLD` at best, and if it stays down it is a delisting the snapshot diff will
never catch, because the catalog entry persists.
