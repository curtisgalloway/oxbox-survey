<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-08
venue: openrouter
model: cohere/north-mini-code:free
kind: findings
source: oxbox-run
agent: claude-fable-5-1
corpus: oxbox-clean-control
role: candidate
run: 2026-09-08T01-49-14Z
wall_s: 901
timed_out: true
findings: 0
real: 0
---

# North Mini Code free on the zero-defect control, pinned to Cohere: timed out again at 900 seconds, on its only route

**What happened** — The re-send the editor asked for after this model's
first zero-defect control run timed out: the same payload (`jailtest.py` at
`6302b12`, 6,096 B, review mode, effort high, 100,000 tokens, temperature
0.2) to `cohere/north-mini-code:free` with `provider: {"only": ["cohere"],
"allow_fallbacks": false}`. Cohere is this listing's only endpoint, so the
pin adds attribution rather than choice. No response before oxbox's
900-second read timeout, for the second time in fifty minutes, on the route
that answered the same model's ask-grounding in 25 seconds and its scanner
fix in 243 seconds.

## Evidence

Log `logs/2026-09-08T01-49-14Z`: `request.json` and `meta.json` only
(`meta.json` `provider` `{"only": ["cohere"], "allow_fallbacks": false}`), no
`response.json`; `status.json` `ok` false, `error` "oxbox-send: timed out
after 900s reading the response (global)", `route` null. The endpoints
listing at 01:48Z showed `cohere` with `uptime_last_30m` 97.3.

## So what

Two identical timeouts on a 6 KB review from a model that answers the other
two fixtures in under five minutes, on the one route that serves it. With
the route fixed, what remains is the model on this payload: it reasons past
fifteen minutes on a clean file and does not come back. The row stands as
timed out, speed 0, nothing to score on quality or cost, and the editor now
has the attribution the first row lacked.

## Cost

No response, so no model bill is recorded (the listing is free in any case)
and no checking half.
