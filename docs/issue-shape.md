<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

# The shape of an issue

What a published issue contains, section by section, and what it never contains.
This replaces the report-format block in the generator, which described the issue by
naming the scripts to run and the tables to paste. That is why the generated issues
read as an audit of the survey rather than a report for a reader.

Read this with `docs/editorial-thesis.md`, which says what the survey is for. This
file says what that looks like on the page.

**Revised 2026-09-09** to borrow the framing of the editor's other weekly, the AI
Weekly Survey: a compact set of highlights up top, curated items in a fixed form
underneath, and the long detail behind a link rather than in the reader's path. The
editor's words: *"Keep the tl;dr part pretty compact and link out to the long
detail."*

**A published edition is never changed.** A revision to this shape applies from the
next issue onward; the editions already on the site stay as they were published.
The editor's ruling, 2026-09-09: *"Never change existing editions."*

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

- At most **10 second-level sections** in an issue; the shape below uses eight. The
  2026-09-08 draft had 42 headings; a reader cannot hold that, and it stops being a
  report and becomes an outline.
- Third-level headings only inside "The record", one per venue or per part of the
  record. **No fourth-level headings at all.**
- **No table wider than four columns**, and none longer than the venue's own row
  count. A wider table is a link to the workbook.
- At most **five** highlights, **five** items under "What's new this week", **five**
  under "Top things we learned", and **four** models under "Models we're using this
  week".

## The item form

Everything in the top half of the issue is an item, and every item has the same
four parts, in this order, as one bullet:

1. **A bold headline with the date or the number in it.** "Six of 21 free rows on
   OpenRouter answered", not "OpenRouter availability".
2. **One or two sentences of substance.** What happened, in the evidence tier's own
   words, with the identifier verbatim. The item is the claim; the record is the
   evidence. Anything enumerable behind the claim — the rows that failed and how, the
   token counts, the per-run breakdown, the figures a cost was computed from — goes
   into the record under the part it belongs to, and the item links there. An item
   with a nested list under it is an item that swallowed its evidence.
3. ***Why it matters:*** one sentence, in italics, on what the reader does
   differently. The reader is deciding whether to point a cheap model at a code review
   this week, from their own code; tie it to that, not to the survey. Under "Models
   we're using this week" the line is ***Why this model:*** instead, because there the
   question is why this one and not the next.
4. **The sources**, as named links separated by a middle dot: the model card, the
   announcement, the workbook tab, the part of the record below. A run of the
   survey's own has no public page, so it is named in words ("the survey's
   2026-09-01 run") and not linked.

An item never opens with a framing move and never restates the section it sits in.
A quiet week is fine to say, in one line, and is never padded.

**The reader's problem, not the survey's.** The reader runs these models from their
own code. An item is written as something that will happen to them: "your account's
privacy settings block eight rows", not "this account's data policy"; "a real and
serious vulnerability", not which commit of the survey's own harness fixed it and how
many minutes later. How oxbox works, and what the survey did about a finding in its
own code, is inside baseball. The editor's phrase, 2026-09-09: *"Is there a lesson for
others trying to run these models from their own code?"* If there is not, the item
does not belong.

## The sections, in order

### Title and byline

`# The Oxbox Survey`, then one line: `Issue N, YYYY-MM-DD.` Nothing else. The
editor's ruling on the 2026-09-10 issue: *"Leave info for the highlights. This is
just the header explaining what it is and with the issue number."* The site takes this
line as the archive card's summary and the feed entry's description; that is accepted.

### What this is

Two sentences, in the same words every week, directly under the standfirst: what the
survey does, and what task these models are being given — today that is reviewing
public code, run through oxbox. Then a link to the background page for a reader who
wants more than two sentences. The generator carries the fixed words.

A reader who has never seen an issue should not have to infer the task from the
tables. A returning reader skips the block on sight because it has not changed.

### This week's highlights

The tl;dr, and the first heading. Three to five one-liners, each a bold headline fact
with the number or date in it and then one sentence, drawn from anywhere in the issue
below. This is the section a reader stops at if they read nothing else, and it is
what the highlights email or feed reader carries. Nothing appears here that does not
appear again, with its sources, in an item below.

### Editor's notes

The editor's own, in first person, written by them. The generator leaves the heading
and nothing under it. Every other section is third person.

### What's new this week

At most five items, each one a thing that changed in the world and that a reader
would act on: a model appeared or vanished, a route stopped answering, a price moved,
a cloaked listing was revealed, a run found something. "Unchanged" is not an item.
The survey's own tooling is never an item. The full churn list lives in the record
below; an item here links to it rather than repeating it.

### Top things we learned

At most five items: what broke, the workaround that was necessary, the flag that had
to be set or the run returned nothing. This is the operational half of the thesis and
the section nobody else writes. The distinction from "What's new this week": that
section is what changed in the world, this one is what you have to do about it.

### Models we're using this week

The manifest in prose. This section is the models the editor is actually pointing
oxbox at this week, in the manifest's order, with a link to the manifest, and it is
where the manifest comes from: a model is here because its Editor's Rating puts it in
the manifest, or, until the ratings exist, because a checked run earned it a place and
the section says so. At most four items, free or cheap paid. The headline carries the
identifier, the venue and the price; the substance is the headline fact of its record;
the italic line is *Why this model:*, why this one and not the next. A model's scores
may be quoted in the sentence; the score table itself is in the workbook. Do not
restate reachability here. A model that failed its probe does not appear.

The name was the editor's suggestion on 2026-09-09, replacing "Top models to try":
*"This will turn into the manifest; is there a better framing for it?"*

### What a review cost

**Two or three numbers, in sentences, and a link to the workbook.** What a free
model's findings cost to check, under which checking model, against what a cheap paid
model costs to run and check. Name the checking model every time; a checking cost
without its supervisor is a number without a unit. **Say which bill the reader pays.**
Every figure is at the checking model's list price through the API, and the section
says so once; a reader whose checking model is covered by a subscription pays in quota
rather than dollars, and the section says that too, in one sentence. The two are not
the same cost and the issue never lets one stand for the other. The full cost tables, every tier
and every supervisor, live in the workbook, and the derivation of the figures lives in
`docs/`. Neither belongs in the issue. If a figure needs a dagger to explain it, the
sentence quoting it says the thing the dagger says.

### How far to trust this

Short, and it leads with the editor's own framing: what was tried here versus what a
vendor said. The sample size, once. The tier labels, once. Anything that would make a
number in this issue misleading. The standing regulatory caveat is one line here, that
a model's vendor can be on a United States restricted-party list and nothing in a
catalog card says so, with a link to "Restricted-party listings" in the record, where
the lists and the week's vendors are spelled out. State a limit once and move on. A
defense of the methodology is not a caveat.

### The record

After a horizontal rule. This is the long detail the top half links out to, and a
reader who wants only the report never has to scroll into it. It holds, as
third-level headings in this order:

- **The models.** The catalog as a listing, one table per venue, on a no-change week
  too. Four columns: the identifier, the context window, whether it answered, and the
  limitation that would bite a reader. Then a short paragraph only for the entries
  whose limitation needs explaining. Everything else the snapshot carries is in the
  workbook.
- **The stealth models.** One paragraph per cloaked model: slug, listed date, context,
  the stated free window and days left, terms, and the attribution with its evidence
  and the base rate of such guesses being wrong. One line when the slot is empty, and
  after three consecutive empty issues the line moves into the churn entry and the
  heading goes until a listing appears (generator review 2026-09-10, accepted).
- **What models changed since the last issue.** Added, delisted, repriced, revealed.
  One line each.
- **The runs.** Every run the top half draws on, in date order, one short entry each:
  the model and venue, what was sent, what came back, the counts, the verification
  and who checked it, and the figures behind any cost quoted above. This is where an
  item's facts live in full, and where a reader who doubts a number goes.
- **Restricted-party listings.** The standing regulatory caveat in full: each list,
  what it restricts, the vendors in this week's catalogs that are on it, with a
  primary source per list, and the note that affiliates are not listings. Stated as
  facts about lists, never as legal advice, and it says once that a reader in a
  regulated setting should check the lists themselves. Moved here from the trust
  section at the editor's direction, 2026-09-09.
- **Sources.** Every URL fetched and every search run, as named links with a one-line
  description each, never bare URLs. Say which were used and which were checked and
  rejected.

The site gives every heading an anchor made from its text, lowercased with hyphens
for spaces and punctuation dropped, so an item above links to `#the-models`,
`#the-stealth-models`, `#what-models-changed-since-the-last-issue`, `#the-runs`,
`#restricted-party-listings` or `#sources`.

## What never appears in an issue

- **The complete record in the top half.** Every model ever run, every fixture score,
  the rubric, both supervisors' cost tables. That is the workbook and `docs/`, and the
  issue links to them.
- **The survey's own adjudication.** How a verdict was settled, which checker
  disagreed, what the rubric argued about.
- **Notes about the survey's tooling.** "The cost script has no as-of filter", "nine
  rows are omitted", "the table carries the entire record to a later date". A reader
  does not know there is a script. If a table is partial, either it is the right table
  or it is the wrong one.
- **Defenses of the methodology.** State the limit once in the trust section.
- **The survey's own mistakes.** A verdict the survey got wrong while checking a run
  and then corrected is the survey's own bug, not a lesson for a reader. The editor,
  2026-09-09: *"This feels like our own bug and not that interesting to others."*
- **The generator review.** It goes to `docs/generator-reviews/<date>.md`.
- **Anything unchanged since last week**, outside the record.

## How to tell whether a draft is right

Read the issue as a reader who has not seen a previous one, and answer three
questions. If any answer is no, the draft is not ready.

1. Can you say, after the highlights, what you would do differently this week?
2. Is every table something you would actually read, or are some of them there because
   a script produced them?
3. Does any section above the rule explain the survey to you rather than tell you
   something about the models?
4. Is the most important fact first, in the issue and in every item, the way a wire
   story leads?

The writing is judged by the journalistic framing the survey adopted on 2026-09-08,
not by taste: the base is Associated Press style through the `newsroom-style` skill,
and the departures and additions are the "How to write it" section of the generator,
`.claude/skills/oxbox-survey/SKILL.md`. The inverted pyramid, one idea per sentence,
the claim before its qualification, a finite verb over a nominalization, acronyms
dropped rather than expanded. `scripts/prose_metrics.py` measures the mechanical ones.
What the survey is for, which decides what an item is about, is
`docs/editorial-thesis.md`.

Then count: second-level sections at most 10, table columns at most 4, highlights at
most 5, items under "What's new this week" at most 5, things under "Top things we
learned" at most 5, and models under "Models we're using this week" at most 4. And check the
form: every item has its bold headline, its substance, its *Why it matters:* line and
its sources.
