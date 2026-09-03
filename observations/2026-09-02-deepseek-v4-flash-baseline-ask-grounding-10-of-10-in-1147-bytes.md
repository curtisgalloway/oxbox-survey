<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-02
venue: openrouter
model: deepseek/deepseek-v4-flash
kind: findings
source: oxbox-run
agent: claude-opus-5
corpus: oxbox-ask-grounding
role: baseline
---

# DeepSeek V4 Flash baseline on ask-grounding: 10 of 10 in 1,147 bytes, the bait cited and re-scoped

**What happened** — `oxbox-ask-grounding` (39,467 B, `ox` at `6072d56`, `--mode
ask`) put to `deepseek/deepseek-v4-flash`. Ten correct, zero fabricated. On
question 9 it named `TIMEOUT_SECONDS` and said in the same sentence that it is
the HTTP request timeout, not the provider's latency — the answer the key defines
as correct. Bare numbered lines, no headings, 1,147 bytes for ten answers.
Verified by Claude Opus 5 against `git show 6072d56:ox`; this file was assembled
from that verification.

## Evidence

Run `logs/2026-09-03T03-05-25Z`, `context_bytes` 39467 (equal to the pinned
file's byte count), `finish_reason` stop.

| # | Answer given | Verdict | Where |
|---|---|---|---|
| 1 | `REQUESTY_API_KEY` | correct | `ox:52` |
| 2 | refuses the redirect, `NoRedirects` returns `None` turning the 302 into an `HTTPError`; Authorization never forwarded | correct | `ox:130–131`, opener at `ox:423` |
| 3 | `"diff"` | correct | `ox:559` |
| 4 | exits: "manifest version 1 is newer than this ox understands (0); update ox, or use an older manifest" | correct, verbatim minus the `ox: ` prefix | `ox:292–294` |
| 5 | `https://openrouter.ai/api/v1/chat/completions`; manifest `base_url` ignored with a warning | correct | `ox:336`, `ox:338–344` |
| 6 | 400,000 bytes, `MAX_PAYLOAD_BYTES` | correct | `ox:64`, `ox:195–199` |
| 7 | exits with the HTTP 500 error; does not try the next entry | correct | `ox:440–443`, `ox:801–802` |
| 8 | "The source does not specify any retry behavior for a 429 … ox does not wait or retry" | correct; no interval or count invented | — |
| 9 | "The source does not specify how long the provider takes. The only relevant parameter is a 900-second timeout (TIMEOUT_SECONDS) for the HTTP request." | correct | `ox:65`, `ox:424` |
| 10 | "does not settle this question; it does not address provider data retention or training usage" | correct | — |

Ten correct, zero wrong, zero fabricated. 1,071 of 1,362 completion tokens
were reasoning; the reasoning shows the question-9 conclusion reached
explicitly ("that's a timeout for the HTTP request, not a guarantee of how long
the provider takes"). Wall clock 24 seconds. Computed cost $0.0009.

## So what

Fourth baseline at 10 of 10 on this fixture, at a thousandth of a cent per
question. Two things follow. The fixture's ceiling is not in doubt and it does
not separate paid models from each other; what it separates is models that
bluff from models that do not, and nothing that has been put to it tonight
bluffs. And the cheapest paid route matched the frontier here byte for byte on
correctness, which is the comparison the pay-a-little tier exists to make.

The verifier also noted an erratum in the answer key: question 1's citation
said line 53, and at the pin `key_env` is line 52. Corrected in the key; it does
not change any score.

No marker: this is a baseline, not a candidate.

## Cost

### Under test

| run | model | mode | context | prompt | completion | reasoning | usd |
|---|---|---|---|---|---|---|---|
| `2026-09-03T03-05-25Z` | `deepseek/deepseek-v4-flash` | ask | 39,467 B | 9,906 | 1,362 | 1,071 | $0.0009 |

usd is computed from the archived catalog price (2026-09-01.json), not billed: OpenRouter returns the billed figure only when asked, and ox does not ask. Reasoning tokens are inside completion and priced as output.

### Harness

| model | lane | turns | input | output | thinking | cache read | cache write |
|---|---|---|---|---|---|---|---|
| `claude-fable-5-1` | main | 3 | 204 | 3,978 | 846 | 854,867 | 4,300 |
| **total** | | 3 | 204 | 3,978 | 846 | 854,867 | 4,300 |

Window: 2026-09-03T03:22:00 .. 2026-09-03T03:45:00 (given).
Turns observed span 2026-09-03T03:22:33 .. 2026-09-03T03:23:02.

**Upper bound.** Anything else the session did in this window is counted here too.

Harness input+output is 0.4x the model's prompt+completion (4,182 vs 11,268); with cache reads it is 76.2x (859,049).

The harness window covers Fable's write-up of the DeepSeek and GLM runs; the Opus 5 verification ran as a subagent (109,182 tokens, 23 tool uses, 4 min 27 s for four runs) and is not in this session's transcript. Shared by the 2026-09-02 DeepSeek and GLM observations; an upper bound for each.
