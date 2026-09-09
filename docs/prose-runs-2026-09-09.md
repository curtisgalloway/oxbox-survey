<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

# Prose runs under generator 2.7.0, measured 2026-09-09

Four prose arms, one set of facts. Every arm wrote from the same intermediate, the
one the 2.6.0 Opus content pass produced on 2026-09-08, so the writer is the only
variable. Read this with `docs/prose-baseline-2026-09-08.md`, which is the
before-picture, and `docs/issue-shape.md`, which is what the arms were checked
against.

```
python3 scripts/generate_issue.py --arm <arm> --date 2026-09-01 \
    --intermediate work/v26/2026-09-01-opus-5.intermediate.json --out work/v27-prose
python3 scripts/prose_metrics.py ../oxbox.ai/editions/2026-09-01.md work/v27-prose/*.issue.md
```

## Why this run exists

The 2.6.0 run was the first to meet every count in `docs/issue-shape.md`, and it still
paraphrased the approved format: "New this week" for "What's new this week", "Caveats"
for "How far to trust this", the models ahead of the lessons, "What this is" promoted
to a section, no "Editor's notes" heading. The cause was mechanical. The prose pass is
handed the skill's "Report format" block, which had become a pointer to the spec, and
the prose pass by design has no file tools to follow a pointer with. It inferred the
shape from the pointer and from the stale paragraphs beneath it.

2.7.0 pastes the spec into the prompt whole and hands the writer the ten headings
verbatim and numbered (`SECTIONS` in `scripts/generate_issue.py`, checked against the
spec by `surveytest.py`). The two-sentence block under the byline is now fixed text in
SKILL.md, so it is the same words every week.

## Shape

Every arm: title `The Oxbox Survey`, the fixed byline block, one lead paragraph, an
empty "Editor's notes", then the ten second-level headings in the spec's order with
the spec's words. No fourth-level headings. Five items under "What's new this week",
five under "Top things we learned", one model under "Top models to try" (the
intermediate carries one). Every "What's new" item has its bold headline and its
italic *Why you should care:* line; Astra wrote them as a numbered list, the Claude
arms as paragraphs.

| arm | H2 | H3 | tables | widest | prose-pass cost | seconds |
|---|---|---|---|---|---|---|
| opus-5 | 10 | 4 | 4 | 4 | $1.01 | 105 |
| fable-low | 10 | 4 | 6 | 4 | $2.14 | 136 |
| fable-high | 10 | 5 | 4 | 4 | $2.37 | 198 |
| astra | 10 | 5 | 4 | 4 | subscription | 238 |

Every arm answered as a single model (`uniform: yes` in each `.meta.json`); none was
mixed. The two extra tables in fable-low are the same two the 2.6.0 Opus run had
under "What a review cost", both within four columns.

## Prose

| issue | prose words | sents | median | p90 | >30w | nominal /1k | slop |
|---|---|---|---|---|---|---|---|
| published 2026-09-01 (1) | 3929 | 220 | 16 | 34 | 14% | 15.3 | 1 |
| 2.6.0 opus-5 | 2953 | 258 | 11 | 20 | 0% | 16.6 | 3 |
| 2.6.0 astra | 2552 | 361 | 7 | 12 | 0% | 17.2 | 3 |
| 2.7.0 opus-5 | 2770 | 212 | 13 | 24 | 2% | 15.2 | 2 |
| 2.7.0 fable-low | 2958 | 266 | 10 | 19 | 2% | 16.2 | 2 |
| 2.7.0 fable-high | 3179 | 300 | 10 | 17 | 0% | 16.0 | 2 |
| 2.7.0 astra | 2695 | 367 | 7 | 13 | 0% | 15.6 | 1 |

Every arm is shorter than the published issue and every arm has cut the long-sentence
share from 14% to 2% or under. The numbers no longer separate the arms much; what
separates them now is what a reader would notice, and that is the editor's read, not
a metric.

## What to read for

- **Opus** is the shortest and cheapest of the Claude arms and the most literal about
  the shape.
- **Fable high** is the only arm whose lead paragraph ends by telling the reader what
  to do ("pick from the six named below"), which is the spec's first test of a draft.
  It folded the edition-history sentences into the byline line.
- **Fable low** added a second preamble paragraph after the lead, which the spec does
  not allow, and kept the two extra cost tables. Otherwise indistinguishable from
  Fable high on the numbers, at nearly the same price.
- **Astra** writes the shortest sentences by a wide margin (median 7 words, 367 of
  them). Whether that reads as clear or as choppy is the thing to check; the metrics
  cannot say.

## What this run does not show

- The content pass was not rerun. The 2.7.0 `CONTENT_PROMPT` names `lead` and
  `lessons` and orders its keys by the spec; the intermediate these arms wrote from
  predates that and has no `lead`, so each writer chose its own opening fact. All four
  chose the same one.
- Only 2026-09-01 has been regenerated. 2026-08-24 and 2026-08-27 are still owed.

## Later the same day: the AI Weekly Survey framing (2.8.0)

The editor read the 2026-09-09 issue of their other weekly and asked for its framing
here: compact highlights up top, items in a fixed form, the long detail behind a link.
`docs/issue-shape.md` was redrawn (commit d715a83 and the one after it) and Opus was
run twice against the same 2.6.0 intermediate.

| draft | prose words | top half | record | tables above the rule | anchor links | cost |
|---|---|---|---|---|---|---|
| 2.7.0 opus-5 | 2770 | — | — | 4 | 0 | $1.01 |
| 2.8.0 first pass | 3499 | — | — | 0 | 5 | $1.61 |
| 2.8.0 second pass | 3231 | 2148 | 3016 | 0 | 14 | $1.02 |

The first pass under 2.8.0 came out 26% longer than 2.7.0 because the prose prompt
still required every fact in the intermediate to appear in the issue and the record
had no place for per-run detail, so the writer nested the row lists, token counts and
per-run breakdowns inside the items. The second pass followed one added rule, *the
item is the claim; the record is the evidence*, and a fifth part of the record, "The
runs", to hold it. Every item above the rule is now headline, one or two sentences,
an italic *Why it matters:* line and sources, and links down by anchor. The five
highlights are 134 words. The top half is 2148 words, of which the trust section's
standing regulatory bullets are a large fixed share.

Both drafts are in `work/v28-prose/` and `work/v28b-prose/`. Awaiting the editor's
read, and a Doc review round of the revised shape.
