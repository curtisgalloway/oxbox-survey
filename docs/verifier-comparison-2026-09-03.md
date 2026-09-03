<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

# Verifier comparison, 2026-09-03: Opus 5 against Gemini 3.8 Flash

The method and its compromises are in [decisions.md](decisions.md) under
"Comparing verifiers". This is the result of the first run.

**Not an observation, on purpose.** `observations/` feeds part 2 of each issue,
which is about models the survey recommends or declines to. This is about the
survey's own machinery — the reviewing agent, not a reviewed model — and its
`model:`/`role:` fields have no honest value here. It lives beside the generator
reviews for the same reason those do.

## What was run

The fifteen findings the five 2026-09-02 baselines emitted against
`oxbox-clean-control`, replayed to two arms under
[`corpora/prompts/verify-findings.txt`](../corpora/prompts/verify-findings.txt)
and scored against
[`corpora/answers/oxbox-clean-control-verdicts.json`](../corpora/answers/oxbox-clean-control-verdicts.json).

| arm | model | harness | evidence |
|---|---|---|---|
| opus | `claude-opus-5` | `claude -p`, no tools | inlined, ~41–45 KB |
| gemini | `gemini-3.8-flash-medium` | `agy --print --effort medium`, no tools | identical bytes |

`medium` is Gemini 3.8 Flash's own default effort and the middle rung agy
offers. The run could not have gone through `ox` at any setting: ox's ladder was
`low|high|max` and had no rung for it. That gap is being closed on the oxbox side
(branch `effort-ladder`, unpushed at the time of writing), and this run is the
reason — a real experiment left the audited path because the tool could not
express the setting.

## Result

| arm | scored | correct | missed a real defect | confirmed an invention |
|---|---|---|---|---|
| opus | 15 | 12 | 2 | 1 |
| gemini | 15 | 11 | 3 | 1 |

| id | batch | opus | gemini | key |
|---|---|---|---|---|
| S1 | sonnet-5 | REFUTED | REFUTED | REFUTED |
| S2 | sonnet-5 | REFUTED | REFUTED | REFUTED |
| G1 | gemini-3.7-flash | CONFIRMED | CONFIRMED | CONFIRMED |
| P1 | gpt-5.6-sol | REFUTED | REFUTED | REFUTED |
| **P2** | gpt-5.6-sol | **REFUTED** | **REFUTED** | **CONFIRMED** |
| P3 | gpt-5.6-sol | UNCERTAIN | CONFIRMED | CONFIRMED\|UNCERTAIN |
| P4 | gpt-5.6-sol | REFUTED | REFUTED | REFUTED |
| P5 | gpt-5.6-sol | REFUTED | REFUTED | REFUTED |
| **P6** | gpt-5.6-sol | **CONFIRMED** | REFUTED | REFUTED |
| **P7** | gpt-5.6-sol | REFUTED | **CONFIRMED** | REFUTED |
| P8 | gpt-5.6-sol | REFUTED | REFUTED | REFUTED |
| **L1** | glm-5.3-flash | CONFIRMED | **REFUTED** | CONFIRMED |
| L2 | glm-5.3-flash | REFUTED | REFUTED | REFUTED |
| L3 | glm-5.3-flash | REFUTED | REFUTED | REFUTED |
| **L4** | glm-5.3-flash | **REFUTED** | **REFUTED** | CONFIRMED\|UNCERTAIN |

## One point apart, and the point is not the interesting part

12 against 11 on fifteen rows is not a result. Two things underneath it are.

**The same arm gave the same defect opposite verdicts.** P2 and L1 are one bug —
the network probes record any exception as containment, so on a host with no
route all three pass without exercising the jail. GPT-5.6 sol and GLM-5.3 Flash
found it independently and wrote it up differently. The Opus arm **refuted it as
P2 and confirmed it as L1**, in separate runs, from byte-identical source. Its
L1 reasoning names the right standard — "the same vacuous-pass hazard the module
docstring says it is" — and its P2 reasoning never reaches it. The difference
between the two batches is the candidate's phrasing: GLM's version spells out
`exit 0`, GPT's stops at "all three PASS".

That is worse than being wrong. An arm that misses a defect consistently can be
corrected with a rule; an arm whose verdict depends on how the finding was worded
cannot, and a single run of it cannot be distinguished from a careful one.

**Both arms missed the same two rows.** P2, and L4 (the marker file that is never
removed — true, and negligible, which is a verdict neither arm reached). The two
arms disagreed on four rows in all: on P3 both answers are acceptable, on P7 and
L1 the key sides with Opus, and on P6 it sides with Gemini. So the cheap arm was
not the reckless one — **Opus confirmed an invention that Gemini correctly
refused** — and each arm's single false confirm landed on a different row.

**Gemini's misses were not carelessness either.** Its L1 argument is that "the
consequence of certifying an uncontained jail as contained cannot occur because
oxbox unconditionally denies network egress" — a coherent reading that answers a
narrower question than the one the key asks. The key's ground is the file's own
docstring standard, *passing by not looking*, which is a judgment about intent,
not a fact about the sandbox. Two of the three shared errors are of that kind.

## Cost

Measured for one arm, unmeasurable for the other.

| arm | turns | output | thinking | cache write | cache read |
|---|---|---|---|---|---|
| `claude-opus-5` | 5 | 45,318 | 39,762 | 237,362 | 62,377 |
| `gemini-3.8-flash-medium` | 5 | — | — | — | — |

Opus figures from `costcheck.py --cwd`, over a transcript directory nothing else
writes to, so for once the harness number is not an upper bound polluted by other
work. Computed at OpenRouter list ($5/$25 per million, cache write 1.25x, cache
read 0.1x): **$2.65**, not billed. The same output volume at Gemini 3.8 Flash's
$3.75/M would be $0.17.

**agy publishes no token accounting.** Its transcripts carry `content`,
`thinking` and `status` and no usage fields, so the Gemini arm's half cannot be
reported in tokens at all — only as "inside a subscription". That collides with
the rule in [observations/README.md](../observations/README.md) that a findings
run reports both halves of its cost. If a subscription CLI ever becomes the
standing supervisor, that rule needs re-deciding, not quiet exemption.

## What this does and does not license

It does not license swapping the supervisor. The record it was scored against was
built by Claude agents *with tools and the whole repository*, and both arms here
were toolless on a fixed evidence set — so this measures agreement with a past
judgment under harder conditions, not fitness for the job.

What it does establish is narrower and more useful: on this record the expensive
arm's advantage is one row in fifteen, and its failure mode is worse than the
cheap arm's. Neither should be trusted unsupervised on the finding that mattered
most — both refuted it, and the one that got it right in the other batch got it
right for a reason it could not reproduce.

The next thing worth running is the wording sensitivity directly: put P2 and L1
to the same arm several times, and put each one's text to the other. If a
verifier's verdict moves with the candidate's phrasing, that is a property of the
verification step the survey has never measured, and it applies to the standing
supervisor exactly as much as to a cheap replacement.
