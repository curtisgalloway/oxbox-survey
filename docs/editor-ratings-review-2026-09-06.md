<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

# Editor's Rating review

The Editor's Rating column, for the editor to fill in. Every model the survey has put through ox is below with what the record measured on each dimension, my read of it, and a slot for the rating. The digits are bucketed by `ratings.py` from observation frontmatter and are not opinions. The rating is yours and the tools only read it.

**How to rate.** Under each model, replace the blank after **Editor's Rating** with one of Good, Acceptable, Marginal, Poor, and write a line after **Why**. That line becomes the manifest's `why` field, so write it for a reader of the survey. Leave a margin comment for anything else. Good and Acceptable go into the next manifest, Goods above Acceptables. Marginal and Poor stay out.

**Where the digits stand.** The cost digit now exists on ask-grounding: Fable 5.1 ran it at $0.2756, so that fixture's ceiling is $0.0276 per hit. It cannot exist on the scanner fix, because Fable refuses that prompt outright (content filter, twice, no tokens billed). It does not yet exist on the clean control or on real-work batches, because the verification half there is a shared session window rather than a per-run figure. The quality digit exists only on fixtures with a seeded answer set, so it is a dash for every free candidate, whose runs were on review batches with no such set. For those you are rating on the raw column, real findings over findings emitted, plus speed, plus the color.

Backticks around model names do not survive the conversion to a Doc; ignore that.

## The rubric

| Dimension | Measured | 5 | 4 | 3 | 2 | 1 | 0 |
|---|---|---|---|---|---|---|---|
| Quality | seeded defects found, of those present | all | 3/4 or more | half or more | a quarter or more | any | none, or no output |
| Cost | USD per real finding or hit, both halves, against the fixture's Fable 5.1 ceiling | under 1/100 | under 1/10 | under 1x | up to 3x | up to 10x | over 10x, or nothing real |
| Speed | wall clock per run | under 30 s | under 2 min | under 5 min | under 10 min | under 20 min | 20 min or more, or timed out |

## What the scale looks like: the paid baselines

Reference rows, never rated, never in the manifest. They show what a 5 and a 0 look like on the same fixtures. Fable 5.1 is the price ceiling, so its own cost digit is a 2 by construction.

| Model | Fixture | Quality | Cost | Speed | Real / findings | Model USD |
|---|---|---|---|---|---|---|
| claude-fable-5.1 | ask-grounding | 5 | 2 | 4 | | $0.2756 |
| claude-fable-5.1 | secret-scanner-fix | refused | | | | $0 |
| claude-fable-5.1 | clean-control | | | 4 | 2 / 5 | $0.3663 |
| gpt-5.6-sol | ask-grounding | 5 | 4 | 5 | | $0.0273 |
| gpt-5.6-sol | secret-scanner-fix | 5 | | 4 | | $0.0392 |
| gpt-5.6-sol | clean-control | | | 3 | 1 / 8 | $0.0861 |
| claude-sonnet-5 | ask-grounding | 5 | 3 | 5 | | $0.0416 |
| claude-sonnet-5 | secret-scanner-fix | 0 | | 3 | | $0.1845 |
| claude-sonnet-5 | clean-control | | | 3 | 0 / 2 | $0.1611 |
| gemini-3.7-flash | ask-grounding | 5 | 4 | 4 | | $0.0183 |
| gemini-3.7-flash | secret-scanner-fix | 5 | | 2 | | $0.1531 |
| gemini-3.7-flash | clean-control | | | 3 | 1 / 1 | $0.0620 |
| deepseek-v4-flash | ask-grounding | 5 | 5 | 5 | | $0.0009 |
| deepseek-v4-flash | secret-scanner-fix | 0 | | 0 | | $0.0014 |
| deepseek-v4-flash | clean-control | | | 2 | 0 / 0 | $0.0005 |

Sonnet's 0 on the scanner fix is a wrong hunk header, so the patch does not apply, plus a self-hit. DeepSeek's 0 is the same apply failure and a 21-minute wall clock. Ask-grounding is saturated, seven models at 10 of 10, so a 5 there says little and the cost digit is what separates them. Fable on the clean control is the first model to find both known defects at that pin, both hedged UNCERTAIN, with one invention.

## minimax/minimax-m3:free (OpenRouter, listed, rank 1 of the current manifest)

**Quality.** No quality digit, no seeded set. Real work: 13 of 15 findings real across two review batches on oxbox on 2026-08-29, two of them fixed within the hour. 7 of 12 on the exposure gate on 2026-08-30, where a reframed prompt found the cross-host redirect the neutral prompt missed, fixed the same afternoon. Three more batches that day, not rows because they were verified by the fixes that shipped rather than by a review pass: six findings confirmed, one UNCERTAIN refuted, the rest unverified. The table shows 20 real of 27 across the two rows.

**Cost.** Free. Both halves are not per-run in the record, so no cost digit. The reasoning share is the story: 98 percent of completion tokens went to thinking across seven runs, the largest run used 84 percent of the 100,000 default, and one call in seven returned nothing. Two of seven responses carry token accounting that does not add up. Every false finding cost a verification pass, and there were seven of those across the two rows.

**Speed.** 182 s and 189 s on the two rows, a 3. Across the seven runs in the logs the spread is 111 s to 734 s, so the worst case is a 1.

**Disqualifier.** None standing. The shared free pool 429s under concurrency and clears at 120-second serial retries.

**My read.** The only free model with run evidence at volume, and the findings it leads with are the ones that get fixed. The caveats are budget and reliability, not quality: run it at the 100,000 default, expect one empty return in a handful, and read everything it emits because a quarter of it will not hold. It is already rank 1 and nothing in the record argues for moving it.

**Editor's Rating:** Good

**Why:** Decent performance, OK speed.

## z-ai/glm-5.3-flash (OpenRouter, paid, rank 2 of the current manifest; new candidate rows this round)

**Quality.** Run as a candidate on all three fixtures this afternoon, at your direction. Ask-grounding: 10 of 10 in 25 seconds, a 5. Scanner fix: corrupt hunk header, the patch does not apply without a recount, all 8 verdicts hold and zero self-hits behind it, but gate 1 is the gate, a 0. Clean control: 4 findings, 1 real, 3 inventions. The same model ran the same three payloads as a baseline on 2026-09-02 and got a clean apply on the scanner fix and a different one of the two known defects on the clean control. So n=2 on each fixture: one pass and one fail on the mechanical half of a diff, one of two defects each time on the review, and two of its three inventions repeated verbatim.

**Cost.** Ask-grounding at a tenth of a cent, a 5 against the ceiling. Scanner fix $0.0090, no digit because that fixture has no ceiling. Clean control billed $0.0034, double the catalog computation, because OpenRouter routed that one run to SiliconFlow at $0.15 and $0.50 per million instead of Z.AI at $0.075 and $0.25. The catalog price is the price of one route.

**Speed.** 25 s on ask, a 5. 730 s on the scanner fix, a 1, and 544 s as a baseline. 90 s on the clean control, a 4.

**Disqualifier.** None. Vendor note: Z.ai (Zhipu) is on the BIS Entity List, effective 2025-01-16; see the regulatory section below.

**My read.** In ask mode this route is fast, cheap and right, twice. In diff mode it reasons for ten minutes and then miscounts a hunk header half the time. On review it reaches one real defect per run and repeats its inventions. The Ox Alpha evidence that put it at rank 2 was a 5-of-5 review with zero false positives; the paid route has not reproduced that on any fixture, and the clean-control invention rate is the reason to hesitate. Acceptable on the ask and the price; whether diff-mode reliability drags it to Marginal is your call.

**Editor's Rating:** ____

**Why:** ____

## nemotron-3-ultra-free (OpenCode Zen, listed)

**Quality.** No quality digit, no seeded set. 2 of 10 findings real on the exposure gate on 2026-08-30, a matched payload against MiniMax's 7 of 12. The one defect in the file that mattered was filed as UNCERTAIN with "low but non-zero" confidence.

**Cost.** OpenCode publishes no price, so no model USD. 4,872 completion tokens against MiniMax's 30,712 on the same payload, so a sixth of the tokens. Eight refutations for two real findings is the expensive half.

**Speed.** 129 s, a 3.

**Disqualifier.** None. An earlier "never reached" verdict had a mechanical cause, a harness wedge fixed in oxbox, so the model has never failed; it has been run exactly once.

**My read.** One run, low yield, and it hedged the finding that counted. A run on a seeded fixture would settle whether the yield or the hedging is the real problem, and that costs nothing at this venue.

**Editor's Rating:** Poor

**Why:** 2/10 is pretty poor performance.

## x-preview-f-free, the Ox Alpha listing (OpenCode Zen, delisted)

**Quality.** No quality digit, no seeded set. 5 of 5 real on one file on 2026-08-24, zero false positives, including a real credential leak in oxbox's redirect path that falsified a claim the maintainer had made in writing. Issue 0.2 had 63 findings at 72 percent on the same weights through OpenRouter's stealth slot.

**Cost.** Free while it lasted. 3,611 prompt and 16,704 completion tokens, 4,935 of them reasoning. Reasoning is billed against the completion budget, which is what broke ox's old 32,000 default and led to the 100,000 default.

**Speed.** Roughly 15 minutes on the one recorded run, a 1.

**Disqualifier.** OpenCode blocked ox's default User-Agent on 2026-08-24; ox was fixed and the run that found the leak happened the same day, so the record shows it cleared. The listing itself is gone: the model was revealed as GLM-5.3 Flash and is in no current snapshot. Same weights are served paid on OpenRouter as z-ai/glm-5.3-flash, rated above.

**My read.** The best precision in the record, on a listing that no longer exists. Your Marginal keeps it out of the manifest, which is the right outcome for a delisted row whatever the reason; the delisting question below is about making that mechanical.

**Editor's Rating:** Marginal

**Why:** Great performance, terrible speed.

## mistral/leanstral-1-5 (Requesty, listed)

**Quality.** No quality digit, no seeded set. 6 findings, 0 real, on the same file where Ox Alpha found 5 of 5. Four were titled BUG and then concluded to be non-defects in their own body. One was factually wrong about Python semantics. Three were the same observation with three contradictory verdicts.

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

**Why:** ____

## Regulatory exposure

Added at your direction. This is a standing caveat the generator will now carry in every issue, tiered and linked, never as legal advice. What is in the record as of 2026-09-06:

- **BIS Entity List** (Commerce Department export controls). Zhipu AI, the vendor behind the z-ai models including glm-5.3-flash and the Ox Alpha weights, was added effective 2025-01-16 ([Federal Register 2025-00704](https://www.federalregister.gov/documents/2025/01/16/2025-00704/addition-of-entities-to-and-revision-of-entry-on-the-entity-list)). The list restricts supplying listed companies with US-origin items; it does not by itself forbid calling the vendor's hosted API, but procurement and compliance policies commonly key on it.
- **1260H list** (Defense Department, Chinese military companies). The June 2026 update added Alibaba, the vendor behind Qwen, and Baidu ([WilmerHale, 2026-06-11](https://www.wilmerhale.com/en/insights/client-alerts/20260611-pentagon-adds-65-new-entities-to-the-1260h-list-of-chinese-military-companies); [CNBC, 2026-06-09](https://www.cnbc.com/2026/06/09/alibaba-baidu-byd-named-on-pentagons-china-military-list-.html)). It bars the department from contracting with listed companies and, from June 2027, from buying their products through third parties.
- **Pending additions.** You reported that further Chinese AI vendors are on a non-public backlog for Entity List addition. I found no citable source, so the skill carries it as unverified and names no vendor. If you have a link, add it here and I will cite it.

A listing is a card fact: it can never earn a rating and it is not a disqualifier in the table's sense, since the venue serves the model. It is a fact you weigh when rating, and the catalog table will state it in each affected model's limitation column in the same words every week.

## Open questions

1. **glm-5.3-flash** was run as a candidate; its section is above and it can now be rated. Done.

2. **Delisted models.** Still open. Nothing mechanical marks x-preview-f-free or glm-5.3-free as out; your Marginal and Poor keep them out this round, but a Good on a delisted row would pull it into the manifest. I propose that ratings.py treat absence from the newest snapshot of the model's venue as a standing `delisted` disqualifier, dated by that snapshot. Yes or no?

3. **Cost ceilings.** Fable ran all three fixtures. Ask-grounding has its ceiling and every row on it has a cost digit. The scanner fix cannot have one: Fable refuses the prompt as "violative cyber content," twice, and a different ruler for one fixture would make the digits incomparable, so that column stays a dash there. The clean control needs a per-run verification cost before any model's both-halves figure exists; the tooling reports the verification half only as a shared session window today. Two options: accept the dash on human-verified fixtures until costcheck can attribute a window to one run, or define the ceiling there from Fable's model half alone and say so. I lean to the dash.

4. **glm-5.3-free's why.** Your Poor is recorded in the Doc but not yet in the ratings file, because the checks refuse a rating without a why. One line will do.
