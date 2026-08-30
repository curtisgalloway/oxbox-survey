<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-08-24
venue: opencode
model: x-preview-f-free
kind: access
source: oxbox-run
agent: claude-opus-5
---

# OpenCode Zen rejects the default urllib User-Agent, so ox could not reach it

**What happened** — the first real `ox --venue opencode` review run failed with
`403 error code: 1010` before reaching a route. `urllib` defaults its
User-Agent to `Python-urllib/3.x`; OpenCode Zen's Cloudflare rejects that.

## Evidence

```
ox: venue=opencode model=x-preview-f-free mode=review context=13207B files=1
ox: HTTP 403: error code: 1010
```

Isolated by sending the same authenticated payload twice, changing only the header:

```
default urllib UA  -> 403 error code: 1010
explicit UA        -> 200 OK
```

Fixed in curtisgalloway/oxbox#3, which sets an explicit `User-Agent`.

## So what

The venue was listed as supported in oxbox#2 and was not reachable at all. The
defect was in the **verification**, not the code: the chat-completions shape was
confirmed on all four venues by a probe script that happened to set its own
User-Agent, while only `zenmux` — on a host that does not filter the header —
was driven end to end through `ox`.

"Verified" covered the API shape and silently did not cover reachability. The
generalisable rule: **a venue is only verified by the client that will actually
call it.** A probe written with different defaults tests a different thing.

Related to [[2026-08-23-opencode-zen-accepts-chat-completions]], which remains
accurate about the route and is the observation that carried the too-broad
implication.
