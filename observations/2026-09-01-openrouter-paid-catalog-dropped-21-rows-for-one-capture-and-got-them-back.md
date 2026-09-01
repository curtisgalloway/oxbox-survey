<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-01
venue: openrouter
model: "-"
kind: availability
source: manual
agent: claude-fable-5-1
---

# The OpenRouter catalog lost 21 rows, 33 of them under `openai/`, for one capture, and had most of them back two days later

**What happened** — the archived raw catalogs (`catalogs/openrouter/`) show the
paid tier shrinking sharply between the 2026-08-27 and 2026-08-30 captures and
recovering by 2026-09-01. A draft edition written from the 08-30 capture reported
"OpenRouter dropped every OpenAI batch route" as a landscape change. It was a
snapshot of a transient state.

## Evidence

Row counts from the three archives, `payload.data` length and `id` prefixes:

```
capture       rows   openai/   openai :batch   all :batch
2026-08-27     417       93          35             60
2026-08-30     396       60           2             41
2026-09-01     419       89          31             65
```

Net change 2026-08-27 to 2026-09-01: 16 rows added, 14 removed. Of the `openai/`
batch routes, six are gone for good (`o1`, `o1-pro`, `o3-mini-high`, `o3-pro`,
`o4-mini-high`, `gpt-5-codex`, all `:batch`) and two open-weights ones were added
(`gpt-oss-120b`, `gpt-oss-20b`). Twelve `:batch` routes were added for other
vendors, four non-batch rows arrived (`anthropic/claude-fable-5.1`,
`ibm-granite/granite-4.2-8b`, `inception/mercury-2.5-preview`,
`tencent/hy4-preview`), and seven left, three of them Anthropic `-fast` variants.
The free tier was identical across all three captures.

## So what

**A single capture can catch a catalog mid-change, and a diff against it reports
the change as a fact.** The 08-30 draft's paragraph was accurate about the two
captures it compared and wrong about the world; the user's margin note on it,
"time will tell if this is a typical shifting of models", was the right reading.
Two rules follow for the survey:

- A churn claim about anything outside the free tier needs to survive a second
  capture before it is written up as landscape. The free tier is diffed
  mechanically and is small enough to eyeball; the paid tier is neither.
- The catalog archive is what made this checkable at all. Without the 08-27 and
  09-01 payloads there would be no way to know the 08-30 drop reversed.

Whether the 08-30 state was a provider-side outage, a rollout, or a deliberate
change that was undone is unknown, and the survey has no evidence to say.
