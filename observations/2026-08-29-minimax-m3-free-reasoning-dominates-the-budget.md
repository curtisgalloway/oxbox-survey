<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-08-29
venue: openrouter
model: minimax/minimax-m3:free
kind: efficiency
source: oxbox-run
agent: claude-opus-5
---

# MiniMax M3 free spends 86–97% of its completion budget on reasoning, and one run's usage does not add up

**What happened** — the two review runs on 2026-08-29 reported reasoning as
almost the whole completion. Neither truncated, because oxbox's default cap is
now 100,000; under the old 32,000 default the larger batch would have been cut
off mid-answer.

## Evidence

From `logs/<run>/response.json`, the `usage` block as OpenRouter returned it:

```
2026-08-30T01-11-26Z   prompt 5,668   completion 33,914   reasoning 32,973 (97%)
                       answer text 7,405 chars, reasoning text 129,082 chars
2026-08-30T01-14-28Z   prompt 7,037   completion 18,312   reasoning 15,702 (86%)
                       answer text 9,964 chars, reasoning text 61,610 chars
```

Both runs: `"cost": 0`, `"is_byok": false`, `cached_tokens` 128, and
`"provider": "GMICloud"` — the free MiniMax M3 route was served by GMICloud, which
the catalog row does not say.

## The arithmetic

The second run reconciles: 18,312 − 15,702 = 2,610 tokens for 9,964 characters,
about 3.8 characters per token, which is ordinary for English markdown.

The first does not: 33,914 − 32,973 = 941 tokens for 7,405 characters, about 7.9
characters per token. The reasoning text in the same response runs at 3.9. A
characters-per-token ratio is an estimate and not a tokenizer, so this is a
flag, not a conclusion — but roughly 900 completion tokens appear unaccounted
for in that one response.

## So what

Budget this model against reasoning, not against the answer. A review that
returns 7KB of findings can spend 34,000 completion tokens getting there, and the
free tier is capped on requests rather than tokens, so the cost of that is
latency and cap headroom rather than money. It also means `max_completion_tokens`
in the catalog is a much weaker guide to "will my review fit" than it looks:
what fits is the answer, what fills the budget is the thinking.

Second: the served provider is worth recording per run. "OpenRouter" is the
router, not the party that saw the code.
