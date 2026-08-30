<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-08-23
venue: openrouter
model: stealth/ox-alpha
kind: efficiency
source: oxbox-run
agent: claude-opus-5
---

# Ox Alpha's reasoning is billed against max_tokens, so ox's 32k default truncates a real review

**What happened** — the first review batch spent 122,707 characters of reasoning
and hit the 32,000-token default cap mid-sentence, emitting 4 findings before
`finish_reason=length`. Re-running the identical file set at 100,000 tokens
produced 15 findings and finished cleanly.

## Evidence

Same 4 files (66 KB of `src/devices/usb/drivers/usb-bus`), same prompt, two runs:

```
ox: model=stealth/ox-alpha mode=review effort=high context=66516B files=4
ox: finish=length prompt_tokens=17036 completion_tokens=32000 reasoning_chars=122707
   -> 4 findings, cut off mid-sentence in finding 4
```

```
ox: model=stealth/ox-alpha mode=review effort=high context=66516B files=4  (--max-tokens 100000)
ox: finish=stop
   -> 15 findings
```

Reasoning consumed ~31.3k of the 32k budget; roughly 700 tokens of content
survived. Subsequent batches at 100k, after also asking for at most 4 sentences
per finding:

```
05-dwc2            finish=stop  completion_tokens=8521   reasoning_chars=29176
06-dwc3-core       finish=stop  completion_tokens=11713  reasoning_chars=40527
07-dwc3-endpoints  finish=stop  completion_tokens=23171  reasoning_chars=79214
```

Every batch from that point on finished with `finish=stop`; none truncated.

## So what

`ox`'s `--max-tokens` default is 32000. For this model at `--effort high` that is
not a large-output setting, it is a **broken** one: the reasoning trace is
charged against the same budget, so the default silently converts a review into a
truncated fragment. Nothing in the response says "your budget was spent
thinking" — only `finish_reason=length` and a sentence that stops mid-word.

Two consequences for the survey:

- **The free tier caps *requests*, not tokens.** An under-budgeted call is a
  wasted request, not merely a shorter answer. At 50/day unfunded, truncating a
  review costs 2% of the day's budget to learn nothing.
- **Concision buys budget on both sides.** Adding "at most 4 sentences per
  finding, prefer breadth over depth" to the task text cut reasoning volume
  (122,707 → 29,176-79,214 chars) *and* raised the finding count on the same
  files from 4 to 15. The instruction did not trade depth for coverage; it
  bought both.

Recommended floor for a review run against this model: `--max-tokens 100000`.
Worth considering whether `ox`'s default should rise, or whether it should warn
on `finish_reason=length` rather than printing a truncated answer as if complete.
