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

---

# Second generation: both arms through ox, and the economics

Generation 1 could compare accuracy and not cost, because agy publishes no token
accounting. Both arms were re-run through `ox` against OpenRouter, where the
venue's own usage comes back in `status.json` and `costcheck.py` prices it from
the catalog. `ox` is toolless by construction, so "control tool use" needed no
arranging: there is no tool to control.

Each model runs at its **own** `default_effort` rather than a matched rung --
`google/gemini-3.8-flash` at `medium`, `anthropic/claude-opus-5` at `high` --
because the question is what a supervisor costs to actually run, and a matched
rung would price a setting nobody would choose. `medium` needs ox from the
`effort-ladder` work; every run asserts the level it actually went out at by
reading `meta.json`, not the flag that was passed.

## The correction the arms forced

L4 first accepted `CONFIRMED|UNCERTAIN`. **All four arms refuted it, unanimously,
with the observation's own reasoning.** They were right. "True, negligible" had
been mapped the same way for L4 and P3, and the two are not the same category:
P3's described consequence happens and is merely harmless, while L4's two
described consequences -- a dirtied `git status`, unbounded accumulation -- do not
happen at all. The contract asks whether the described failure occurs, so
`REFUTED` is correct. The key is corrected and carries the correction; scores
below are against the corrected key.

That is the replay design working: an agreement statistic would have buried it,
and the disagreement list is what surfaced it.

## Verdicts

| id | opus | or-opus | gemini | or-gemini | key |
|---|---|---|---|---|---|
| S1 | REFUTED | REFUTED | REFUTED | REFUTED | REFUTED |
| S2 | REFUTED | REFUTED | REFUTED | REFUTED | REFUTED |
| G1 | CONFIRMED | CONFIRMED | CONFIRMED | CONFIRMED | CONFIRMED |
| P1 | REFUTED | REFUTED | REFUTED | **CONFIRMED** | REFUTED |
| **P2** | **REFUTED** | **REFUTED** | **REFUTED** | CONFIRMED | CONFIRMED |
| P3 | UNCERTAIN | UNCERTAIN | CONFIRMED | CONFIRMED | CONFIRMED\|UNCERTAIN |
| P4 | REFUTED | REFUTED | REFUTED | REFUTED | REFUTED |
| P5 | REFUTED | REFUTED | REFUTED | **CONFIRMED** | REFUTED |
| P6 | **CONFIRMED** | **CONFIRMED** | REFUTED | **CONFIRMED** | REFUTED |
| P7 | REFUTED | REFUTED | **CONFIRMED** | **CONFIRMED** | REFUTED |
| P8 | REFUTED | REFUTED | REFUTED | **CONFIRMED** | REFUTED |
| **L1** | CONFIRMED | CONFIRMED | **REFUTED** | CONFIRMED | CONFIRMED |
| L2 | REFUTED | REFUTED | REFUTED | REFUTED | REFUTED |
| L3 | REFUTED | REFUTED | REFUTED | REFUTED | REFUTED |
| L4 | REFUTED | REFUTED | REFUTED | REFUTED | REFUTED |

**Opus is harness-independent.** `opus` (claude -p, source inlined) and `or-opus`
(ox, source as `--files`) returned identical verdicts on all fifteen findings,
across different harnesses, different payload shapes and different tokenizers.
Whatever generation 1 measured, it was not a harness artifact.

**Gemini is not.** The two Gemini arms are the same model at the same effort and
they disagree on six of fifteen, including L1 -- the real defect -- which agy
refuted and ox confirmed.

## The number that answers the question

| arm | confirmed | of which real | precision | real found | recall | usd |
|---|---|---|---|---|---|---|
| or-opus | 3 | 2 | 67% | 2 of 3 | 67% | $1.0946 |
| or-gemini | 9 | 4 | 44% | 3 of 3 | 100% | $0.1938 |

`or-gemini` is the only arm that caught P2 -- and it caught it by confirming six
of the eight findings in that batch. That is not judgment, it is a confirm bias,
and it is the one failure mode that makes a supervisor worthless: the entire job
is filtering inventions out, and an arm that confirms them passes the cost
downstream instead of paying it.

So the cheap supervisor costs **$0.90 less** and hands a human **six more
findings to read**. It is economical only if reading and dismissing a code-review
finding against source is worth less than about **fifteen cents**. It is not --
that is minutes of attention per finding, on exactly the task the supervisor
existed to avoid.

**On this evidence, no.** A 5.6x cheaper supervisor did not make cheap candidates
economical, because the saving is denominated in tokens and the cost it creates
is denominated in human attention, and the second is the expensive one.

## Where the money actually goes

| batch (candidate) | emitted | real | or-opus | or-gemini |
|---|---|---|---|---|
| claude-sonnet-5 | 2 | 0 | $0.2577 | $0.0507 |
| gemini-3.7-flash | 1 | 1 | $0.1671 | $0.0215 |
| gpt-5.6-sol | 8 | 1 | $0.4377 | $0.0733 |
| deepseek-v4-flash | 0 | 0 | $0.0811 | $0.0099 |
| glm-5.3-flash | 4 | 1 | $0.1510 | $0.0383 |

Three things this makes visible that per-run cost never did:

- **Supervision dominates the candidate by two orders of magnitude.** All five
  candidate runs together cost $0.3112. Opus supervision of them cost $1.0946.
  For the two super-cheap candidates alone -- DeepSeek and GLM, $0.0020 combined
  -- Opus supervision was $0.2321, **116x their own cost**. A free model's price
  is noise; the question is only ever what reading its output costs.
- **The floor is the source, not the findings.** Opus answered DeepSeek's *empty*
  batch in **eleven completion tokens** and still cost $0.0811, essentially all
  of it prompt. Supervision is a large fixed cost per batch plus reasoning, so
  batching a candidate's findings into one call is what makes any of this
  affordable; verifying findings one at a time would multiply that floor by the
  finding count.
- **Inventions are billed twice.** GPT-5.6 sol's eight findings, six of them
  inventions, cost Opus $0.4377 to supervise -- 40% of its bill across five
  batches, and **five times what GPT itself cost to run**. An inventive candidate
  is expensive in its own tokens and again in everything spent refuting it. That
  is the multiplier the survey has never priced, and it argues for reporting a
  candidate's invention rate as a cost, not only as a quality signal.

The realized saving is also smaller than the sticker. The price ratio is 6.67x on
both axes; the measured ratio across five batches is **5.6x**, because Gemini
spends more completion tokens reaching a worse answer (39,463 against Opus's
26,615). Cheap models think longer, and about a fifth of the discount goes back.

## Availability

The `or-gemini` GPT batch failed on first attempt: HTTP 502 from Google via
OpenRouter, `"JSON error injected into SSE stream"`, `error_type:
provider_unavailable`, after producing 11,874 characters of reasoning that were
discarded and billed as zero tokens. It succeeded on one retry. One failure in
ten runs is not a rate, but a supervisor is infrastructure, and infrastructure
that drops a request after doing the work is a different proposition from one
that does not.

## What this licenses now

Still not a swap. But the case is stronger than generation 1's and points the
other way: the cheap arm is not merely one row worse, it is **unstable across
harnesses on the finding that mattered** and **biased toward confirming** on the
largest batch. Both properties are invisible in an accuracy score and both are
disqualifying for unsupervised use.

The wording-sensitivity experiment proposed above is now more urgent, not less --
`or-gemini` catching P2 while every other arm missed it is either the phrasing
effect again or a confirm bias, and those two have opposite implications. The
same batch, re-run several times against each arm, separates them.
