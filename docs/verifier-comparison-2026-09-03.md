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

Scores below are against the **corrected** key — L4 was fixed after generation 2,
see "The correction the arms forced". As first published this section read 12 and
11; the L4 row moved both arms up one and is not a difference between them.

| arm | scored | correct | missed a real defect | confirmed an invention |
|---|---|---|---|---|
| opus | 15 | 13 | 1 | 1 |
| gemini | 15 | 12 | 2 | 1 |

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
| L4 | glm-5.3-flash | REFUTED | REFUTED | REFUTED *(corrected)* |

## One point apart, and the point is not the interesting part

13 against 12 on fifteen rows is not a result. Two things underneath it are.

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

**Both arms missed the same row.** P2 — and, as first scored, L4 as well, which
turned out to be the key's error rather than theirs. The two arms disagreed on
four rows in all: on P3 both answers are acceptable, on P7 and
L1 the key sides with Opus, and on P6 it sides with Gemini. So the cheap arm was
not the reckless one — **Opus confirmed an invention that Gemini correctly
refused** — and each arm's single false confirm landed on a different row.

**Gemini's misses were not carelessness either.** Its L1 argument is that "the
consequence of certifying an uncontained jail as contained cannot occur because
oxbox unconditionally denies network egress" — a coherent reading that answers a
narrower question than the one the key asks. The key's ground is the file's own
docstring standard, *passing by not looking*, which is a judgment about intent,
not a fact about the sandbox.

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

**Provenance of the ox that ran these.** oxbox `12b8358`, authored 14:03:10 PDT,
two and a half minutes before the first run at 14:05:46; the next commit to touch
`ox` landed 42 minutes after the last run at 14:13:12. Against current oxbox main
that is `git diff 12b8358 HEAD -- ox` = 12 insertions, 0 deletions, of which nine
are comment and three are code: `venue_cost` recorded into the status initializer,
the status record and the attempt record, all after the response is parsed.
Nothing in request building, effort resolution or anything on the wire, so these
figures reproduce against current ox.

(An earlier note gave the baseline as `c8b287e` and the delta as 28 insertions
and 3 deletions. That was the wrong commit -- the manifest-diagnosis change was
already in the tree while these runs executed, so it is not part of the delta at
all. Corrected 2026-09-03 after a peer session checked the authored timestamps
against the run directory names.)

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

**Opus is harness-independent and wording-dependent, and both are in this table.**
`opus` (claude -p, source inlined) and `or-opus` (ox, source as `--files`)
returned identical verdicts on all fifteen findings, across different harnesses,
payload shapes and tokenizers. Whatever generation 1 measured, it was not a
harness artifact. But the same table shows both Opus arms refusing P2 and
confirming L1 -- **one defect, two wordings, opposite verdicts** -- so generation
1's wording effect survives into generation 2 on the same model. The two facts
are not in tension and a reader given only the first will over-read it: what is
stable across harnesses is not thereby stable across how a candidate phrased its
finding.

**Gemini is neither.** The two Gemini arms are the same model at the same effort
and they disagree on six of fifteen, including L1.

## The number that answers the question

Recall is counted over **distinct defects**, not findings. P2 and L1 are one bug,
so counting them separately would score an arm as having found and missed the
same defect at once. P3 is excluded from both columns: its key accepts either
CONFIRMED or UNCERTAIN, so confirming it is not a false positive and declining to
is not a miss, and a row the record refuses to adjudicate cannot be evidence
against either arm. That exclusion is also the only choice not made by which arm
it flatters -- scoring P3 as real costs the arm that hedged it, scoring it as not
real costs the arm that confirmed it.

| arm | confirmed | of which real | precision | defects found | recall | usd |
|---|---|---|---|---|---|---|
| or-opus | 3 | 2 | 67% | 2 of 2 | 100% | $1.0946 |
| or-gemini | 8 | 3 | 38% | 2 of 2 | 100% | $0.1938 |

Those dollars are computed from the archived catalog, and OpenRouter's own
`usage.cost` agrees with them **to the cent on all ten successful runs** --
$1.0946 and $0.1938 summed independently. That is the only external check
`costcheck.py`'s pricing has ever had, and it passed.

`usage.cost` turns out to be present on every response although `ox` never asks
for it: none of these runs' `request.json` carries a `usage` key. An oxbox
handoff records the opposite as a dead end, and it is wrong. The catalog figure
stays the published one anyway -- a price derived from bytes in this repo can be
recomputed by anyone later, and a number read off a live response cannot -- but
the venue's own claim is now recorded beside it, which is both a cross-check and
the thing that would survive a mid-week price change.

**Both arms found every real defect.** The recall column is not where they differ
and the argument does not rest on it. They differ entirely in what else came back:
`or-opus` hands a human three findings to read, `or-gemini` hands back eight for
the same two defects.

`or-gemini` was the only arm to confirm P2 in its own wording -- and it did so
while confirming six of the eight findings in that batch. Catching a real defect
is not evidence of judgment in an arm that confirms nearly everything, and confirm
bias is the one failure mode that makes a supervisor worthless: the entire job is
filtering inventions out, and an arm that confirms them passes the cost downstream
instead of paying it.

So the cheap supervisor costs **$0.90 less** and hands back **five more findings
to read**. It is economical only if reading a code-review finding and dismissing
it against source is worth less than about **eighteen cents**. It is not -- that
is minutes of attention per finding, on exactly the task the supervisor existed
to do.

**On this evidence, no.** A 5.6x cheaper supervisor did not make cheap candidates
economical. The saving is denominated in tokens and the cost it creates is
denominated in human attention, and the second is the expensive one.

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

The `or-gemini` GPT batch failed on first attempt, and **the interesting part is
that it did not fail over HTTP.** The response came back 200 with a well-formed
`chat.completion` body, no top-level `error`, and a populated `usage` block. The
failure is inside it:

```
choices[0].finish_reason   "error"
choices[0].error           {"code": 502,
                            "message": "JSON error injected into SSE stream",
                            "metadata": {"error_type": "provider_unavailable"}}
choices[0].message.content null
usage                      prompt 0, completion 0, cost 0
reasoning                  11,874 characters, present and preserved
```

A client that checks the HTTP status sees success and moves on. ox's HTTP error
path never ran; what caught this was its no-content check -- `model returned no
content (finish=error)`, exit 1, `ok=false`, response and reasoning both kept.
That is the failure worth reporting for venue reliability, because it is the one
that gets past a naive client, and the 11,874 characters of reasoning billed at
zero tokens are confirmed by the venue's own usage block.

It succeeded on one retry. One failure in eleven runs is not a rate, but a
supervisor is infrastructure, and infrastructure that returns 200 on a request it
dropped is a different proposition from one that errors honestly.

(An earlier version of this section called it "HTTP 502 from Google via
OpenRouter". That was wrong and the distinction is the whole value of the datum.)

The run log for that failure is at
`~/.cache/oxbox-verifier/runs-2026-09-03/ox-logs/2026-09-03T21-09-18Z/`, with the
502 body in `response.json`. It was first written to a session scratchpad, which
is cleaned; an availability claim whose evidence has been deleted is a claim
nobody can check, so the whole run set was copied somewhere durable. Point
`--work` at a durable path when the runs are meant to be citable later.

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


---

# Third generation: Fable 5.1 as the price ceiling, and what it did to P2

`anthropic/claude-fable-5.1` added as the expensive control -- $10/$50 per
million, 2x Opus 5 and 13x gemini-3.8-flash, at `high`, its own default. Same ox
path, same pinned bytes, same contract.

**It is also the arm with a conflict of interest, and that turned out to be the
point.** Fable was the survey's first standing supervisor before the job moved to
Opus on price, and it *wrote 11 of the 15 rows it was scored against* -- the
sonnet, gemini-3.7 and gpt batches all carry `agent: claude-fable-5-1`. Only
L1-L4 were Opus's. Its agreement score is circular by construction and is not
reported as accuracy.

## Paying more buys nothing

| arm | confirmed | of which real | precision | defects | recall | usd |
|---|---|---|---|---|---|---|
| or-opus | 3 | 2 | 67% | 2 of 2 | 100% | $1.0946 |
| or-gemini | 8 | 2 | 25% | 2 of 2 | 100% | $0.1938 |
| or-fable | 3 | 2 | 67% | 2 of 2 | 100% | $1.9645 |

Fable and Opus are identical on every headline number. They differ on individual
rows in opposite directions -- Fable refuted P6 where Opus confirmed an
invention, Opus refuted P7 where Fable confirmed one -- and net to the same
score. **The expensive end of the curve is flat.** $0.87 more than Opus for no
measurable difference, which is a cleaner answer to "is the supervisor
underpowered" than any argument about it.

## The control refuted its own verdict

**Fable refuted P2 -- the row Fable wrote.** Its reasoning today is nearly
word-for-word Opus's: the conflation of exceptions is real, but the finding's
premise, a sandbox that permits networking, does not exist at this pin.

Three of four arms refuted it, including its author. The finding's own text says
why: GPT-5.6 sol's stated failure scenario is *"The sandbox permits unrestricted
networking but the host temporarily has no default route"*, and `jail.sb`'s
`(deny network*)` with `oxbox`'s `--unshare-all` makes that premise unreachable
and unconfigurable. The contract asks whether the described failure occurs. It
does not.

**P2 is now REFUTED**, at the maintainer's direction, with the reasoning recorded
in the key.

### This retires the wording-sensitivity finding

Generation 1 read P2-refuted-with-L1-confirmed as one defect getting opposite
verdicts on phrasing, and called that worse than being wrong. **That was an
over-read, and reading the two findings verbatim settles it.** They are not the
same claim:

- GPT's P2 asserts only the leak, on a premise that cannot hold here.
- GLM's L1 asserts the leak *and* adds the argument that survives it -- "there is
  no argument that host-level network failure proves anything about the jail" --
  and proposes the outside-the-jail oracle that became the fix in `0090c35`.

GLM's write-up says more, and the extra part is the true part. Every arm treating
them differently was precision, not inconsistency. The proposed
wording-sensitivity experiment is withdrawn: there is no effect to measure here.

What the episode does establish is a rule the corpus did not have: **a finding is
scored as written, not as generously as it could be read.** Fable-then credited
an accurate mechanism and let an unreachable consequence pass; Fable-now, under a
contract that says an unreachable consequence is not a defect, refuses to. Same
model, same evidence, different standard -- so the standard has to be written
down, which it now is.

## The final answer

Every arm found every real defect. Nobody missed anything. The whole difference
between supervisors is what else they hand back:

| supervisor | cost | findings a human reads | of which real | wasted reads |
|---|---|---|---|---|
| gemini-3.8-flash | $0.1938 | 8 | 2 | 6 |
| claude-opus-5 | $1.0946 | 3 | 2 | 1 |
| claude-fable-5.1 | $1.9645 | 3 | 2 | 1 |

Going cheaper saves **$0.90** and buys **five extra findings to read** -- about
eighteen cents a read, against minutes of human attention each. Going more
expensive costs **$0.87** and buys **nothing at all**.

So the answer to "can a cheap enough supervisor make untrusted super-cheap models
economical" is no, and the reason is not that the cheap supervisor is bad at
finding defects -- it found all of them. It is that a supervisor's product is a
*short* list, and the cheap one cannot produce one. Opus sits at the efficient
point of a curve that is flat above it and steep below.
