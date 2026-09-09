<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

# Prose baseline, measured 2026-09-08

The complaint is that issues read dense. This is the measurement taken before any
rules changed, so a later run of `scripts/prose_metrics.py` can be compared against
something rather than against an impression.

Measured over the three issues published before this date. The editions live in the
`oxbox.ai` repo and are all rights reserved, so only numbers are recorded here.

```
python3 scripts/prose_metrics.py ../oxbox.ai/editions/2026-08-24.md \
                                 ../oxbox.ai/editions/2026-08-27.md \
                                 ../oxbox.ai/editions/2026-09-01.md
```

| issue | prose words | sents | median | p90 | >30w | acr | acr unexp | nominal | /1k words | stacks | stacks-x | slop |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-08-24 (0.2) | 1494 | 107 | 12 | 26 | 7% | 10 | 6 | 27 | 18.1 | 0 | 0 | 0 |
| 2026-08-27 (0.3) | 1815 | 110 | 13 | 32 | 13% | 12 | 4 | 34 | 18.7 | 5 | 1 | 0 |
| 2026-09-01 (1) | 3929 | 220 | 16 | 34 | 14% | 4 | 2 | 60 | 15.3 | 6 | 0 | 1 |

Tables, code fences, headings and navigation rows are excluded. A catalog table is
supposed to be dense, and counting it would swamp the paragraphs this is about.

## What the numbers say

**The trend is the finding.** Across three issues the median sentence went 12 → 13 →
16 words, the 90th percentile went 26 → 32 → 34, and the share of sentences over 30
words doubled from 7% to 14%. The issues are getting denser as they get longer, which
is what a reader would report as "harder to read".

**The density is coordination, not vocabulary.** Reading the sentences over 30 words
back, almost none of them is jargon-heavy or abstract. They are concrete, they use
finite verbs, and they weld two or three independent facts together with a semicolon
or an "and". Three examples from issue 1, all from sections a reader actually reads:

- 41 words listing three models' token volumes and Programming ranks. That is a
  three-row table written as a sentence.
- 68 words defining what a manifest is and then what `ox --manifest` does with it.
  Two ideas, one sentence.
- 34 words comparing how two models ranked the same finding, spliced at a semicolon.

**It concentrates in the sections that get read.** By count of sentences over 30
words: "This week's highlights" 8, "What we ran" 4, "Sources" 4, "Top models to try"
3. The two sections a reader opens the issue for are the two densest.

**Two of the six counters do not discriminate on this corpus, and are kept anyway.**

- *Noun stacks.* The raw counter finds 0–6 per issue, and on inspection all but one
  are product names: `Nemotron 3 Ultra`, `Claude Fable 5.1`, `big-pickle OpenCode
  Zen`. A name cannot be broken apart with a preposition, so the `stacks-x` column
  reports the count with name runs excluded — 0, 1, 0. Genuine noun stacks are
  effectively absent. The counter stays as a regression guard.
- *Slop.* One hit in three issues ("not only"). The vendored EQ-Bench list is largely
  fiction slop that a technical report will never emit, so a low count here is weak
  evidence rather than a clean bill. What it is good for is catching a new phrase if
  one starts appearing.

**Nominalizations are counted raw and need reading with `--terms`.** The mechanical
suffix scan cannot tell a nominalization from a domain noun. The top hits in issue 1
are `completion` (8), `evidence` (5), `observation` (4), `severity` (3). `completion`
is almost entirely the card field "max completion tokens", which is a field name and
not a writing choice. Track the rate per 1000 words rather than the raw count, and
read the term list before concluding anything from a move.

**Unexpanded acronyms: two real ones, and an audience call.** The counter skips two
sets. `NOT_ACRONYMS` holds single letters, units and currencies. `ASSUMED_KNOWN`
holds the ones this readership is taken to know already, and that set is the audience
call -- it is provisionally API, JSON, CPU, AI, URL, HTTP, CLI and LLM, and it is
marked `TODO(editor)` in the script because it belongs to whoever knows the readers.
A letter followed by digits is skipped as a model designator, which is what `M3` in
`MiniMax M3` is.

What is left is small and consistent: **GLM in all three issues, SWE in two.** Those
are this report's own vocabulary rather than the industry's, and the rule now says to
expand them every week. The extra hits in the two pre-launch issues are `USE`, `HOLD`,
`AVOID` and `BUG` -- the status markers retired on 2026-09-06, which are all-caps
labels and not acronyms at all.

## What is deliberately not measured

Not Flesch, Flesch-Kincaid, or any grade-level composite. They penalize
`supported_parameters` and "endpoint context" for being long words when those are the
correct words, and they reward a short sentence no matter how many clauses are nested
inside it. On this corpus they are close to noise.
