<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

# What the survey is for

The standing answer to "why does this exist, and what belongs in it". The generator
reads this; see `.claude/skills/oxbox-survey/SKILL.md`, "What the report is for, and
what earns a place in it", which is drawn from it.

## The thesis

**The value is operational, not evaluative.** In the editor's words, 2026-09-08:

> I want this to be most useful and not duplicate just measuring models — focusing on
> the practical aspects of "OK, here's what you have to do to make this work and be
> cost-effective" is the value.

Others measure models at a scale this survey will never reach. Artificial Analysis
prices and benchmarks them. SWE-PRBench scores review quality against 350
human-annotated pull requests. A survey with a handful of fixtures and one reviewer's
repositories cannot out-measure either, and an issue that tries is a worse version of
work that already exists.

What none of them tells a reader is what you have to *do* to make a cheap model work,
and whether it pays.

> **We try inexpensive models on real code, verify what they claim, and report whether
> the useful findings were worth the trouble.**

The measurement is the evidence for that claim. It is not the product.

## Who the reader is

The editor, 2026-09-09:

> The reader doesn't care particularly about 'oxbox' and how the tool works; they are
> interested in free and cheap models, how they perform, what works well and what
> doesn't, which routers work well, etc. Bugs in oxbox, things we changed there, don't
> hold their interest so much.

So the reader is an engineer choosing a free or cheap model to point at code this
week, from their own code or their own tools. What they came for: which models answer
and how they perform, what works and what does not, which routers and gateways work
well, and what it costs to check the output. What they did not come for: how oxbox
works, bugs found in oxbox, what oxbox changed.

The survey's own code is only the specimen the models are tried on. A finding in it is
evidence about the model, and that is the sole reason it appears: name the model, the
finding, and whether it held up, and leave out the commit, the harness internals and
the fix timing. **The test for every item: does it tell the reader something about a
model, a router or a cost?** If it tells them something about oxbox, it is out.

## The five things that earn space

- **Access.** Does it answer, through the route a reader can actually reach, today.
- **Usable output.** Did it finish a review, honor the format, produce a patch that
  applies.
- **Verification burden.** What it took to sort real findings from invented ones, in
  money and attention. The number that decides whether a free model is cheap, and one
  almost nobody else reports.
- **What changed.** Appeared, vanished, slowed, repriced, started refusing. Week over
  week is evidence no single benchmark run produces.
- **One inspectable incident.** A finding, its reproduction, its verdict, and what
  changed because of it.

## Where this came from

A Codex session in this repository, 2026-09-08 09:41, in which the editor asked:

> what is your opinion of the overall usefulness of this survey, compared to other
> existing model evaluations out in the world?

The reply is worth keeping in full because two of its judgments became rules:

> **I think it is worth continuing, but its strongest product is a field report for
> people choosing inexpensive code reviewers. Its present evidence is too narrow to
> support a general model leaderboard.**

> The real defects found in your code are compelling evidence that individual runs
> helped. They are much weaker evidence that the winning model will outperform another
> model next week or on another repository. I would make that distinction central to
> the publication.

> My biggest concern is the **maintenance effort relative to the information gained**.
> Eleven review rounds, repeated adjudication of the same ambiguous findings, and
> elaborate cost buckets around a handful of fixtures suggest that the machinery is
> consuming more attention than the sample can repay.

And its recommended change of emphasis, which is now the selection rule:

> - Lead each edition with what changed and what a reader should do differently.
> - Make recommendations specific to a task and tested route, with provisional
>   confidence.
> - Keep a small, stable acceptance suite and repeated trials for serious candidates.
> - Use external evaluations to shortlist candidates and provide context.
> - Spend most verification effort on fresh, realistic reviews and consequential
>   failures.
> - Keep detailed adjudication available as supporting evidence, with less of it in
>   the reader's path.

It also moderated its own earlier advice on outside datasets, which is why `docs/
editor-ratings-review-2026-09-06.md` adopts a pinned slice rather than a whole
benchmark:

> a public slice could improve calibration, but a large vulnerability benchmark should
> not become the survey's main project.

## Why this file exists at all

The test-set half of that session reached the repository the same day, as Q7 and Q8 in
the r11 review. The editorial half did not, and was recoverable on 2026-09-08 only by
reading the Codex session rollout on the editor's laptop.

That is the third time direction for this generator has been found stranded outside it:

1. The voice rules the editor gave across the 2026-08-27 review rounds went to
   `docs/generator-reviews/2026-09-01.md`, which nothing read back.
2. The style rules of 2026-08-27 went to an agent's private memory file, so they
   reached a session only when that memory happened to load.
3. This thesis stayed in a Codex transcript.

Meanwhile the generator carried 520 lines on evidence tiers, manifest derivation,
provider pins and cost tables, and nothing on what a reader finds interesting — so it
wrote what it was told to write. The three generated issues of 2026-09-08 ran to 5,500
and 7,500 prose words of adjudication detail against a published issue's 3,900, and the
editor's verdict on them was that they "go way deep into detail that is not relevant to
the interesting things we're trying to communicate".

**A rule that lives outside the generator is not a rule.** Direction belongs here or in
`SKILL.md`, and the generator is now told to read both.
