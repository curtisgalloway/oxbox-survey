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
corpus: oxbox-ask-grounding
role: candidate
run: 2026-09-06T22-46-02Z
wall_s: 37
hits: 10
hits_of: 10
usd_model: 0.0010
usd_total: 0.0010
harness_model: claude-fable-5-1
harness_window: 2026-09-06T23:00Z..2026-09-06T23:03Z
harness_in: 96
harness_out: 9282
harness_cache_read: 2322362
harness_cache_write: 11631
---

# DeepSeek V4 Flash as a candidate on ask-grounding: 10 of 10 in 37 seconds for a tenth of a cent, served by a third provider

**What happened** — `oxbox-ask-grounding` (`ox` at `6072d56`, 39,467 B, `--mode
ask`) put to `deepseek/deepseek-v4-flash` as a candidate, at the editor's
direction that a cheap enough paid model is a candidate (round 3, question
4; this one lists at $0.07 in and $0.14 out per million, the cheapest paid
row in the survey). Ten correct, zero wrong, zero fabricated; the three
unsettled questions declined with the right reason each time. 1,283
completion tokens, 936 reasoning, 37 seconds, $0.00099 billed. OpenRouter
routed the run to StreamLake, a provider the record had not seen for this
model; the 2026-09-02 baseline went elsewhere at the same list price.
Against the fixture's Fable 5.1 ceiling of $0.0276 per hit this is $0.0001
per hit: quality 5, cost 5, speed 4.

Verified by Fable 5.1 against the answer key, every answer cited to the line.

## Evidence

Run `logs/2026-09-06T22-46-02Z`, `context_bytes` 39467, `finish_reason` stop,
`venue_cost` 0.0009865, provider StreamLake.

| # | Answer given | Verdict | Where |
|---|---|---|---|
| 1 | `REQUESTY_API_KEY` | correct | `ox:52` |
| 2 | does not follow; `NoRedirects` raises `HTTPError`, logged to `error.txt`; header never sent to the `Location` host | correct | `ox:114`, `ox:423`, `ox:440–443` |
| 3 | `diff` | correct | `ox:559` |
| 4 | exits with the message quoted | correct | `ox:292–294` |
| 5 | the table URL; `base_url` ignored, warning printed | correct | `ox:338–344` |
| 6 | 400,000 bytes | correct, terse; the `--force` escape is not mentioned and was not asked for | `ox:64`, `ox:195` |
| 7 | exits with the `AttemptFailed` message, does not try the next entry | correct | `ox:801–802`, `ox:823–824` |
| 8 | not settled; no retry logic, no wait or count | correct; absence stated | — |
| 9 | not settled; `TIMEOUT_SECONDS` is a request timeout, not a generation estimate | correct | `ox:65` |
| 10 | not settled; the warning is about logging and sharing, not training | correct | `ox:185–193` |

## So what

Eighth model at 10 of 10; the fixture is saturated. This run is the first
candidate row for the cheapest paid model in the survey and the terseness is
the only thing that distinguishes it: every answer is one sentence, and every
sentence is right. The provider changed between the baseline and this run at
the same list price, which is the same routing fact GLM-5.3 Flash showed on
the clean control, and a reminder that the catalog price is the price of a
route.

The verification half on this fixture is the answer key, so `usd_total`
equals `usd_model`.

## Cost

### Under test

| run | model | mode | context | prompt | completion | reasoning | usd |
|---|---|---|---|---|---|---|---|
| `2026-09-06T22-46-02Z` | `deepseek/deepseek-v4-flash` | ask | 39,467 B | 9,906 | 1,283 | 936 | $0.0009 |

usd is computed from the archived catalog price (2026-09-01.json), not billed: OpenRouter returns the billed figure only when asked, and ox does not ask. Reasoning tokens are inside completion and priced as output.

### Harness

| model | lane | turns | input | output | thinking | cache read | cache write |
|---|---|---|---|---|---|---|---|
| `claude-fable-5-1` | main | 3 | 96 | 9,282 | 2,017 | 2,322,362 | 11,631 |
| **total** | | 3 | 96 | 9,282 | 2,017 | 2,322,362 | 11,631 |

Window: 2026-09-06T23:00:00 .. 2026-09-06T23:03:00 (given).
Turns observed span 2026-09-06T23:00:08 .. 2026-09-06T23:01:28.

**Upper bound.** Anything else the session did in this window is counted here too.

Harness input+output is 0.8x the model's prompt+completion (9,378 vs 11,189); with cache reads it is 208.4x (2,331,740).

The window covers reading the ten answers against the key in the survey session; the run itself was a background job. The verification half on this fixture is the key, so `usd_total` equals `usd_model`.
