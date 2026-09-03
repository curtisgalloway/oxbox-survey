<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-02
venue: openrouter
model: deepseek/deepseek-v4-flash
kind: availability
source: oxbox-run
agent: claude-fable-5-1
corpus: oxbox-secret-scanner-fix
role: baseline
---

# DeepSeek V4 Flash on OpenRouter: 21 minutes 29 seconds for a 5,097-token completion, no error, no truncation

**What happened** — the `oxbox-secret-scanner-fix` baseline run against
`deepseek/deepseek-v4-flash` was started at 02:43:56Z and returned at 03:05:25Z.
`finish_reason` stop, `truncated` false, no retry, no 429, no error. Prompt
10,021 tokens, completion 5,097 of which 4,491 reasoning. The same payload was
answered by four other models the same hour in 35 seconds (GPT-5.6 sol) to
6 minutes 45 seconds (Gemini 3.7 Flash, on 38,609 completion tokens).

## Evidence

Runner log (`run-baselines-2.sh`, serial, one request in flight at a time):

```
=== 2026-09-03T02:43:56Z start deepseek_deepseek-v4-flash-oxbox-secret-scanner-fix
=== 2026-09-03T03:05:25Z exit 0 deepseek_deepseek-v4-flash-oxbox-secret-scanner-fix
ox: log -> /Users/curtisg/src/oxbox/logs/2026-09-03T02-43-57Z
```

`status.json`: `"finish_reason": "stop"`, `"truncated": false`, `"error": null`.
The two DeepSeek runs that followed on the same route took 24 seconds (ask,
1,362 tokens) and 5 minutes 29 seconds (review, 2,400 tokens) — so the second
slow one is not a one-off either, and neither is anywhere near a token count
that explains it.

## So what

The scanner-fix result itself is in its own observation. This one is about the
wall clock: at 4 tokens per second the cheapest route in the baseline set would
consume the whole of a serialised review queue's patience on one call, and ox's
own read timeout is 900 seconds, so a run 40 percent longer than this one would
have been recorded as a network error instead of a result. One evening, one
route, three requests; re-measure before believing it, and if it holds, the
provider page for OpenRouter should say which upstream served it — the run log
does not record that.

No marker: this is a baseline, not a candidate.
