<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

# Editor's Rating review

The Editor's Rating column, for the editor to fill in. Every model the survey has put through ox is below with what the record measured on each dimension, my read of it, and a slot for the rating. The scores are bucketed by `ratings.py` from observation frontmatter and are not opinions. The rating is yours and the tools only read it.

## What I need from you

Everything this document asks of you, in one place. Direct edits in the Doc are decisions; margin comments are instructions. Anything not listed here is settled or is mine to do.

- **Q1. Reproducible safe-direction failures.** Both checkers confirmed Fable's F2 and F3, which the record counts as true-and-negligible rather than real. With reproduce-first in force those are demonstrable in seconds. Should a confirmed, reproducible, safe-direction failure count as real, count separately, or stay as it is? *Default if you say nothing:* stays as it is.
- **Q3. Which check sets a fixture's cost ceiling.** The zero-defect control ceiling, $0.9152 per real finding, was computed from Fable's run plus Fable's in-harness check of it, $1.46 at list. The metered check of the same run cost $0.57, which would make the ceiling $0.47. The cost table now uses the bill for that run, so the table and the ceiling constant no longer describe the same check. In-harness, metered, or whichever the ceiling checker performed most recently? *Default:* in-harness, as today.
- **Q4. The models to try next.** The shortlist under "Models to try next" is unmarked, and two of its free rows have since been delisted. Mark the ones you want, strike the ones you do not, and I will queue the first batch on all three fixtures with both checkers, metered. A seeded run on any free model would also give the free tier its first quality score. *Default:* nothing is queued.

Q2 (G1) was ruled after r5 and is recorded under "G1, explained"; Q5 (DeepSeek's re-run) was done. All seven ratings are in, so no rating slot is empty.

**How to rate.** Under each model, replace the blank after **Editor's Rating** with one of Good, Acceptable, Marginal, Poor, and write a line after **Why**. That line becomes the manifest's `why` field, so write it for a reader of the survey. Leave a margin comment for anything else. Good and Acceptable go into the next manifest, Goods above Acceptables. Marginal and Poor stay out.

**Where the scores stand.** The cost score exists on ask-grounding (Fable's ceiling $0.0276 per hit) and on the zero-defect control (`oxbox-clean-control`; $0.9152 per real finding, from Fable's run plus Fable's own in-harness check of it; the metered check of the same run came in cheaper, and question 3 asks which kind of check a ceiling means). It cannot exist on the scanner fix: Fable refuses that prompt whatever the framing, and a diagnostic pair showed the task text, not the file, is the trigger. The quality score exists only on fixtures with a seeded answer set, and it is a dash for every free row because none of the free models has been run on one: the two seeded fixtures were built on 2026-09-02, after the free rows were made, and every free run in the record is a hand-verified real-work batch. Nothing stops a free model from running the scanner fix or ask-grounding, and the three reachable free rows still listed in the shortlist below would get them first. All seven ratings are in. The rule derives the manifest as GLM-5.3 Flash at rank 1 and DeepSeek V4 Flash at rank 2: MiniMax M3 free, rated Good, was delisted from OpenRouter on 2026-09-07 and is held out until a catalog lists it again.

**The cost tables have moved to a Sheet**, one tab per checking model plus the same-batch, per-fixture, ratings and rubric tabs, regenerated from the record each round: [Oxbox Survey costs](https://docs.google.com/spreadsheets/d/1Xbp8ymZBMU7IIbd2OmqQI31ye9L4daRklShv6rzvGMU/edit) (r3; r4 of this document linked r1 by mistake). This document keeps the same-batch table and the reading.

Backticks around model names do not survive the conversion to a Doc; ignore that.

## The rubric

| Dimension | Measured | 5 | 4 | 3 | 2 | 1 | 0 |
|---|---|---|---|---|---|---|---|
| Quality | seeded defects found, of those present | all | 3/4 or more | half or more | a quarter or more | any | none, or no output |
| Cost | USD per real finding or hit, both halves, against the fixture's Fable 5.1 ceiling | under 1/100 | under 1/10 | under 1x | up to 3x | up to 10x | over 10x, or nothing real |
| Speed | wall clock per run | under 30 s | under 2 min | under 5 min | under 10 min | under 20 min | 20 min or more, or timed out |

## What the scale looks like: the paid baselines

Reference rows, never rated, never in the manifest. They show what a 5 and a 0 look like on the same fixtures. Fable 5.1 is the price ceiling, so its own cost score is a 2 by construction.

| Model | Fixture | Quality | Cost | Speed | Real / findings | Model USD |
|---|---|---|---|---|---|---|
| claude-fable-5.1 | ask-grounding | 5 | 2 | 4 | | $0.2756 |
| claude-fable-5.1 | secret-scanner-fix | refused | | | | $0 |
| claude-fable-5.1 | zero-defect control | | | 4 | 2 / 5 | $0.3663 |
| gpt-5.6-sol | ask-grounding | 5 | 4 | 5 | | $0.0273 |
| gpt-5.6-sol | secret-scanner-fix | 5 | | 4 | | $0.0392 |
| gpt-5.6-sol | zero-defect control | | | 3 | 1 / 8 | $0.0861 |
| claude-sonnet-5 | ask-grounding | 5 | 3 | 5 | | $0.0416 |
| claude-sonnet-5 | secret-scanner-fix | 0 | | 3 | | $0.1845 |
| claude-sonnet-5 | zero-defect control | | | 3 | 0 / 2 | $0.1611 |
| gemini-3.7-flash | ask-grounding | 5 | 4 | 4 | | $0.0183 |
| gemini-3.7-flash | secret-scanner-fix | 5 | | 2 | | $0.1531 |
| gemini-3.7-flash | zero-defect control | | | 3 | 1 / 1 | $0.0620 |
| deepseek-v4-flash | ask-grounding | 5 | 5 | 5 | | $0.0009 |
| deepseek-v4-flash | secret-scanner-fix | 0 | | 0 | | $0.0014 |
| deepseek-v4-flash | zero-defect control |  | 3 | 0 | 1 / 4 | $0.0203 |

Sonnet's 0 on the scanner fix is a wrong hunk header, so the patch does not apply, plus a self-hit. DeepSeek's 0 is the same apply failure and a 21-minute wall clock. Ask-grounding is saturated, seven models at 10 of 10, so a 5 there says little and the cost score is what separates them. Fable on the zero-defect control is the first model to find both known defects at that pin, both hedged UNCERTAIN, with one invention.

## minimax/minimax-m3:free (OpenRouter, delisted 2026-09-07; rank 1 of the 2026-09-01 manifest)

**Quality.** No quality score, no seeded set. Real work: 13 of 15 findings real across two review batches on oxbox on 2026-08-29, two of them fixed within the hour. 7 of 12 on the exposure gate on 2026-08-30, where a reframed prompt found the cross-host redirect the neutral prompt missed, fixed the same afternoon. Three more batches that day, not rows because they were verified by the fixes that shipped rather than by a review pass: six findings confirmed, one UNCERTAIN refuted, the rest unverified. The table shows 20 real of 27 across the two rows.

**Cost.** Free. Both halves are not per-run in the record, so no cost score. The reasoning share is the story: 98 percent of completion tokens went to thinking across seven runs, the largest run used 84 percent of the 100,000 default, and one call in seven returned nothing. Two of seven responses carry token accounting that does not add up. Every false finding cost a verification pass, and there were seven of those across the two rows.

**Speed.** 182 s and 189 s on the two rows, a 3. Across the seven runs in the logs the spread is 111 s to 734 s, so the worst case is a 1.

**Disqualifier.** Delisted since 2026-09-07: the 2026-09-07 snapshot finds no `minimax/minimax-m3:free` on OpenRouter, its endpoints list is empty, and only the paid `minimax/minimax-m3` remains at $0.30 in and $1.20 out per million. The delisting rule holds it out of the manifest whatever its rating, until a catalog lists it again. Before that: the shared free pool 429s under concurrency and clears at 120-second serial retries.

**My read.** The only free model with run evidence at volume, and the findings it leads with are the ones that get fixed. The caveats are budget and reliability, not quality: run it at the 100,000 default, expect one empty return in a handful, and read everything it emits because a quarter of it will not hold. It was rank 1 and nothing in the record argued for moving it; the venue moved it. Your Good stays on the record for the day it comes back.

**Editor's Rating:** Good

**Why:** Decent performance, OK speed.

## z-ai/glm-5.3-flash (OpenRouter, paid, rank 1 of the 2026-09-07 manifest, pinned)

**Quality.** Run as a candidate on all three fixtures, at your direction. Ask-grounding: 10 of 10 in 25 seconds, a 5. Scanner fix: corrupt hunk header, the patch does not apply without a recount, all 8 verdicts hold and zero self-hits behind it, but gate 1 is the gate, a 0. Zero-defect control: 4 findings, 0 real, 4 inventions, after your C3 ruling (below); it had been recorded as 1 real. The same model ran the same three payloads as a baseline on 2026-09-02 and got a clean apply on the scanner fix and one real defect on the zero-defect control. So n=2 on each fixture: one pass and one fail on the mechanical half of a diff, one real finding in eight on the review, and three inventions repeated.

**Cost.** Ask-grounding at a tenth of a cent, a 5 against the ceiling. Scanner fix $0.0090, no score because that fixture has no ceiling. Zero-defect control billed $0.0034, double the catalog computation, because OpenRouter routed that one run to SiliconFlow at $0.15 and $0.50 per million instead of Z.AI at $0.075 and $0.25. The catalog price is the price of one route. Since oxbox 1.1.0 the manifest pins the route: the 2026-09-07 entry names the four routes the rated runs went to, with `max_price` at the catalog row, which excludes SiliconFlow until it prices at list.

**Speed.** 25 s on ask, a 5. 730 s on the scanner fix, a 1, and 544 s as a baseline. 90 s on the zero-defect control, a 4.

**Disqualifier.** None. Vendor note: Z.ai (Zhipu) is on the BIS Entity List, effective 2025-01-16; see the regulatory section below.

**My read.** In ask mode this route is fast, cheap and right, twice. In diff mode it reasons for ten minutes and then miscounts a hunk header half the time. On review it reaches one real defect per run and repeats its inventions. The Ox Alpha evidence that put it at rank 2 was a 5-of-5 review with zero false positives; the paid route has not reproduced that on any fixture, and the zero-defect control invention rate is the reason to hesitate. Acceptable on the ask and the price; whether diff-mode reliability drags it to Marginal is your call.

**Editor's Rating:** Acceptable

**Why:** Fast and mostly good. Z.ai's regulatory status is a concern though.

## deepseek/deepseek-v4-flash (OpenRouter, paid, rank 2 of the 2026-09-07 manifest, pinned; rated this round)

**Quality.** Run as a candidate on all three fixtures under your rule that a cheap enough model is a candidate; at $0.089 in and $0.177 out per million on the 2026-09-07 catalog it is the cheapest paid row in the survey.

- Ask-grounding: 10 of 10 in 37 seconds, a 5, terse and right, and the new executable scorer passes it.
- Scanner fix: corrupt hunk header, the patch does not apply without a recount, 8 of 8 verdicts and zero self-hits behind it, a 0, the same failure as its baseline run and as GLM-5.3 Flash's candidate run.
- Zero-defect control, four times. The first candidate run went to StreamLake and returned nothing after 33 minutes with 99,999 of 100,000 tokens spent reasoning; the re-run you asked for (question 5) went to Novita, the third provider to serve this model, and returned two findings in 47 seconds. D1 is C3 in the same words and falls under your C3 ruling as an invention; D2 is G1's mechanism and is real under your G1 ruling. Then, on 2026-09-07, the first two pinned runs the survey has made: the same payload to StreamLake by name answered in 151 seconds with one finding (no timeout on `getaddrinfo`, refuted by reproduction inside the jail, where the call raises in 6 ms), and to DigitalOcean by name answered on the third attempt, after two 429s from that provider's shared pool, in 320 seconds with one finding (C3 again, in a third wording). 1 real of 4 findings over the four runs.
- A fixture cell takes the worst score on each dimension, so the table reads speed 0 from the blowout beside cost 3 and 1 real of 4.

**Cost.** Ask-grounding at a tenth of a cent, a 5 against the ceiling. Scanner fix $0.0024, no score, because that fixture has no cost ceiling: the score is a ratio against Fable 5.1's cost per real finding on the same fixture, and Fable refuses the scanner-fix prompt, so there is nothing to divide by. Zero-defect control $0.016 for nothing on the blowout, $0.0016 for the two Novita findings (billed at 1.6x the catalog row, because that route is priced above list), $0.0015 pinned to StreamLake and $0.0007 pinned to DigitalOcean for the identical payload. The Novita re-run is the first row on this fixture with a metered checking half: Fable 5.1 $0.37 and Opus 5 $0.23 for one request each, so both halves came to $0.37 against the $0.92 ceiling, a cost 3. Nine runs on OpenRouter have gone to three providers at three prices.

**Speed.** 37 s on ask, a 4. 16 minutes on the scanner fix, a 1. 33 minutes for nothing, a 0, then 47 seconds, 151 seconds and 320 seconds on the same payload from three named providers.

**Disqualifier.** None. Vendor note: DeepSeek is not on either list in the regulatory section; you reported a non-public backlog, uncited.

**My read.** The blowout was the route, not the weights, and the route can now be named: oxbox 1.1.0 (2026-09-07) passes OpenRouter's `provider` object through, and the pinned pair showed what a pin buys. Attribution and a price guard, yes: the route that answered is the route that was asked for, and DigitalOcean's refusal was visible as DigitalOcean's instead of being routed around. Stability and quality, no: StreamLake, which hung for 33 minutes on Saturday, answered in 151 seconds on Monday, and the route that served the model's one ideal answer served an invention on the same bytes. On what it finds, the model is fast, cheap and has produced nothing the record had not already adjudicated: five answers to the zero-defect control, all different, one right. On ask it is as good as anything in the table and cheaper than all of it; on the two harder fixtures it has failed the apply gate twice. Your Acceptable puts it at rank 2, pinned to the three routes its runs went to, with `max_price` at the catalog row.

**Editor's Rating:** Acceptable

**Why:** we fixed the routing problem; otherwise it's decent.

## nemotron-3-ultra-free (OpenCode Zen, listed)

**Quality.** No quality score, no seeded set. 2 of 10 findings real on the exposure gate on 2026-08-30, a matched payload against MiniMax's 7 of 12. The one defect in the file that mattered was filed as UNCERTAIN with "low but non-zero" confidence.

**Cost.** OpenCode publishes no price, so no model USD. 4,872 completion tokens against MiniMax's 30,712 on the same payload, so a sixth of the tokens. Eight refutations for two real findings is the expensive half.

**Speed.** 129 s, a 3.

**Disqualifier.** None. An earlier "never reached" verdict had a mechanical cause, a harness wedge fixed in oxbox, so the model has never failed; it has been run exactly once.

**My read.** One run, low yield, and it hedged the finding that counted. A run on a seeded fixture would settle whether the yield or the hedging is the real problem, and that costs nothing at this venue.

**Editor's Rating:** Poor

**Why:** 2/10 is pretty poor performance.

## x-preview-f-free, the Ox Alpha listing (OpenCode Zen, delisted)

**Quality.** No quality score, no seeded set. 5 of 5 real on one file on 2026-08-24, zero false positives, including a real credential leak in oxbox's redirect path that falsified a claim the maintainer had made in writing. Issue 0.2 had 63 findings at 72 percent on the same weights through OpenRouter's stealth slot.

**Cost.** Free while it lasted. 3,611 prompt and 16,704 completion tokens, 4,935 of them reasoning. Reasoning is billed against the completion budget, which is what broke ox's old 32,000 default and led to the 100,000 default.

**Speed.** Roughly 15 minutes on the one recorded run, a 1.

**Disqualifier.** OpenCode blocked ox's default User-Agent on 2026-08-24; ox was fixed and the run that found the leak happened the same day, so the record shows it cleared. The listing itself is gone: the model was revealed as GLM-5.3 Flash and is in no current snapshot. Same weights are served paid on OpenRouter as z-ai/glm-5.3-flash, rated above.

**My read.** The best precision in the record, on a listing that no longer exists. Your Marginal keeps it out of the manifest, which is the right outcome for a delisted row whatever the reason; the delisting question below is about making that mechanical.

**Editor's Rating:** Marginal

**Why:** Great performance, terrible speed.

## mistral/leanstral-1-5 (Requesty, listed)

**Quality.** No quality score, no seeded set. 6 findings, 0 real, on the same file where Ox Alpha found 5 of 5. Four were titled BUG and then concluded to be non-defects in their own body. One was factually wrong about Python semantics. Three were the same observation with three contradictory verdicts.

**Cost.** Paid on Requesty; no USD in the record. Roughly a tenth of Ox Alpha's tokens on the same input. Six refutations for zero real findings.

**Speed.** Not recorded in seconds. The observation says fifteen times faster than Ox Alpha on the same input, which would put it around a minute.

**Disqualifier.** None. Requesty accepts chat completions without a deposit.

**My read.** One run, and the output had negative value: acting on its one confident claim would have "fixed" a guard that already works.

**Editor's Rating:** Poor

**Why:** 0/6 findings is the definition of Poor.

## z-ai/glm-5.3-free (ZenMux, delisted)

**Quality.** Answered with nothing. Empty content at both 8,000 and 32,000 token budgets, more than 99.9 percent of each spent on reasoning, finish reason set, no error. The 127,000-character trace circles the exact defect Ox Alpha reported and ends mid-sentence. Under the rule that is a quality 0, not a disqualifier: the venue served the request and the model produced no review.

**Cost.** Free at the price, but ZenMux gates its free tier on a funded account, so it was uncallable until a deposit was made.

**Speed.** Not recorded.

**Disqualifier.** The deposit gate came from a probe, so it annotates the catalog rather than the row. The listing is gone: ZenMux's 2026-09-01 catalog has z-ai/glm-5.3 and z-ai/glm-5.3-flash as paid rows and only GLM-4.7 Flash and GLM-4.6v Flash as free ones. Your ZenMux balance would let any of those run, but none of them is this row.

**My read.** An output problem the catalog cannot see, on a listing that has since vanished. Poor on this evidence, and moot in practice.

**Editor's Rating:** Poor

**Why:** It's delisted.

## What it costs, by checking model

The full tables are in the [costs Sheet](https://docs.google.com/spreadsheets/d/1Xbp8ymZBMU7IIbd2OmqQI31ye9L4daRklShv6rzvGMU/edit), one tab per checking model. Your direction to run both Opus 5 and Fable 5.1 as checkers is in force, and your answer to question 3 is now in the record: the checking half can be metered. A metered check sends the same verification instructions and the same five pinned files through OpenRouter as one request, and the figure is what the venue billed, every token counted. Six such checks exist today, three per checker: Fable's zero-defect control run, DeepSeek's re-run, and the G1 re-check under the amended contract; the tables mark them ‡, and where a run has both an in-harness check and a metered one, the bill wins. The in-harness figures remain floors for the reason r4 gave: a subagent's output tokens are not in its transcript and cannot be derived from the harness total.

What metering showed on Fable's five-finding batch: the same five verdicts from Fable 5.1 for $0.57 in 98 seconds, against $1.46 at list and 152 seconds for the in-harness subagent with its eight tool calls and cache writes; Opus 5 for $0.37 in 142 seconds against a $0.79 floor and 343 seconds. Fable used 29 percent fewer output tokens than Opus and finished 44 seconds sooner, and still cost 56 percent more, because its list price is double; your theory that Fable uses fewer tokens holds, and the bill does not follow it. The price of metering is that the checker reads and cannot run: the metered Opus flipped F4 from uncertain to refuted on a reading the reproduction on dev contradicts. Under reproduce-first the metered check is the fallback, and its cost is the cost of the fallback.

The reading: under either checker the model half never decides a run's cost; the checking half does. The free models' checking is the most expensive in the table because their runs were hand-verified real-work batches of ten to twelve findings. Fixture runs scored by a key or a scorer have a zero checking half by rule.

#### The same batch, checked by more than one supervisor

Run `2026-09-03T03-05-25Z`:

| Checker | Input | Output | Cache read | Cache write | USD | Wall clock |
|---|---|---|---|---|---|---|
| claude-fable-5-1 | 66 | - | 130,427 | 41,989 | $0.5581 at list | 40 s |
| claude-opus-5 | 16 | - | 440,152 | 47,193 | $0.5151 at list | 60 s |

Run `2026-09-03T03-20-23Z`:

| Checker | Input | Output | Cache read | Cache write | USD | Wall clock |
|---|---|---|---|---|---|---|
| claude-fable-5-1 | 98 | - | 193,423 | 46,404 | $0.6294 at list | 47 s |
| claude-opus-5 | 16 | - | 434,642 | 47,340 | $0.5133 at list | 61 s |

Run `2026-09-03T03-21-05Z`:

| Checker | Input | Output | Cache read | Cache write | USD | Wall clock |
|---|---|---|---|---|---|---|
| claude-fable-5-1 | 66 | - | 114,659 | 75,485 | $0.9729 at list | 90 s |
| claude-opus-5 | 10 | - | 252,658 | 80,094 | $0.6270 at list | 2 min |

Run `2026-09-06T21-22-57Z`:

| Checker | Input | Output | Cache read | Cache write | USD | Wall clock |
|---|---|---|---|---|---|---|
| claude-fable-5-1 | 66 | 9,744 (derived) | 114,776 | 75,805 | $1.4641 at list | 3 min |
| claude-fable-5-1 via openrouter (billed) | 17,402 | 7,934 | - | - | $0.5707 billed | 98 s |
| claude-opus-5 | 12 | - | 345,900 | 99,363 | $0.7940 at list | 6 min |
| claude-opus-5 via openrouter (billed) | 17,400 | 11,173 | - | - | $0.3663 billed | 2 min |

Derived. claude-fable-5-1: output is the Agent tool's reported total (85,615) minus input and cache writes; plausible against the visible reply, but see the Opus record of the same batch for a case where that derivation fails.

Run `2026-09-06T21-30-07Z`:

| Checker | Input | Output | Cache read | Cache write | USD | Wall clock |
|---|---|---|---|---|---|---|
| claude-fable-5-1 | 66 | 7,123 (derived) | 114,892 | 75,858 | $1.3338 at list | 117 s |
| claude-opus-5 | 8 | 10,758 (derived) | 184,557 | 87,230 | $0.9065 at list | 5 min |

Derived. claude-fable-5-1: output is the Agent tool's reported total (83,047) minus input and cache writes; subagent transcripts do not record final output. claude-opus-5: output is the Agent tool's reported total (97,996) minus input and cache writes; subagent transcripts do not record final output.

Run `2026-09-07T00-06-45Z`:

| Checker | Input | Output | Cache read | Cache write | USD | Wall clock |
|---|---|---|---|---|---|---|
| claude-fable-5-1 via openrouter (billed) | 17,610 | 3,806 | - | - | $0.3664 billed | 49 s |
| claude-opus-5 via openrouter (billed) | 17,608 | 5,753 | - | - | $0.2319 billed | 79 s |

## Two checkers, five batches

| Batch | Fable 5.1 | Opus 5 | Record |
|---|---|---|---|
| GLM-5.3 Flash candidate, zero-defect control (C1..C4) | C3 confirmed | C3 refuted | you ruled refuted after the runs |
| Fable 5.1 baseline, zero-defect control (F1..F5), in-harness | F1 refuted, F2..F5 confirmed | same, F4 uncertain on host state | F2, F3 counted as true-and-negligible, not real |
| the same five, metered through OpenRouter | identical to the in-harness Fable check | F4 refuted, rest as before | unchanged; F4 stays real on the dev reproduction |
| GLM-5.3 Flash baseline, zero-defect control (G1..G4) | all four refuted | G1 confirmed, rest refuted | G1 is real, ruled 2026-09-06 (fixed upstream) |
| DeepSeek V4 Flash re-run, zero-defect control (D1, D2), metered | D1 confirmed as safe-direction, D2 refuted | both refuted | D1 invention by the C3 ruling; D2 real by the G1 ruling |
| GLM-5.3 Flash baseline, zero-defect control (G1..G4), re-checked metered under the G1 ruling | G1 confirmed, G4 confirmed as benign, rest refuted | G1 confirmed, rest refuted | the split on G1 closes; G4 stays refuted per the key |
| Both models' baseline ask-grounding (10 each) | 10 of 10 | 10 of 10 | 10 of 10, and the scorer agrees |

The C3 shape has now been checked four times and split the same way every time: Fable credits the mechanism and calls the failure safe-direction, Opus refutes, and the reproduction sides with Opus for a reason neither reader can see from the source (at uid 0 the jail really exposes the shadow file, so the FAIL is true). The G1 shape has been checked three times: in-harness Fable refuted, in-harness Opus confirmed, and both metered checkers refuted DeepSeek's restatement of it as written. Every refutation of it says the same thing, that no leaking jail exists at this pin for the vacuous pass to conceal. You ruled on it after r5; the ruling is recorded below.

## The C3 ruling

Two checkers split on finding C3 of the GLM-5.3 Flash zero-defect control candidate run: Fable 5.1 confirmed it, Opus 5 refuted it. At your direction it was run rather than read again, on argenta (macOS, seatbelt) and dev (Debian 13, bubblewrap), with the `/etc/shadow`-first scenario forced on Linux at an ordinary uid and at uid 0.

| Host, uid, first path in the list | Read probe | Stat oracle | `open("/etc/shadow")` in the jail | The oracle's FAIL is |
|---|---|---|---|---|
| macOS, ordinary user, `~/.ssh` | shadow not in the list on darwin | PASS | no such file on macOS | nothing to judge |
| Linux, ordinary user, real home | PASS | PASS on `~/.ssh` | PermissionError | nothing to judge |
| Linux, ordinary user, shadow forced first | PASS | FAIL, exit 1 | PermissionError | false, the jail holds |
| Linux, uid 0, shadow forced first | skipped by the uid-0 rule | FAIL, exit 1 | readable, 923 bytes | true, root reads the host's shadow file |

The stat succeeded at both uids, so the `/etc` bind is the cause and uid 0 is not. Your ruling: follow the real-world evidence. C3 is refuted; the run is 0 real of 4, recorded as a correction observation that the tooling overlays onto the original row, which stays as written. Two rules came out of it, both now in the repo: reproduction is the default baseline for a verdict wherever the failure can be run against the pin in a jail, and prompts should name both platforms, since the current ones do not and the models learn about seatbelt and bubblewrap only from the payload.

## What each fixture can prove

You asked whether every test now has a real-world result to check against. Not yet, and the fixtures differ in kind.

| Fixture | How a result is checked today | Executable? |
|---|---|---|
| secret-scanner-fix | `git apply --check` at the pin, eight measured pattern verdicts, a self-scan of `ox` | yes, fully; the scorer is the check |
| ask-grounding | an answer key with line citations, and since today a scorer that extracts the pinned `ox` and runs five of the seven settled questions with `--dry-run` (the credential variable, the default mode, the manifest-version exit, the base_url warning, the 400,000-byte limit at the boundary), reports each observed fact against the key, then pattern-scores the answers; questions 2 and 7 need an HTTP exchange `ox` will not fake and go to a reader; 8 to 10 are scored on saying "not settled" | yes, for eight of ten; all twelve archived runs pass, and the five executed facts agree with the key |
| zero-defect control | the two known defects can be reproduced (the stat oracle was, today, on both platforms; the offline-host one needs a host with no route), everything else is read | per finding, on demand |
| review-queue, exposure-gate | human verification, and fixes that shipped upstream | no answer key by design |

Reproduce-first is now the rule for any finding whose failure can be run, and ask-grounding is executable (your question 4). If the key ever drifts from the code the scorer prints DRIFT rather than trusting the key. Making the review fixtures executable would mean answer keys, which the corpus rule forbids.

## Regulatory exposure

Added at your direction. This is a standing caveat the generator will now carry in every issue, tiered and linked, never as legal advice. What is in the record as of 2026-09-06:

- **BIS Entity List** (Commerce Department export controls). Zhipu AI, the vendor behind the z-ai models including glm-5.3-flash and the Ox Alpha weights, was added effective 2025-01-16 ([Federal Register 2025-00704](https://www.federalregister.gov/documents/2025/01/16/2025-00704/addition-of-entities-to-and-revision-of-entry-on-the-entity-list)). The list restricts supplying listed companies with US-origin items; it does not by itself forbid calling the vendor's hosted API, but procurement and compliance policies commonly key on it.
- **1260H list** (Defense Department, Chinese military companies). The June 2026 update added Alibaba, the vendor behind Qwen, and Baidu ([WilmerHale, 2026-06-11](https://www.wilmerhale.com/en/insights/client-alerts/20260611-pentagon-adds-65-new-entities-to-the-1260h-list-of-chinese-military-companies); [CNBC, 2026-06-09](https://www.cnbc.com/2026/06/09/alibaba-baidu-byd-named-on-pentagons-china-military-list-.html)). It bars the department from contracting with listed companies and, from June 2027, from buying their products through third parties.
- **Pending additions.** You reported that further Chinese AI vendors are on a non-public backlog for Entity List addition. I found no citable source, so the skill carries it as unverified and names no vendor. If you have a link, add it here and I will cite it.

A listing is a card fact: it can never earn a rating and it is not a disqualifier in the table's sense, since the venue serves the model. It is a fact you weigh when rating, and the catalog table will state it in each affected model's limitation column in the same words every week.

## Models to try next

Every model below is listed and, where the venue was probed, reachable. Card facts from the 2026-09-01 catalog, checked against the 2026-09-07 snapshot; nothing here is a rating. Two rows left the venue this week: `minimax/minimax-m2.7:free` and `z-ai/glm-5.2:free` are delisted, struck below. `inclusionai/ling-3.0-flash-sante:free` appeared. The completion cap matters because ox sends 100,000 by default and a lower cap has to go in the manifest's params.

**Free, reachable, never run** (OpenRouter unless noted):

| Model | Context | Completion cap | Reasoning | response_format | Note |
|---|---|---|---|---|---|
| ~~minimax/minimax-m2.7:free~~ | 197K | 177K | yes | yes | delisted 2026-09-07, with its sibling |
| cohere/north-mini-code:free | 256K | 64K | yes | no | a code model; no structured output |
| dots-studio/dots-3-note-preview:free | 512K | 461K | yes | yes | also free on ZenMux |
| inclusionai/ling-3.0-flash-fin:free | 262K | 32K | yes | no | Ant Group; low cap |
| google/gemma-4-31b-it:free, gemma-4-26b-a4b-it:free | 262K | 32K | yes | yes | rate-limited at probe time, not closed |
| ~~z-ai/glm-5.2:free~~ | 256K | 230K | yes | yes | delisted 2026-09-07 |
| ZenMux: z-ai/glm-4.7-flash-free, glm-4.6v-flash-free, ling-3.0-tiny | | | | | your balance covers them; Zhipu rows carry the list note |
| Requesty: google/gemma-4-31b-it, nvidia/muse-glimmer-30b, nemotron-3-super-120b-a12b, nemotron-3.5-lightning-30b-a3b | | | | | answered the probe; class B, no published price |

**Cheap paid, under the dollar line, plausible for review:**

| Model | In/out $/M | Context | Completion cap | Note |
|---|---|---|---|---|
| openai/gpt-oss-120b | 0.037/0.17 | 131K | 118K | the obvious next cheap paid candidate; US vendor |
| openai/gpt-oss-20b | 0.03/0.13 | 131K | 118K | same family, smaller |
| qwen/qwen3-coder-next | 0.12/0.80 | 262K | 236K | no reasoning field; Alibaba, 1260H |
| qwen/qwen3.6-35b-a3b | 0.10/0.90 | 262K | 236K | Alibaba, 1260H |
| nvidia/nemotron-3-super-120b-a12b | 0.085/0.40 | 1M | 16K | cap needs a manifest param |
| nvidia/nemotron-3.5-lightning | 0.08/0.20 | 262K | 131K | |
| google/gemma-4-31b-it | 0.09/0.34 | 262K | 16K | cap needs a manifest param |
| mistralai/mistral-small-2603 | 0.15/0.60 | 262K | 210K | EU vendor |
| mistralai/codestral-2508 | 0.30/0.90 | 256K | 205K | no reasoning field; code model |
| xiaomi/mimo-v2.5 | 0.14/0.28 | 1M | 131K | listed on OpenCode Zen too |
| stepfun/step-3.5-flash | 0.10/0.30 | 262K | 65K | no response_format |
| tencent/hy3 | 0.08/0.33 | 262K | 128K | |
| inception/mercury-2 | 0.25/0.75 | 128K | 50K | a diffusion model, unusual |
| arcee-ai/trinity-large-thinking | 0.25/0.80 | 262K | 80K | no response_format; US vendor |

My suggestion for the first batch: the three reachable free rows still listed plus gpt-oss-120b, mistral-small-2603, nemotron-3.5-lightning and mimo-v2.5, on all three fixtures, both checkers. That is 24 runs at a few cents of model cost and, at today's rates, roughly a dollar of checking per hand-verified batch. Mark the ones you want, strike the ones you do not, and I will queue them.

## G1, explained

You asked me to explain G1 further. Here is the whole of it.

**What the finding says.** On 2026-09-02 GLM-5.3 Flash, as a baseline on the zero-defect control, wrote that `probe()` in `jailtest.py` scores any exception as containment, so a network probe that fails because the host is offline reports PASS, and "an offline host produces a false 'jail holds' verdict." The answer key lists this as L1, offline probes are vacuous, one of the two defects known to be in the file at that pin. It was fixed upstream in oxbox `0090c35`, after the pin, so the fix is outside what any checker can see.

**What is true about the mechanism.** Everything. `probe()` catches `Exception`, records `blocked=True` and keeps only the class name. `tcp_connect`, `dns_lookup` and `udp_send` raise `OSError` subclasses on a timeout or an unreachable network exactly as they do on a jail's denial. On dev today, inside a working jail, the network probes raised `ENETUNREACH` as `OSError` and were scored PASS; the probe cannot tell a jail that denied the connection from a host that had nowhere to send it. GLM described this correctly and DeepSeek redescribed it correctly on Saturday.

**What the checkers disagree about.** The consequence. The finding's stated failure is a false "jail holds": a jail that leaks network, certified by a probe that could not have noticed. Fable's in-harness checker, and both metered checkers on DeepSeek's restatement, read the source and say the jail at this pin cannot leak network: seatbelt has `(deny network*)`, bubblewrap runs `--unshare-all`, and there is no flag or path that shares the network back in. So the scenario "a leaking jail passes" needs a jail this tree cannot produce, and under your C3 rule (score the finding as written; a mechanism whose consequence is unreachable in this tree is not a defect) it is refuted. Opus's in-harness checker confirmed it in the unsafe direction: the probe would pass silently through a future regression, and a test whose PASS does not depend on the thing it tests is broken now, not later, with the caveat that today the unearned PASS coincides with the right answer.

**Why C3 and G1 look the same and are not.** Both are a real mechanism with a stated consequence the tree cannot reach. But C3's consequence was wrong on its own terms: it said the FAIL at uid 0 was false, and the reproduction showed the FAIL was true, root reads the shadow file inside the jail. Refuting C3 followed the evidence about what the code does. G1's consequence is not wrong; it is conditional on a leak the code does not have. Refuting G1 would follow a rule about what counts, not evidence about what the code does. The reproduction on dev supports G1's mechanism and cannot speak to its consequence, because to show a leaking jail passing you need a leaking jail.

**Your ruling (2026-09-06, after r5): "a host that's down doesn't count as the jail succeeding."** G1 stands as real and D2 with it. The rule is now stated in the verifier contract and the decisions log: a finding is refuted when its stated consequence is shown false or needs a state the pin cannot produce, and not merely because the property a check certifies happens to hold today when the finding is that the check cannot fail. Checks from here on answer a contract that differs from the one the earlier checks answered, so the same-batch tables keep both, and a re-check of the G1 shape under the new wording was the control, and it was run the same night: both metered checkers confirm G1 under the amended contract ($0.16 and $0.47, both back inside two minutes), and Fable's reason adds the sentence the ruling turns on, that today's backends deny network "but the test would not detect their loss."

**What each ruling would have meant.** If G1 stands, the record's position is that a test which cannot fail is a defect in the test, whatever the jail does today, which is the position the upstream fix took and the answer key encodes. The C3 rule then reads: a finding is refuted when its stated consequence is *false*, not merely when it is *unreachable today*. D2 stands with it and DeepSeek's re-run is 1 real of 2. If G1 is reversed, the rule reads as Fable's checker read it, strictly as written, the answer key loses one of its two known defects for scoring purposes (the fix upstream stays a fact, but not a scoreable one at this pin), GLM's September 2 baseline drops to 0 real of 4, and DeepSeek's re-run drops to 0 of 2 by a correction. My recommendation is that G1 stands and the C3 rule is stated as "refuted when the consequence is shown false", because that is the rule the reproduction actually applied and it keeps the key honest about a defect that was real enough to fix.
