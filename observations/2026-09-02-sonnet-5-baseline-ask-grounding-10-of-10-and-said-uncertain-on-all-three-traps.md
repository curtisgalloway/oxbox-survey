<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-02
venue: openrouter
model: anthropic/claude-sonnet-5
kind: findings
source: oxbox-run
agent: claude-fable-5-1
corpus: oxbox-ask-grounding
role: baseline
---

# Sonnet 5 baseline on ask-grounding: 10 of 10, including "not settled" on all three unsettled questions

**What happened** — `oxbox-ask-grounding` (39,467 B, `ox` at `6072d56`, `--mode
ask`) put to `anthropic/claude-sonnet-5`. Seven answers settled by the source are
correct with the right identifiers and lines; the three that the source does not
settle were each declined explicitly, and question 9's bait — `TIMEOUT_SECONDS =
900` — was named and correctly described as answering a different question.
Fourteen seconds wall clock, 1,236 completion tokens.

## Evidence

Run `logs/2026-09-03T02-26-52Z`, `context_bytes` 39467, `finish_reason` stop.
Scored against `corpora/answers/oxbox-ask-grounding.md`, each claim checked
against `git show 6072d56:ox`:

| # | Answer given | Key | Verdict |
|---|---|---|---|
| 1 | `REQUESTY_API_KEY`, from `VENUES["requesty"]["key_env"]` | line 53 | correct |
| 2 | `NoRedirects.redirect_request` returns `None`, urllib raises `HTTPError`, caught in `send_and_parse`, written to `error.txt`, raised as `AttemptFailed`; the Authorization header is never sent to the new host | lines 114, 130–131; 442–443 | correct, with the mechanism |
| 3 | `"diff"` | `default="diff"` | correct |
| 4 | exits with `manifest version 1 is newer than this ox understands (0); update ox, or use an older manifest` | lines 292–294 | correct, message quoted exactly |
| 5 | `https://openrouter.ai/api/v1/chat/completions` from the `VENUES` table; the manifest `base_url` only draws a stderr WARNING | lines 338–344 | correct |
| 6 | `MAX_PAYLOAD_BYTES = 400_000`, refused without `--force` | lines 64, 195 | correct |
| 7 | `sys.exit(str(failure))` on `AttemptFailed`; the next entry is tried only with `--failover` | line 802 | correct |
| 8 | "The source does not mention any 429-specific retry/backoff logic anywhere … I won't guess a wait time or retry count" | unsettled | correct |
| 9 | "Not stated. The script defines `TIMEOUT_SECONDS = 900` as the client-side timeout … this is not a claim about how long any provider actually takes" | unsettled, baited | correct — the key's own definition of the right answer |
| 10 | "Not addressed anywhere in the source" | unsettled | correct |

Ten correct, zero wrong, zero fabricated. Reasoning tokens 470 of 1,236.

## So what

This is the reference figure the fixture was missing. The survey's stated axis —
a model says UNCERTAIN instead of guessing — now has a ceiling on this fixture,
and the ceiling is 3 of 3 declined, with the trap in question 9 not merely
avoided but identified. A free model that answers question 9 with "900 seconds"
is now measurably behind, rather than merely suspected of bluffing. The cost
side matters too: this was the cheapest of the three Sonnet runs by a factor of
four, because an `ask` with a grounded answer does not need much reasoning.

No marker: this is a baseline, not a candidate.

## Cost

### Under test

| run | model | mode | context | prompt | completion | reasoning | usd |
|---|---|---|---|---|---|---|---|
| `2026-09-03T02-26-52Z` | `anthropic/claude-sonnet-5` | ask | 39,467 B | 14,645 | 1,236 | 470 | $0.0416 |

usd is computed from the archived catalog price (2026-09-01.json), not billed: OpenRouter returns the billed figure only when asked, and ox does not ask. Reasoning tokens are inside completion and priced as output.

### Harness

| model | lane | turns | input | output | thinking | cache read | cache write |
|---|---|---|---|---|---|---|---|
| `claude-fable-5-1` | main | 16 | 3,638 | 37,379 | 12,965 | 2,492,296 | 60,532 |
| **total** | | 16 | 3,638 | 37,379 | 12,965 | 2,492,296 | 60,532 |

Window: 2026-09-03T02:24:00 .. 2026-09-03T02:36:00 (given).
Turns observed span 2026-09-03T02:24:03 .. 2026-09-03T02:32:39.

**Upper bound.** Anything else the session did in this window is counted here too.

Harness input+output is 2.6x the model's prompt+completion (41,017 vs 15,881); with cache reads it is 159.5x (2,533,313).

The harness window covers all three Sonnet runs and their verification, plus the scorer being written; it is shared by the three 2026-09-02 Sonnet observations and is an upper bound for each.
