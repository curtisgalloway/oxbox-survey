<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-06
venue: openrouter
model: deepseek/deepseek-v4-flash
kind: findings
source: oxbox-run
agent: claude-fable-5-1
corpus: oxbox-clean-control
role: candidate
run: 2026-09-06T22-46-39Z
wall_s: 1984
findings: 0
real: 0
usd_model: 0.0160
---

# DeepSeek V4 Flash as a candidate on the clean control: 99,999 of 100,000 completion tokens spent reasoning, no content, 33 minutes, $0.016

**What happened** — `oxbox-clean-control` (`jailtest.py` at `6302b12`, 6,096 B, `--mode review`) put to `deepseek/deepseek-v4-flash` as a candidate. `finish_reason` length: the completion budget of 100,000 tokens was spent, 99,999 of them on reasoning, and the content was empty. 33 minutes wall clock, $0.01597 billed, provider StreamLake. As a baseline four days earlier the same model returned an empty finding list, the fixture's ideal answer, in 5 minutes 29 seconds for $0.0005. This is not that: an empty answer is a decision, an empty content field after the budget runs out is a failure to answer, the mode GLM-5.3 free showed on 2026-08-24 and MiniMax M3 showed once in seven.

Under the rule this is a row with quality unmeasured (no seeded set) and nothing real, not a disqualifier: the venue served the request.

## Evidence

`oxbox-send: finish=length prompt_tokens=1837 completion_tokens=100000 reasoning_chars=488654`; `status.json` `ok` false; `response.json` `usage.cost` 0.0159653, `provider` StreamLake. The reasoning trace is 488,654 characters.

## So what

Two of DeepSeek V4 Flash's four runs on OpenRouter have now gone to a different provider than the catalog's price row names, and the candidate run that went to StreamLake behaved unlike the baseline that did not. The survey cannot tell from one pair whether the route or the day is the difference. Either way, a run that spends the whole budget thinking is a real cost, $0.016 and 33 minutes here, for nothing.

## Cost

### Under test

| run | model | mode | context | prompt | completion | reasoning | usd |
|---|---|---|---|---|---|---|---|
| `2026-09-06T22-46-39Z` | `deepseek/deepseek-v4-flash` | review | 6,096 B | 1,837 | 100,000 | 99,999 | $0.0160 billed ($0.0145 at the catalog price) |

### Harness

| model | lane | turns | input | output | thinking | cache read | cache write |
|---|---|---|---|---|---|---|---|
| `claude-fable-5-1` | main | 2 | 4 | 3,935 | 2,407 | 1,649,530 | 10,588 |

Window: 2026-09-06T23:36:00 .. 2026-09-06T23:42:00 (given). Shared with the scanner-fix observation of the same run set. **Upper bound.** There was nothing to verify; the window is the read of two status records.
