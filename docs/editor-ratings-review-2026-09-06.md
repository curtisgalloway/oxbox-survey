<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

# Editor's Rating review

The Editor's Rating column, for the editor to fill in. Every model the survey has put through ox is below with what the record measured on each dimension, my read of it, and a slot for the rating. The digits are bucketed by `ratings.py` from observation frontmatter and are not opinions. The rating is yours and the tools only read it.

**How to rate.** Under each model, replace the blank after **Editor's Rating** with one of Good, Acceptable, Marginal, Poor, and write a line after **Why**. That line becomes the manifest's `why` field, so write it for a reader of the survey. Leave a margin comment for anything else. Good and Acceptable go into the next manifest, Goods above Acceptables. Marginal and Poor stay out.

**Where the digits stand.** The cost digit exists on ask-grounding (Fable's ceiling $0.0276 per hit) and now on the clean control ($0.9152 per real finding, from Fable's run plus Fable's own check of it). It cannot exist on the scanner fix: Fable refuses that prompt whatever the framing, and a diagnostic pair showed the task text, not the file, is the trigger. The quality digit exists only on fixtures with a seeded answer set, so it is a dash for every free candidate. Six ratings are in; DeepSeek V4 Flash is the seventh row and awaits yours. The rule derives the next manifest as MiniMax M3 free at rank 1 and GLM-5.3 Flash at rank 2, the current order.

**The cost tables have moved to a Sheet**, one tab per checking model plus the same-batch, per-fixture, ratings and rubric tabs, regenerated from the record each round: [Oxbox Survey costs](https://docs.google.com/spreadsheets/d/1gl6yELjYxiNski90Sqr3gLpZwWeCmZFJzVO8A9dmJ34/edit). This document keeps the same-batch table and the reading.

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

**Quality.** Run as a candidate on all three fixtures, at your direction. Ask-grounding: 10 of 10 in 25 seconds, a 5. Scanner fix: corrupt hunk header, the patch does not apply without a recount, all 8 verdicts hold and zero self-hits behind it, but gate 1 is the gate, a 0. Clean control: 4 findings, 0 real, 4 inventions, after your C3 ruling (below); it had been recorded as 1 real. The same model ran the same three payloads as a baseline on 2026-09-02 and got a clean apply on the scanner fix and one real defect on the clean control. So n=2 on each fixture: one pass and one fail on the mechanical half of a diff, one real finding in eight on the review, and three inventions repeated.

**Cost.** Ask-grounding at a tenth of a cent, a 5 against the ceiling. Scanner fix $0.0090, no digit because that fixture has no ceiling. Clean control billed $0.0034, double the catalog computation, because OpenRouter routed that one run to SiliconFlow at $0.15 and $0.50 per million instead of Z.AI at $0.075 and $0.25. The catalog price is the price of one route.

**Speed.** 25 s on ask, a 5. 730 s on the scanner fix, a 1, and 544 s as a baseline. 90 s on the clean control, a 4.

**Disqualifier.** None. Vendor note: Z.ai (Zhipu) is on the BIS Entity List, effective 2025-01-16; see the regulatory section below.

**My read.** In ask mode this route is fast, cheap and right, twice. In diff mode it reasons for ten minutes and then miscounts a hunk header half the time. On review it reaches one real defect per run and repeats its inventions. The Ox Alpha evidence that put it at rank 2 was a 5-of-5 review with zero false positives; the paid route has not reproduced that on any fixture, and the clean-control invention rate is the reason to hesitate. Acceptable on the ask and the price; whether diff-mode reliability drags it to Marginal is your call.

**Editor's Rating:** Acceptable

**Why:** Fast and mostly good. Z.ai's regulatory status is a concern though.

## deepseek/deepseek-v4-flash (OpenRouter, paid; new candidate rows this round)

**Quality.** Run as a candidate on all three fixtures under your rule that a cheap enough model is a candidate; at $0.07 in and $0.14 out per million it is the cheapest paid row in the survey. Ask-grounding: 10 of 10 in 37 seconds, a 5, terse and right. Scanner fix: corrupt hunk header, the patch does not apply without a recount, 8 of 8 verdicts and zero self-hits behind it, a 0, the same failure as its baseline run and as GLM-5.3 Flash's candidate run. Clean control: no answer at all. It spent 99,999 of 100,000 completion tokens reasoning and returned empty content after 33 minutes, the failure mode GLM-5.3 free showed in August; as a baseline four days earlier it had returned the fixture's ideal empty finding list in five and a half minutes.

**Cost.** Ask-grounding at a tenth of a cent, a 5 against the ceiling. Scanner fix $0.0024, no digit. Clean control $0.016 for nothing. Four runs on OpenRouter went to three different providers at the same list price.

**Speed.** 37 s on ask, a 4. 16 minutes on the scanner fix, a 1. 33 minutes to produce nothing on the clean control, a 0.

**Disqualifier.** None. Vendor note: DeepSeek is not on either list in the regulatory section; you reported a non-public backlog, uncited.

**My read.** On ask mode it is as good as anything in the table and cheaper than all of it. On the two harder fixtures it has now failed the apply gate twice and blown a budget once. That is Marginal on the record as it stands, and the ask result is the reason not to call it Poor; a second clean-control run would tell you whether the blowout is the route or the model.

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

**Why:** It's delisted.

## What it costs, by checking model

The full tables are in the [costs Sheet](https://docs.google.com/spreadsheets/d/1gl6yELjYxiNski90Sqr3gLpZwWeCmZFJzVO8A9dmJ34/edit), one tab per checking model. Your direction to run both Opus 5 and Fable 5.1 as checkers is in force: today every candidate and baseline batch that needed a reader has been checked by both, and the September 2 runs whose checking had been an unmeasured Opus subagent were re-checked by both, so the "unpriced share" caveat you asked about is gone. What replaced it is narrower and permanent: a subagent's output tokens are not in its transcript and cannot be derived from the harness total (the residue came out within two percent of 20,000 on four different checks), so every in-harness checking figure is a floor over input and cache, footnoted as such. The only route to a fully metered checking half is sending the verification through OpenRouter, as the verifier comparison did, which is toolless checking with the evidence inlined, a different job.

The reading: under either checker the model half never decides a run's cost; the checking half does. The free models' checking is the most expensive in the table because their runs were hand-verified real-work batches of ten to twelve findings. Fixture runs scored by a key or a scorer have a zero checking half by rule.

#### The same batch, checked by more than one supervisor

Run `2026-09-03T03-05-25Z`:

| Checker | Input | Output | Cache read | Cache write | USD at own list price | Wall clock |
|---|---|---|---|---|---|---|
| claude-fable-5-1 | 66 | - | 130,427 | 41,989 | $0.5581 | 40 s |
| claude-opus-5 | 16 | - | 440,152 | 47,193 | $0.5151 | 60 s |

Run `2026-09-03T03-20-23Z`:

| Checker | Input | Output | Cache read | Cache write | USD at own list price | Wall clock |
|---|---|---|---|---|---|---|
| claude-fable-5-1 | 98 | - | 193,423 | 46,404 | $0.6294 | 47 s |
| claude-opus-5 | 16 | - | 434,642 | 47,340 | $0.5133 | 61 s |

Run `2026-09-03T03-21-05Z`:

| Checker | Input | Output | Cache read | Cache write | USD at own list price | Wall clock |
|---|---|---|---|---|---|---|
| claude-fable-5-1 | 66 | - | 114,659 | 75,485 | $0.9729 | 90 s |
| claude-opus-5 | 10 | - | 252,658 | 80,094 | $0.6270 | 2 min |

Run `2026-09-06T21-22-57Z`:

| Checker | Input | Output | Cache read | Cache write | USD at own list price | Wall clock |
|---|---|---|---|---|---|---|
| claude-fable-5-1 | 66 | 9,744 (derived) | 114,776 | 75,805 | $1.4641 | 3 min |
| claude-opus-5 | 12 | - | 345,900 | 99,363 | $0.7940 | 6 min |

Derived. claude-fable-5-1: output is the Agent tool's reported total (85,615) minus input and cache writes; plausible against the visible reply, but see the Opus record of the same batch for a case where that derivation fails.

Run `2026-09-06T21-30-07Z`:

| Checker | Input | Output | Cache read | Cache write | USD at own list price | Wall clock |
|---|---|---|---|---|---|---|
| claude-fable-5-1 | 66 | 7,123 (derived) | 114,892 | 75,858 | $1.3338 | 117 s |
| claude-opus-5 | 8 | 10,758 (derived) | 184,557 | 87,230 | $0.9065 | 5 min |

Derived. claude-fable-5-1: output is the Agent tool's reported total (83,047) minus input and cache writes; subagent transcripts do not record final output. claude-opus-5: output is the Agent tool's reported total (97,996) minus input and cache writes; subagent transcripts do not record final output.

## Two checkers, three batches

| Batch | Fable 5.1 | Opus 5 | Record |
|---|---|---|---|
| GLM-5.3 Flash candidate, clean control (C1..C4) | C3 confirmed | C3 refuted | you ruled refuted after the runs |
| Fable 5.1 baseline, clean control (F1..F5) | F1 refuted, F2..F5 confirmed | same, F4 uncertain on host state | F2, F3 counted as true-and-negligible, not real |
| GLM-5.3 Flash baseline, clean control (G1..G4) | all four refuted | G1 confirmed, rest refuted | G1 is real (L1, fixed upstream) |
| Both models' baseline ask-grounding (10 each) | 10 of 10 | 10 of 10 | 10 of 10 |

Nine agreements in ten on the first two batches and one split each way overall. Both splits are the same shape: a finding with the right mechanism and a stated consequence the tree cannot produce. On C3 Fable was generous; on G1 Fable was strict and Opus credited the mechanism, which is what the record and the upstream fix did. The rule says as written, and as written G1's scenario, an offline host certifying a jail that permits egress, needs a jail that permits egress. I have left G1 as the record has it and flag the tension: the same reading that refuted C3 would refute G1.

## The C3 ruling

Two checkers split on finding C3 of the GLM-5.3 Flash clean-control candidate run: Fable 5.1 confirmed it, Opus 5 refuted it. At your direction it was run rather than read again, on argenta (macOS, seatbelt) and dev (Debian 13, bubblewrap), with the `/etc/shadow`-first scenario forced on Linux at an ordinary uid and at uid 0.

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
| ask-grounding | an answer key with line citations, read by a checker | no; seven of ten questions could be executed against the pinned `ox` (defaults, the manifest-version exit, the base_url warning, the payload limit) with a small harness, and the three unsettled ones are the calibration measure by design |
| clean-control | the two known defects can be reproduced (the stat oracle was, today, on both platforms; the offline-host one needs a host with no route), everything else is read | per finding, on demand |
| review-queue, exposure-gate | human verification, and fixes that shipped upstream | no answer key by design |

Reproduce-first is now the rule for any finding whose failure can be run. Making ask-grounding executable would be one small scorer; making the review fixtures executable would mean answer keys, which the corpus rule forbids. Whether to build the ask scorer is a question below.

## Regulatory exposure

Added at your direction. This is a standing caveat the generator will now carry in every issue, tiered and linked, never as legal advice. What is in the record as of 2026-09-06:

- **BIS Entity List** (Commerce Department export controls). Zhipu AI, the vendor behind the z-ai models including glm-5.3-flash and the Ox Alpha weights, was added effective 2025-01-16 ([Federal Register 2025-00704](https://www.federalregister.gov/documents/2025/01/16/2025-00704/addition-of-entities-to-and-revision-of-entry-on-the-entity-list)). The list restricts supplying listed companies with US-origin items; it does not by itself forbid calling the vendor's hosted API, but procurement and compliance policies commonly key on it.
- **1260H list** (Defense Department, Chinese military companies). The June 2026 update added Alibaba, the vendor behind Qwen, and Baidu ([WilmerHale, 2026-06-11](https://www.wilmerhale.com/en/insights/client-alerts/20260611-pentagon-adds-65-new-entities-to-the-1260h-list-of-chinese-military-companies); [CNBC, 2026-06-09](https://www.cnbc.com/2026/06/09/alibaba-baidu-byd-named-on-pentagons-china-military-list-.html)). It bars the department from contracting with listed companies and, from June 2027, from buying their products through third parties.
- **Pending additions.** You reported that further Chinese AI vendors are on a non-public backlog for Entity List addition. I found no citable source, so the skill carries it as unverified and names no vendor. If you have a link, add it here and I will cite it.

A listing is a card fact: it can never earn a rating and it is not a disqualifier in the table's sense, since the venue serves the model. It is a fact you weigh when rating, and the catalog table will state it in each affected model's limitation column in the same words every week.

## Models to try next

Every model below is listed and, where the venue was probed, reachable. Card facts from the 2026-09-01 catalog; nothing here is a rating. The completion cap matters because ox sends 100,000 by default and a lower cap has to go in the manifest's params.

**Free, reachable, never run** (OpenRouter unless noted):

| Model | Context | Completion cap | Reasoning | response_format | Note |
|---|---|---|---|---|---|
| minimax/minimax-m2.7:free | 197K | 177K | yes | yes | the sibling of the rank-1 model |
| cohere/north-mini-code:free | 256K | 64K | yes | no | a code model; no structured output |
| dots-studio/dots-3-note-preview:free | 512K | 461K | yes | yes | also free on ZenMux |
| inclusionai/ling-3.0-flash-fin:free | 262K | 32K | yes | no | Ant Group; low cap |
| google/gemma-4-31b-it:free, gemma-4-26b-a4b-it:free | 262K | 32K | yes | yes | rate-limited at probe time, not closed |
| z-ai/glm-5.2:free | 256K | 230K | yes | yes | rate-limited at probe; Zhipu, Entity List |
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

My suggestion for the first batch: the four reachable free rows plus gpt-oss-120b, mistral-small-2603, nemotron-3.5-lightning and mimo-v2.5, on all three fixtures, both checkers. That is 24 runs at a few cents of model cost and, at today's rates, roughly a dollar of checking per hand-verified batch. Mark the ones you want, strike the ones you do not, and I will queue them.

## Open questions

1. **Reproducible safe-direction failures.** Both checkers confirmed Fable's F2 and F3, which the record counts as true-and-negligible rather than real. With reproduce-first in force those are demonstrable in seconds. Should a confirmed, reproducible, safe-direction failure count as real, count separately, or stay as it is?

2. **G1.** Fable's checker refuted it on the same reading you used to refute C3; Opus, the record and the upstream fix hold it real. Stands, or reversed?

3. **A metered checking half.** The in-harness checkers cannot report output tokens. The verifier comparison already sends verification through OpenRouter, where every token is billed, at the cost of the checker being toolless. Do you want the cost table's checking half measured that way, in-harness with the floor footnote, or both?

4. **An executable ask-grounding.** Seven of its ten questions can be run against the pinned `ox` with a small scorer. Build it?

5. **DeepSeek's clean-control blowout.** One run to StreamLake spent the whole budget reasoning; the baseline run elsewhere did not. Re-run once to separate route from model before you rate it?
