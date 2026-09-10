<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-10
venue: openrouter
model: anthropic/claude-opus-5
kind: access
source: oxbox-run
agent: claude-fable-5-1
corpus: oxbox-secret-scanner-fix
role: baseline
run: 2026-09-10T19-39-16Z
---

# Opus 5 refuses the secret-scanner fix: `content_filter` in three seconds, nothing billed, the same refusal Fable 5.1 gave on 2026-09-06

**What happened** — `oxbox-secret-scanner-fix` (`ox` at `6072d56`, 39,467 B,
`--mode diff`, effort high, 100,000 tokens, temperature 0.2) put to
`anthropic/claude-opus-5` as a frontier baseline for the special edition.
The venue returned no content: `finish_reason` `content_filter`,
`native_finish_reason` `refusal`, and the same usage-policy message Fable 5.1
returned twice on 2026-09-06. No token counts, nothing billed, three seconds.
Not retried: the 2026-09-06 pair showed the trigger is the task text, not a
transient.

## Evidence

Log `logs/2026-09-10T19-39-16Z`, `context_bytes` 39467. From `response.json`:

```
"finish_reason": "content_filter",
"native_finish_reason": "refusal",
"refusal": "This request triggered restrictions on violative cyber content
and was blocked under Anthropic's Usage Policy. To learn more, see
https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback."
```

`status.json`: `ok` false, `venue_cost` null, `prompt_tokens` null.

The same bytes were answered today by `openai/gpt-5.6-terra-pro` and by
`google/gemini-3.8-flash`, and on 2026-09-02 by five other models. The
prompt asks for a regex change to a secret scanner and lists the credential
forms as `<n chars>` placeholders.

## So what

Both Anthropic flagship models on OpenRouter decline this fixture, so the
"all Opus" arm of the comparison has no patch score and a reader who sends a
secret-scanner change to either model through the API should expect the
request to be blocked rather than answered. A cheap model is not the only
one that can return nothing.

No disqualifier: this is a baseline, and the refusal is the model's, not the
venue's.
