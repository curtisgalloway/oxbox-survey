<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

# Verifier comparison, 2026-09-20: eight arms, two routers, and 67 findings

The method is in [decisions.md](decisions.md) under "Comparing verifiers" and "A
cheap verifier is tested against a cheap verifier, and the router is an arm".
This is the result of the second run, and the first on the extended key.

**Not an observation, on purpose**, for the reason the
[2026-09-03 run](verifier-comparison-2026-09-03.md) gives: this is about the
survey's own machinery, the reviewing agent rather than a reviewed model, and
the `model:`/`role:` fields have no honest value here.

## What was run

Every finding the survey has recorded an adjudicated verdict for at pin
`6302b12` on `oxbox-clean-control`: **67 findings in 14 batches**, up from 15 in
5. Eight arms replayed them under
[`corpora/prompts/verify-findings.txt`](../corpora/prompts/verify-findings.txt),
all toolless, all on byte-identical payloads, none of them running anything.

| arm | model | venue | billed |
|---|---|---|---|
| `or-opus` | `anthropic/claude-opus-5` | ox / OpenRouter | $4.0127 |
| `or-glm` | `z-ai/glm-5.3-flash` | ox / OpenRouter, pinned | $0.0438 |
| `or-deepseek` | `deepseek/deepseek-v4-flash` | ox / OpenRouter, pinned | $0.0110 |
| `free-ling-vl` | `inclusionai/ling-3.0-flash-vl:free` | ox / OpenRouter | $0 |
| `free-dots` | `dots-studio/dots-3-note-preview:free` | ox / OpenRouter | $0 |
| `local-qwen38` | `qwen3.8:27b-64k` | ollama, local | $0 |
| `local-gptoss` | `gpt-oss:20b-64k` | ollama, local | $0 |
| `local-gemma4` | `gemma4:26b-64k` | ollama, local | $0 |

Two arms did not finish every batch, and the reason is the result rather than a
gap in it. `free-dots` failed 6 of 14, all `finish=length`: the free model spent
its whole 32,768-token cap reasoning and returned nothing, which is the free
pool's documented failure on this corpus. `or-glm` failed 5 on the first pass
and 3 after retries: the two recovered ones were a 1Password TLS handshake
timeout and a 900-second read timeout, both infrastructure; the three that
stand are `finish=length` at effort `max` on the three largest batches, which
is the 32,768-token cap doing what the decision entry said it might. `or-glm`'s
figures below are over the **11 batches** it completed, and a rate over 33 rows
is not comparable to one over 67.

## The list a human would have to read

The figure that matters, because a supervisor's job is filtering inventions out
and an arm that confirms everything has moved the cost rather than removed it.

| arm | confirmed | of which real | precision | recall |
|---|---|---|---|---|
| **`casc/qwen38`** (router) | 11 | 8 | **73%** | 2 of 2 |
| **`casc/glm`** (router, 11 batches) | 10 | 7 | **70%** | 2 of 2 |
| `or-opus` | 19 | 10 | 53% | 2 of 2 |
| `disa/qwen38+deepseek` (router) | 17 | 9 | 53% | 2 of 2 |
| `casc/deepseek` (router) | 10 | 5 | 50% | 2 of 2 |
| `local-qwen38` | 16 | 8 | 50% | 2 of 2 |
| `free-dots` | 4 | 2 | 50% | 2 of 2 |
| `or-glm` (11 batches) | 15 | 7 | 47% | 2 of 2 |
| `free-ling-vl` | 21 | 6 | 29% | 2 of 2 |
| `or-deepseek` | 17 | 3 | 18% | 2 of 2 |
| `local-gptoss` | 22 | 4 | 18% | 1 of 2 |
| `local-gemma4` | 56 | 10 | 18% | 2 of 2 |

**Read the recall column as nearly empty.** The corpus holds two real defects, so
every "2 of 2" is a two-item sample and the only arm to miss one is
`local-gptoss`. Precision is where the information is.

## The cheap arm is not the reckless one, and one cheap arm is the worst

`local-gemma4` is what the parent decision predicted in the abstract and had
never seen: it confirmed **56 of 67** findings, reached full recall by refusing
almost nothing, and handed back a list longer than the one it was given. It
costs nothing and saves nothing.

`local-qwen38` is the opposite, and it is the result worth arguing about. A
27-billion-parameter open-weight model on a Mac Studio, billing zero, scored **57
of 67** against the key at 50% precision and full recall -- and 84% on the 57 rows
its own model did not emit as a candidate, so the score is not self-flattery.

## Opus cannot be ranked here, and that is the finding

`or-opus` scored 58 of 67. It also **wrote 52 of those 67 rows**: the recorded
verdicts in the key were reached by Fable 5.1 and Opus 5, and after the
extension nearly every new row is theirs. On the 15 rows its own model did not
produce, it scored 10 -- 67%.

Do not read that 67% as Opus being worse than a free local model. The 15
residual rows are **not a random sample**: they are the 11 original Fable-verified
rows plus exactly the four the record contests -- C3, refuted after being
reproduced rather than read; M1 and M2, confirmed by both metered checkers and
refuted under the ruling that reproduction produced; and F4, the standing
dissent where the metered Opus check refuted a finding the record keeps real.
The residue is enriched for rows where careful reading is known to have failed.

The honest statement is narrower and more useful than a ranking: **this key
cannot measure Opus at all.** Its verdicts are Opus's own on four rows in five,
and what is left is the hard tail. The cheap arms author nothing here, so they
are the only arms this key scores cleanly -- a structural advantage, and the
reason the parent section's bar stands unchanged.

## The cascade beats every single arm; the consensus router beats none

| router | shape | escalated | precision | cost |
|---|---|---|---|---|
| `casc/qwen38` | cheap REFUTED stands, else escalate | 10 of 14 batches | **73%** | $3.34 |
| `casc/glm` | same, with the cheap paid arm | 8 of 11 | **70%** | $2.24, really $3.34 |
| `casc/deepseek` | same, with the other cheap paid arm | 10 of 14 | 50% | $2.88 |
| `disa/qwen38+deepseek` | agree and act, differ and escalate | 11 of 14 | 53% | $3.55 |
| `or-opus` alone | -- | -- | 53% | $4.01 |

`casc/glm`'s printed $2.24 is **too low and must not be quoted on its own.** The
three batches GLM never completed contribute no escalation, so the router pays
nothing for them -- but a refuter that returns nothing escalates everything, and
in production those three go to the frontier in full. Adding their `or-opus`
batch costs ($0.4169, $0.3260, $0.3525) brings it to $3.34, the same place the
free local refuter lands. The saving is about 17%, not 44%.

**The cascade is the survey's own procedure and nothing had ever measured it.**
`observations/README.md`'s checking order -- reproduce first, then a cheap
refuter, then the metered frontier on whatever survived -- comes out at 73%
precision with a free local refuter in front and 70% with a cheap paid one,
seventeen to twenty points above the frontier model on its own. It gets there by
being asymmetric: it spends nothing on a row the cheap arm killed, and its whole
exposure is a cheap arm refuting a real defect. On this corpus neither refuter
ever did.

**Two unrelated refuters landing in the same place is the reason to believe it.**
`qwen3.8:27b` on local hardware and `z-ai/glm-5.3-flash` through OpenRouter share
no vendor, no venue and no weights, and the cascade gains about the same with
either. One arm at 73% would be a fact about that arm.

**But the cascade is only as good as the refuter's precision.** `casc/deepseek`
gains nothing -- 50%, a point below the frontier alone -- and DeepSeek V4 Flash is
the weakest refuter measured, at 18% on its own. A refuter that confirms
indiscriminately escalates indiscriminately, and hands back the frontier's number
with an extra request in front of it. The choice of cheap model is the whole
decision; "use a cheap model" is not.

**The symmetric router buys nothing.** Acting on what two independent arms agree
about and escalating where they differ lands on 53% precision -- identical to the
frontier model alone -- while escalating *more* batches (11 of 14) and costing
*more* ($3.55 against $4.01, a 12% saving for a procedure with two extra moving
parts). Agreement between two readers who share a prior is not a second opinion,
and the 2026-09-03 run's P2 row already showed the shape of it: two independent
arms agreed and were both wrong. S1 is this run's version -- the key refutes it,
and six of the eight arms confirmed it, including every free and local one.

**The saving is smaller than the escalation rate suggests, and the escalation
rate is the whole story.** Ten of fourteen batches escalated, so the cheap arm
avoided the frontier's bill on four. The evidence payload is the five pinned
files and it dominates the prompt, so an escalated batch re-sends all of it and
is charged in full. A router that escalates 71% of its batches is a frontier
pipeline with a cheap pre-filter attached, and it should be described that way.

What it is *not* is expensive: the cheap half of the whole comparison came to
**8.1 cents** -- $0.0704 for eleven GLM batches and $0.0110 for fourteen DeepSeek
batches -- against $4.01 for one pass of Opus. About 1% of the bill, for the arm
that does the filtering.

## How far to trust this

One run per arm per batch, on 2026-09-20 and 2026-09-21, all replay. Replay
measures agreement with a past judgment and is not the judgment itself; nothing
here is a live verification of anything.

The key is one fixture, one pin, and two real defects. Precision is measured over
67 findings and is worth something; recall is measured over two defects and is
not.

Four key rows disagree with their own observation's original count, because
every later correction is applied: OPUS1, C3, F2, F3. The batch notes say so.

Both cost columns are reported. `usd` is computed from the archived catalog and
`venue` is OpenRouter's own `usage.cost`; for the cheap arms they differ by about
a third in opposite directions on the two models, which is a catalog-versus-venue
gap and not a measurement of either.

**Nothing here adopts a cheap supervisor.** The bar in "Comparing verifiers"
stands: an arm that matches on this record still has to be shown on a batch with
no key before it can take the standing supervisor's job.
