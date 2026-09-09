<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

# The shape of an issue

**DRAFT.**

What a published issue contains, section by section, and what it never contains.
This replaces the report-format block in the generator, which described the issue by
naming the scripts to run and the tables to paste. That is why the generated issues
read as an audit of the survey rather than a report for a reader.

Read this with `docs/editorial-thesis.md`, which says what the survey is for. This
file says what that looks like on the page.

## The one rule underneath all of it

**Every section describes what a reader gets. No section names a script to run.**

The old block said things like *"`python3 ratings.py` output: every model ever run"*.
An instruction like that cannot be selected against. It orders the complete record
into the reader's path, and no amount of editorial rule upstream can undo it — the
2026-09-08 generated issue printed a twelve-column cost table directly beneath a
sentence quoting the editor's own ruling that twelve-column tables are unreadable in
prose. It knew the rule, cited it, and printed the table, because the format block
told it to.

Scripts still produce the numbers. They produce them into the workbook and into
`docs/`, and the issue quotes the two or three that change a decision.

## Two limits, and the difference between them

**Item counts are capped. Word counts are not.**

A cap on *how many* things appear is selection, and selection is the whole job. A cap
on *how many words* a thing gets is compression, and compression is what welds three
facts into one sentence. Every limit below counts items, sections, columns or rows.
None counts words. When something earns its place, it gets the room it needs.

- At most **10 second-level sections** in an issue. The 2026-09-08 draft had 42
  headings; a reader cannot hold that, and it stops being a report and becomes an
  outline.
- Third-level headings only inside "Top models to try" and the catalog, one per model
  or venue. **No fourth-level headings at all.**
- **No table wider than four columns**, and none longer than the venue's own row
  count. A wider table is a link to the workbook.
- At most **five items** under "What's new this week", **five** under "Top things we
  learned", and **four** models under "Top models to try".

## The sections, in order

### Title and byline

`# The Oxbox Survey`, then a byline line carrying the issue number and date. The
title is the publication's name, not a description of the week.

### What this is

Two sentences, in the same words every week, directly under the byline: what the
survey does, and what task these models are being given — today that is reviewing
public code, run through oxbox. Then a link to the background page for a reader who
wants more than two sentences.

A reader who has never seen an issue should not have to infer the task from the
tables. Keep it to two sentences and a link. The standing explanation lives on the
linked page, not here, and a returning reader skips the block on sight because it has
not changed.

### The opening paragraph

One paragraph, after the two-sentence block and before any section. The single fact
that most changes what a reader does this week, stated plainly, with the number in it.
No further preamble, no table of contents sentence, no methodology.

### Editor's notes

The editor's own, in first person, written by them. The generator leaves the heading
and nothing under it. Every other section is third person.

### What's new this week

Leads the issue. At most five items, each one a thing that changed and that a reader
would act on: a model appeared or vanished, a route stopped answering, a price moved,
a cloaked listing was revealed, a run found something.

Each item is a bold headline fact, then an italic *Why you should care:* line, then
the body. "Unchanged" is not an item. The survey's own tooling is never an item.

### Top things we learned

The top things learned this week: what broke, what workarounds were necessary, etc.
Again, at most five things.

This is the operational half of the thesis and the section nobody else writes. A
model that needs its context halved to answer, a route that only works with a
retry, a flag that has to be set or the run returns nothing — that is what a reader
came for. The distinction from "What's new this week": that section is what changed
in the world, this one is what you have to do about it.

### Top models to try

At most four, free or cheap paid, each one a model the editor would actually point
oxbox at. Per model: a heading carrying the identifier, the venue and the price; a
headline fact; then the "why" as full-width prose, never a cramped column. At most
one four-column table of the numbers that matter.

Do not restate reachability here. A model that failed its probe does not appear.

### What a review cost

**Two or three numbers, in sentences, and a link to the workbook.** What a free
model's findings cost to check, under which checking model, against what a cheap paid
model costs to run and check. Name the checking model every time; a checking cost
without its supervisor is a number without a unit.

The full cost tables, every tier and every supervisor, live in the workbook. The
derivation of the figures lives in `docs/`. Neither belongs in the issue. If a figure
needs a dagger to explain it, the sentence quoting it says the thing the dagger says.

### The models

The catalog as a listing, one table per venue, on a no-change week too. Four columns:
the identifier, the context window, whether it answered, and the limitation that
would bite a reader. Everything else the snapshot carries is in the workbook.

Then a short paragraph only for the entries whose limitation needs explaining.

### The stealth models

One paragraph per cloaked model: slug, listed date, context, the stated free window
and days left, terms, and the attribution with its evidence and the base rate of such
guesses being wrong. One line for the whole section when the slot is empty.

### What models changed since the last issue

Added, delisted, repriced, revealed. One line each. Fold this into "What's new this
week" when the week is thin; two churn sections is one too many.

### How far to trust this

Short, and it leads with the editor's own framing: what was tried here versus what a
vendor said. The sample size, once. The tier labels, once. Anything that would make a
number in this issue misleading, including the standing regulatory bullet.

State a limit once and move on. A defense of the methodology is not a caveat.

### Sources

Every URL fetched and every search run, as named links with a one-line description
each, never bare URLs. Say which were used and which were checked and rejected.

## What never appears in an issue

- **The complete record.** Every model ever run, every fixture score, the rubric, both
  supervisors' cost tables. That is the workbook and `docs/`, and the issue links to
  them.
- **The survey's own adjudication.** How a verdict was settled, which checker
  disagreed, what the rubric argued about.
- **Notes about the survey's tooling.** "The cost script has no as-of filter", "nine
  rows are omitted", "the table carries the entire record to a later date". A reader
  does not know there is a script. If a table is partial, either it is the right table
  or it is the wrong one.
- **Defenses of the methodology.** State the limit once in the trust section.
- **The generator review.** It goes to `docs/generator-reviews/<date>.md`.
- **Anything unchanged since last week.**

## How to tell whether a draft is right

Read the issue as a reader who has not seen a previous one, and answer three
questions. If any answer is no, the draft is not ready.

1. Can you say, after the opening paragraph, what you would do differently this week?
2. Is every table something you would actually read, or are some of them there because
   a script produced them?
3. Does any section explain the survey to you rather than tell you something about the
   models?

Then count: second-level sections at most 10, table columns at most 4, items under
"What's new this week" at most 5, things under "Top things we learned" at most 5, and
models under "Top models to try" at most 4.
