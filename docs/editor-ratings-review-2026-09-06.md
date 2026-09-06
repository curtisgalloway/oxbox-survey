<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

# Editor's Rating review

The first pass at the Editor's Rating column, for the editor to fill in. Every model the survey has put through ox is below with what the record measured on each dimension, my read of it, and a slot for the rating. The digits are bucketed by `ratings.py` from observation frontmatter and are not opinions. The rating is yours and the tools only read it.

**How to rate.** Under each model, replace the blank after **Editor's Rating** with one of Good, Acceptable, Marginal, Poor, and write a line after **Why**. That line becomes the manifest's `why` field, so write it for a reader of the survey. Leave a margin comment for anything else. Good and Acceptable go into the next manifest, Goods above Acceptables. Marginal and Poor stay out.

**Two things to know about the digits this week.** The cost digit is a dash for every row, because each fixture's ceiling is Fable 5.1's cost per real defect on that fixture and Fable has not run any of them. And the quality digit is a dash for every free candidate, because the two review fixtures they ran on have no seeded defect set by the corpus rule. So for the candidates you are rating on the raw column, real findings over findings emitted, plus speed, plus the color. That is the state of the evidence, not a gap in the table.

Backticks around model names do not survive the conversion to a Doc; ignore that.

## The rubric

| Dimension | Measured | 5 | 4 | 3 | 2 | 1 | 0 |
|---|---|---|---|---|---|---|---|
| Quality | seeded defects found, of those present | all | 3/4 or more | half or more | a quarter or more | any | none, or no output |
| Cost | USD per real defect, both halves, against the fixture's Fable 5.1 ceiling | under 1/100 | under 1/10 | under 1x | up to 3x | up to 10x | over 10x, or no real defect |
| Speed | wall clock per run | under 30 s | under 2 min | under 5 min | under 10 min | under 20 min | 20 min or more, or timed out |

## What the scale looks like: the paid baselines

Reference rows, never rated, never in the manifest. They show what a 5 and a 0 look like on the same fixtures.

| Model | Fixture | Quality | Speed | Real / findings | Model USD |
|---|---|---|---|---|---|
| gpt-5.6-sol | ask-grounding | 5 | 5 | | $0.0273 |
| gpt-5.6-sol | secret-scanner-fix | 5 | 4 | | $0.0392 |
| gpt-5.6-sol | clean-control | | 3 | 1 / 8 | $0.0861 |
| claude-sonnet-5 | ask-grounding | 5 | 5 | | $0.0416 |
| claude-sonnet-5 | secret-scanner-fix | 0 | 3 | | $0.1845 |
| claude-sonnet-5 | clean-control | | 3 | 0 / 2 | $0.1611 |
| gemini-3.7-flash | ask-grounding | 5 | 4 | | $0.0183 |
| gemini-3.7-flash | secret-scanner-fix | 5 | 2 | | $0.1531 |
| gemini-3.7-flash | clean-control | | 3 | 1 / 1 | $0.0620 |
| deepseek-v4-flash | ask-grounding | 5 | 5 | | $0.0009 |
| deepseek-v4-flash | secret-scanner-fix | 0 | 0 | | $0.0014 |
| deepseek-v4-flash | clean-control | | 2 | 0 / 0 | $0.0005 |
| glm-5.3-flash | ask-grounding | 5 | 4 | | $0.0010 |
| glm-5.3-flash | secret-scanner-fix | 5 | 2 | | $0.0059 |
| glm-5.3-flash | clean-control | | 3 | 1 / 4 | $0.0015 |

Sonnet's 0 on the scanner fix is a wrong hunk header, so the patch does not apply, plus a self-hit. DeepSeek's 0 is the same apply failure and a 21-minute wall clock. Ask-grounding is saturated, all five at 10 of 10, so a 5 there says little.

## minimax/minimax-m3:free (OpenRouter, listed, rank 1 of the current manifest)

**Quality.** No fixture digit. Real work: 13 of 15 findings real across two review batches on oxbox on 2026-08-29, two of them fixed within the hour. 7 of 12 on the exposure gate on 2026-08-30, where a reframed prompt found the cross-host redirect the neutral prompt missed, fixed the same afternoon. Three more batches that day, not rows because they were verified by the fixes that shipped rather than by a review pass: six findings confirmed, one UNCERTAIN refuted, the rest unverified. The table shows 20 real of 27 across the two rows.

**Cost.** Free. Both halves are not per-run in the record, so no cost digit. The reasoning share is the story: 98 percent of completion tokens went to thinking across seven runs, the largest run used 84 percent of the 100,000 default, and one call in seven returned nothing. Two of seven responses carry token accounting that does not add up. Every false finding cost a verification pass, and there were seven of those across the two rows.

**Speed.** 182 s and 189 s on the two rows, a 3. Across the seven runs in the logs the spread is 111 s to 734 s, so the worst case is a 1.

**Disqualifier.** None standing. The shared free pool 429s under concurrency and clears at 120-second serial retries.

**My read.** The only free model with run evidence at volume, and the findings it leads with are the ones that get fixed. The caveats are budget and reliability, not quality: run it at the 100,000 default, expect one empty return in a handful, and read everything it emits because a quarter of it will not hold. It is already rank 1 and nothing in the record argues for moving it.

**Editor's Rating:** ____

**Why:** ____

## nemotron-3-ultra-free (OpenCode Zen, listed)

**Quality.** No fixture digit. 2 of 10 findings real on the exposure gate on 2026-08-30, a matched payload against MiniMax's 7 of 12. The one defect in the file that mattered was filed as UNCERTAIN with "low but non-zero" confidence.

**Cost.** OpenCode publishes no price, so no model USD. 4,872 completion tokens against MiniMax's 30,712 on the same payload, so a sixth of the tokens. Eight refutations for two real findings is the expensive half.

**Speed.** 129 s, a 3.

**Disqualifier.** None. An earlier "never reached" verdict had a mechanical cause, a harness wedge fixed in oxbox, so the model has never failed; it has been run exactly once.

**My read.** One run, low yield, and it hedged the finding that counted. This is the case the decision entry gave as its example of Marginal: it did something, and I would not point a reader at it. A run on a seeded fixture would settle whether the yield or the hedging is the real problem, and that costs nothing at this venue.

**Editor's Rating:** ____

**Why:** ____

## x-preview-f-free, the Ox Alpha listing (OpenCode Zen, delisted)

**Quality.** No fixture digit. 5 of 5 real on one file on 2026-08-24, zero false positives, including a real credential leak in oxbox's redirect path that falsified a claim the maintainer had made in writing. Issue 0.2 had 63 findings at 72 percent on the same weights through OpenRouter's stealth slot.

**Cost.** Free while it lasted. 3,611 prompt and 16,704 completion tokens, 4,935 of them reasoning. Reasoning is billed against the completion budget, which is what broke ox's old 32,000 default and led to the 100,000 default.

**Speed.** Roughly 15 minutes on the one recorded run, a 1.

**Disqualifier.** OpenCode blocked ox's default User-Agent on 2026-08-24; ox was fixed and the run that found the leak happened the same day, so the record shows it cleared. The listing itself is gone: the model was revealed as GLM-5.3 Flash and is in no current snapshot. Same weights are served paid on OpenRouter as z-ai/glm-5.3-flash.

**My read.** The best precision in the record, on a listing that no longer exists. A rating here is for the record, and the manifest question moves to glm-5.3-flash, which is in the open questions below. Note that nothing mechanical currently marks a delisted model as disqualified, so a Good here would pull it into the next manifest. I propose fixing that in the tooling before the next manifest; see the questions.

**Editor's Rating:** ____

**Why:** ____

## mistral/leanstral-1-5 (Requesty, listed)

**Quality.** No fixture digit. 6 findings, 0 real, on the same file where Ox Alpha found 5 of 5. Four were titled BUG and then concluded to be non-defects in their own body. One was factually wrong about Python semantics. Three were the same observation with three contradictory verdicts.

**Cost.** Paid on Requesty; no USD in the record. Roughly a tenth of Ox Alpha's tokens on the same input. Six refutations for zero real findings.

**Speed.** Not recorded in seconds. The observation says fifteen times faster than Ox Alpha on the same input, which would put it around a minute.

**Disqualifier.** None. Requesty accepts chat completions without a deposit.

**My read.** One run, and the output had negative value: acting on its one confident claim would have "fixed" a guard that already works. Its data profile was the most attractive in the survey at the time, which is exactly why it was run, and the run is why the survey stopped ranking on profiles. The decision entry's example of Poor.

**Editor's Rating:** ____

**Why:** ____

## z-ai/glm-5.3-free (ZenMux, delisted)

**Quality.** Answered with nothing. Empty content at both 8,000 and 32,000 token budgets, more than 99.9 percent of each spent on reasoning, finish reason set, no error. The 127,000-character trace circles the exact defect Ox Alpha reported and ends mid-sentence. Under the new rule that is a quality 0, not a disqualifier: the venue served the request and the model produced no review.

**Cost.** Free at the price, but ZenMux gates its free tier on a funded account, so it was uncallable until a deposit was made.

**Speed.** Not recorded.

**Disqualifier.** The deposit gate came from a probe, so it annotates the catalog rather than the row. The listing is gone from the 2026-09-01 ZenMux snapshot.

**My read.** An output problem the catalog cannot see, on a listing that has since vanished. Poor on this evidence, and moot in practice.

**Editor's Rating:** ____

**Why:** ____

## Open questions

1. **glm-5.3-flash is baseline-only.** It sits at rank 2 of the current manifest on the strength of the Ox Alpha reveal, but every run the repo has on it is a baseline, so under the rule it cannot be rated and cannot stay in a manifest dated 2026-09-06 or later. The three fixtures cost under a cent each at its price. Shall I run it as a candidate so it can carry a rating?

2. **Delisted models.** Nothing marks x-preview-f-free or glm-5.3-free as out; a Good on either would pull it into the manifest. I propose that ratings.py treat absence from the newest snapshot of the model's venue as a standing `delisted` disqualifier, dated by that snapshot. The rating then stays on the record and the manifest stays clean. Yes or no?

3. **The cost ceilings.** Every cost digit is a dash until Fable 5.1 runs the three fixtures. At $10 in and $50 out per million, that is on the order of a dollar or two for the set. Shall I run them?
