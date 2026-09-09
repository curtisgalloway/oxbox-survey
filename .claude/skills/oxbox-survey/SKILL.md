---
name: oxbox-survey
description: Generate an issue of the Oxbox Survey — a catalog of the free and stealth models on OpenRouter built from measured card facts and their limitations, plus observations from the ones actually run through oxbox that week, plus a self-review of the generator's own rules. Use this whenever the user asks for the weekly free-model report, the stealth model report, "what's free on OpenRouter this week", an update on cloaked models, or when a scheduled routine fires this skill by name. Also use it after ./oxsurvey has written a new snapshot. Also use it when the user asks whether the report rules need revising, or mentions oxbox alongside model selection.
version: 2.8.0
last_generator_review: 2026-09-09
---

<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

# Oxbox Survey — issue generator

Produces two things every run, in this order:

1. **The report** — what the catalog says about every free model and where each one
   will bite you, then what running a few of them actually showed.
2. **The generator review** — whether the rules in this file still fit the landscape.

Never skip part 2. It is the reason this is a skill and not a saved prompt.

## What the report is for, and what earns a place in it

**The value is operational, not evaluative.** Other people measure models, at a scale
this survey will never reach. Artificial Analysis prices and benchmarks them.
SWE-PRBench scores review quality against 350 human-annotated pull requests. A survey
with a handful of fixtures and one reviewer's repositories cannot out-measure either,
and an issue that tries is a worse version of work that already exists.

What none of them tells a reader is what you have to **do** to make a cheap model work,
and whether it pays. That is the product. The measurement is the evidence for it, never
the point of it.

> **We try inexpensive models on real code, verify what they claim, and report whether
> the useful findings were worth the trouble.**

Five things earn space in an issue. All five are operational.

- **Access.** Does it answer, through the route a reader can actually reach, today. A
  listing is not availability, and a price of zero is not access.
- **Usable output.** Did it finish a review, honor the format, produce a patch that
  applies. A model whose answers need repair costs more than its price.
- **Verification burden.** What it took to sort the real findings from the invented
  ones, in money and in an hour of someone's attention. This is the number that decides
  whether a free model is cheap, and almost nobody else reports it.
- **What changed.** Appeared, vanished, got slower, got repriced, started refusing.
  Week over week is evidence no single benchmark run can produce.
- **One inspectable incident.** A specific finding, the reproduction, the verdict, and
  what changed because of it. One told properly beats twenty tallied.

**The selection test, applied to every section, paragraph and table: what does a reader
do differently because this is here?** If the answer is nothing, cut it. The reader is
deciding whether to point a cheap model at their code this week, not auditing how this
survey reached its numbers.

What does **not** earn a place, however much work it took:

- The survey's own adjudication. How a verdict was settled, which checker disagreed,
  what the rubric argued about. It is the maintainer's record and it belongs in
  `docs/`, not in a reader's path.
- Defenses of the methodology. State a limit once, plainly, and move on.
- Process, tooling and version notes about the survey itself.
- Anything unchanged since last week. "Unchanged" is not interesting.
- Exhaustiveness for its own sake. Every fact on hand is not every fact worth printing.

Two consequences worth stating outright, because both cut against an agent's instinct
to be thorough. **An issue is a field report, not a leaderboard** — the real defects
found are strong evidence that a run helped, and weak evidence that the same model wins
next week or on another repository; keep that distinction visible. And **every edition
leads with what changed and what a reader should do differently**, not with the catalog
and not with the survey's own week.

## What this report is, and is not

Two halves, from two different kinds of evidence, and they must not be blended:

- **The catalog** — card facts, captured from the OpenRouter API into `snapshots/`.
  Reproducible: re-run `oxsurvey` and check. It says what is on offer and what the
  limitations are. It says nothing about whether a model is any good.
- **Tried this week** — the user's own `oxbox` runs. Real behavior, small sample, one
  reviewer's repos, and a fixed corpus for the runs that use one
  (`corpora/corpus-manifest.json`) — a run citing a task id is comparable to every
  other run against that id; one that does not is not. It is the only evidence
  here that speaks to quality, and it covers a handful of models at most.

There is **no numbered ranking of the named tier**, and no league table. Nothing in this
repo measures review quality at scale — not the catalog, and not a vendor benchmark
built to score patch generation. A ranking of 22 models on evidence covering two of
them would be a ranking of vibes with a table around it.

**The rule that keeps this honest: a recommendation requires a run.** The
recommendation is the manifest, and the manifest is derived from the Editor's Rating,
which only a tried model can carry. Card facts can put a model on the editor's list of
things to run next; they can never put it in the manifest.

## The job being surveyed for

This is not a general "best free model" list. The consumer is a specific pipeline:

- Models are **untrusted**. They are run through `oxbox` (github.com/curtisgalloway/oxbox):
  no tools array, no shell, no filesystem, no network path back to the machine. They emit
  text; a human reads it.
- The input is **public code only**. Proprietary or unpublished material never reaches
  these endpoints.
- The task is **code review** — `--mode review`, findings not patches — with occasional
  `--mode diff`.

Two consequences:

- **Data terms are a low-weight axis, not a veto.** "Free means you pay in data" is
  already priced in. A model that trains on inputs is acceptable here when it would be
  disqualifying elsewhere. Say so once, explicitly, rather than re-litigating it weekly.
- **Patch-generation benchmarks are not the target.** SWE-Bench and Terminal-Bench
  measure whether a model can produce a working patch. Review quality is a different
  skill: finding real defects, not inventing plausible ones, and saying "uncertain"
  instead of guessing. No public benchmark measures that. This is why benchmarks appear
  in this report only as a labeled aside — see below.

## Part 1 — the catalog

Generated from the newest snapshot, one row per free model. Every value here is
Measured; do not mix in prose from a vendor's card.

Each row carries: model ID; endpoint context **and** the advertised figure when they
differ; max completion tokens; whether `response_format` is in `supported_parameters`;
`expiration_date`; `is_moderated`; listing age from `created`; and a **limitations**
note — the card fact that would actually bite you on a review run. Sort by something
factual and stable (endpoint context, descending) so the table diffs cleanly week over
week.

The limitations note is the point of the section. A 1M-context endpoint with no
`response_format` and a deprecation date in six weeks is a different proposition from
its neighbour in the table, and the row should say which way.

**Benchmarks, if mentioned at all, are one labeled line** — `Vendor-reported: 82.7
Terminal-Bench 2.1` — attached to a model, never a column, never sorted on, never a
reason for a recommendation. If no benchmark is at hand, do not go looking for one.

## Part 2 — tried this week

Only models actually exercised since the last issue, per `observations/` and the oxbox
logs. Cite the observation file for each claim so a reader can check it. For each model,
report what the evidence shows:

- **Findings quality** — how many findings were verified real, how many were false
  positives, and whether it flagged genuine uncertainty instead of bluffing. Give the
  raw counts and the file it ran against. A count of 4/10 verified on one file is a
  usable observation; "good at review" is not.
- **Output hygiene** — did it follow the format contract? Well-formed hunk headers,
  honored context-line counts, parseable structure. A model whose patches only apply
  with `--recount` costs review time on every run.
- **Availability** — what failed, with the exact error. Distinguish an account-level
  refusal from an upstream shared-pool 429; they need different responses.
- **Token efficiency** — the free tier is capped on *requests*, not tokens. A model
  that reaches the same answer in a third of the tokens fits a large review in one call
  instead of three.
- **Card contradicted?** — if served behavior disagreed with the snapshot (context
  truncated below the endpoint figure, a `supported_parameters` entry that errored),
  say so plainly. That is the most valuable single observation the section can produce,
  because it impeaches the catalog.

**Verify by reproducing, not by reading, wherever the failure can be run.** A finding
that says "X happens when Y" is checked by making Y happen against the pin in a jail and
watching for X, on the platform the finding names or on both; the source is read to
decide what to run and to explain the result, not in place of running it. Two capable
checkers reading the same lines reached opposite verdicts on 2026-09-06 and four commands
settled it. The editor's standing direction from that day: reproduction is the default
baseline for a verdict. Record the reproduction as an observation with a `reproduces:`
field. Name both platforms (macOS seatbelt, Linux bubblewrap) when a finding could hold
on one and not the other; the prompts do not, and the models only learn it from the
payload. Two rulings bound what a reproduction refutes (both 2026-09-06): a finding is
refuted when its stated consequence is shown false or needs a state the pin cannot
produce (C3: the FAIL it called false was true), and it is *not* refuted merely because
the property a check certifies happens to hold today when the finding is that the check
cannot fail (G1: a host that is down does not count as the jail succeeding). A test whose
PASS does not depend on what it tests is a defect now.

**A probe is not a run.** An `observations/` file with `source: probe` proves an endpoint
answers; it says nothing about review quality and never gets a row in the catalog
table. Only `source: oxbox-run` carries measured fields, and only a row can be rated.

**If nothing was run this week, say exactly that in one line and move on.** An empty
observations section is an honest report of a quiet week. Do not pad it with last
week's runs or with reasoning about models nobody touched.

## Data to gather each run

Run `./oxsurvey` first. It captures the catalog into `snapshots/<date>.json` and prints
a diff against the previous snapshot, including the revision triggers it detects
mechanically. Read that output before anything else.

Everything part 1 needs is in there already. Fetch by hand only what the API does not
carry:

| Source | URL | What to take |
|---|---|---|
| Stealth listings | `https://openrouter.ai/stealth` | Terms text, stated free-window length, listing notes |
| Free collection | `https://openrouter.ai/collections/free-models` | Token volumes and category ranks (not in the API) |
| Rate limits | OpenRouter rate-limit docs | Any change to the req/min and req/day structure |
| Attribution | Web search for reveals | Whether a previously cloaked model has been claimed |

Then read the two Observed-tier sources, which together are the entire input to part 2:

- **`observations/`** — dated files written by agents during the week. See
  `observations/README.md` for the schema. Read every file newer than the last issue.
- **`providers/`** — standing facts per venue: access gates, API shape, rate limits,
  known quirks. Read these for context before writing the catalog; they explain why a
  model that looks free may not be callable.
- **oxbox run logs** — `logs/*/meta.json` and the review outputs, on the machine that
  holds them.

If neither has anything new, part 2 is one line.

**Read the newest `docs/generator-reviews/<date>.md` before writing, every run.** It
carries the editor's standing direction on voice and on what is interesting, accumulated
over every review round, in their own words. Part 2 writes to that directory; until
2026-09-08 nothing ever read it back, so a week of direction — "too much inside
baseball", "'unchanged' is not interesting", "lead with punchy facts", "always be
humble; we're just doing little toy tests" — sat in a file the generator never opened,
and the issues drifted exactly the way it warned against. A review loop that only writes
is a loop that teaches nothing.

Two standing documents are read every run, and neither is optional.
`docs/editorial-thesis.md` says what the survey is for and is the source of the "What
the report is for" section above. `docs/issue-shape.md` says what that looks like on
the page, section by section, and is the format this skill used to spell out inline.

### Effort, when writing the manifest

The snapshot carries each model's `reasoning` block — `supported_efforts` and
`default_effort`. That is where a manifest entry's `params.effort` comes from, and
it is the only place it may come from. Three states; only the first may be pinned.

- **Publishes `supported_efforts`.** Pin one of those levels. If the pinned level is
  not the model's own `default_effort`, say so in `why` — the difference is a fact
  about the run, not a detail. `z-ai/glm-5.3-flash` is `["max","high","low"]` with
  `default_effort: max`, and every run this survey has on it went out at `high`,
  below its own default.
- **Accepts `reasoning` but not `reasoning_effort`, `supported_efforts: null`.**
  Effort is not a knob on that model; omit the field. `minimax/minimax-m3:free`,
  rank 1 until it was delisted on 2026-09-07, is exactly this case — it reasons, but
  not on a dial.
- **No `reasoning` block at all.** Omit the field.

A venue that publishes no effort data for any model is not a fourth state to guess
at — every `opencode` capture to date carries none — so omit `params.effort` for its
entries. A level learned from an actual run belongs in an observation and may be
cited in `why`; it does not become a pinned param on the strength of one run.

Getting it wrong degrades rather than breaks: `oxbox send` names and drops an effort
it does not recognize, then falls back through explicit flag > entry `params` > manifest
`defaults` > its own default of `high`. That is the reason to pin only what the
snapshot says, not a license to guess — a wrong level runs, and runs wrong, quietly.

`oxbox send`'s ladder is `low`, `medium`, `high`, `xhigh`, `max` (oxbox `41c7c3f`, on
main since 2026-09-03; unchanged in the 1.0.1 Rust binary). Anything else in
`params.effort` is dropped with a warning. The manifest format itself is oxbox's —
its README section "Survey manifests" is the definition, and this skill only fills it.

### Provider pins, when writing the manifest

On OpenRouter a model id is a pool of endpoints at different prices, caps and
failure modes (`providers/openrouter.md`). Since oxbox 1.1.0 (2026-09-07) a
manifest entry may carry a top-level `provider` key — OpenRouter's routing object,
sent verbatim; only the `openrouter` venue honors it, and oxbox skips a pinned
entry on any other venue rather than sending it unpinned. Never put one under
`params` or `defaults`; it is a property of the entry alone.

**A pin is a claim backed by a measurement.** Fill it only from runs this survey
made, and fill it this way:

- `only` — the endpoint slugs the rated runs actually went to, from `route` in
  their `status.json`. Never a slug chosen from the endpoints listing alone.
- `allow_fallbacks: false` — otherwise the pin is a preference and the price is
  not.
- `max_price` — the list price from the snapshot, so a reader who edits the pin
  away still keeps the price guard.

An entry whose runs went to several routes and were rated together carries all
of them in `only`. An entry with no run on this venue carries no `provider`.

**`manifest_version`.** oxbox 1.1.0 reads `1` and still reads `0`; a `0` manifest
carrying `provider` is honored too, and the point of `1` is that an oxbox older
than 1.1.0 refuses it with "update ox" instead of silently dropping the pin.
Publish `0` until the issue's readers can be expected to have 1.1.0, then `1` for
any issue that carries a pin. State the floor ("requires oxbox >= 1.1.0") in the
issue when the first pinned manifest goes out.

## How to write it

**Who is reading.** An engineer who is competent in adjacent areas, is deciding which
free model to point at a code review this week, and has not read a previous issue.
They do not know this report's vocabulary and will not look anything up. Assume they
are skimming for the one fact that changes what they do, and write so that fact is
findable in one pass. Nothing here is written for the person who maintains the
generator.

**The base is Associated Press style.** Follow the `newsroom-style` skill, which states
it: numbers, attribution, abbreviations, restrictive versus nonrestrictive clauses, the
inverted pyramid, short paragraphs, and its red flags — passive voice hiding who did
what, sentences opening "There is" or "There are", "very" and "extremely". Read it
rather than restating it here; what follows is only where this report departs from it,
and what it adds.

AP is the base because this is a report, the conventions are shared, and a rule with a
stylebook behind it survives an argument that a house preference does not.

**Where this report departs from AP, and why.**

- **Dates are ISO 8601.** `2026-09-01`, never "Sept. 1". Every claim here carries an
  as-of date, snapshots are named by date, and issues are diffed week over week; a
  sortable unambiguous date is load-bearing. Astra's 2026-09-08 run converted every date
  to AP form unprompted, which is how this departure was found.
- **Model and vendor identifiers are reproduced verbatim**, in a code span, never
  recapitalized or reflowed: `minimax/minimax-m3:free`, `z-ai/glm-5.3-flash`. AP's
  company-name rule governs a name in prose (Nvidia), not an identifier a reader pastes
  into a command. Getting one wrong is a defect, not a style slip.
- **The serial comma stays.** AP drops it; the items in this report's lists are long and
  technical and misread without it.
- **First person is allowed in the editor's notes, and only there.** That section is the
  editor's, written by a person. AP's red flag against first person governs the rest.
- **The Editor's Rating is a judgment and says so.** "No editorializing" governs the
  reporting; the rating column is the one place an opinion is the product.

AP's numbers rule needs no departure: its own exemption for "tabular matter and
statistical and sequential forms" already covers `2 of 10 findings` and every measured
figure here.

**What AP does not cover, and this report adds.** The rules below. They are mechanical
on purpose — "write clearly" and "avoid jargon" were this file's spirit since issue 0.1
and moved nothing. `scripts/prose_metrics.py` measures conformance, and the baseline is
`docs/prose-baseline-2026-09-08.md`.

- **One idea per sentence.** No sentence carries more than one subordinate clause. Two
  independent clauses joined by a semicolon, or by "and", "but" or "so", are two
  sentences — split them. This is the rule that matters most here: the density in the
  measured issues is almost entirely coordination, not vocabulary.
- **Enumerable facts are a list, never a sentence.** Three or more parallel items — three
  models' token volumes, three findings, three venues' counts — go in a list or a table.
  A sentence that needs semicolons to keep its items apart is a table that lost its
  borders.
- **State the claim, then qualify it in a new sentence.** Not "20 of 27 findings are
  real, including a stale-lock spin at full CPU, a retry path that read the previous
  attempt's status file, and a cross-host redirect that could turn a private
  repository's exposure verdict into public" — instead the count, then the three
  examples as a list.
- **Prefer a finite verb to a nominalization.** "The model degraded on long contexts",
  not "degradation of the model was observed on long contexts." AP's red flag against
  passive voice hiding who did what is the same defect one step further on: a
  nominalization hides the actor *and* the action.

  This is the rule that fails quietly when the others are followed, so it gets a check
  of its own. Astra's 2026-09-08 run had the best sentence-length numbers of any arm —
  nothing over 30 words, median 8 — and the worst nominalization rate, 25.1 per
  thousand words against 15.0 for Opus on the same facts. It shortened its sentences by
  moving the complexity into abstract nouns rather than removing it. **Short sentences
  full of nominalizations are not clear writing; they are the same density in smaller
  pieces.**

  Two tests, both cheap. Every sentence needs a subject that did something: if the
  actor is missing, the verb is hiding in a noun. And when a `-tion`/`-ment`/`-ance`
  word is the object of a weak verb — *perform*, *conduct*, *provide*, *achieve*,
  *observe*, *carry out* — the noun is the real verb, so use it: "we verified the
  findings", never "verification of the findings was performed".

  Watch the rate, not the count, with `python3 scripts/prose_metrics.py --terms`, and
  read the matched terms before believing a move. The scan cannot tell a nominalization
  from a domain noun, and `completion` is almost always the card field "max completion
  tokens" rather than a writing choice.
- **No noun stack longer than two words.** Break it apart with a preposition. A
  product's own name is exempt and is not a stack: `Nemotron 3 Ultra` and
  `Claude Fable 5.1` are names, and there is no preposition to insert.
- **Acronyms follow AP, which is not what an agent's instinct suggests.** Give a name in
  full on first use and the short form after — and **never** the parenthetical-initials
  construction: not "Bureau of Industry and Security (BIS)". AP rejects that form
  outright, and an earlier draft of this file wrongly required it.

  Some are common enough to use unexpanded, as AP allows for CIA and FBI. Here that is
  the ordinary industry vocabulary and the well-known names: API, JSON, CPU, AI, URL,
  HTTP, CLI, LLM, Nvidia, CNBC, GLM. The set the checker holds is `ASSUMED_KNOWN` in
  `scripts/prose_metrics.py`. A model or vendor name is never an acronym: `GLM-5.3`,
  `MiniMax M3`, `SWE-Bench` are names.

  **Where an acronym earns nothing, drop it rather than expand it** — AP's "if it would
  not otherwise be clear, do not use it", and usually the better half of the rule. Name
  the agency a reader has heard of and leave out the org chart: "the United States
  Commerce Department", not the bureau inside it that issued the listing. Spell out
  cryptic abbreviations the same way: "context", not "ctx".

- **Every paragraph opens with a concrete sentence.** A number, a name, or something
  that happened. Never a framing move ("It is worth noting that…", "There are several
  considerations here…") and never an abstraction the next sentence then explains.
- **Say the number in the units a reader thinks in.** K and M in prose (1.31M, 944K);
  exact figures belong in tables and lists.
- **Link on first mention, inline, inside the sentence.** "[Zhipu claimed the
  model](url)", never a parenthetical "(see link)" or a bare URL in the prose.
- **Never name a path inside this repository in reader-facing text.** Say "the survey's
  2026-09-01 snapshot", not `snapshots/openrouter/2026-09-01.json`. The reader cannot
  open it.
- **Em-dashes and italics are rationed.** Both are usually a sentence asking to be two
  sentences.

None of this licenses cutting content. Every fact that would have appeared still
appears; it gets more room, not less. If a section gets longer under these rules, that
is the rules working — the old length was compression, not brevity.

## Report format

**`docs/issue-shape.md` is the format, and it is authoritative.** Read it before
writing. It gives the sections in order, what each one contains, what never appears in
an issue, and the counts a draft is checked against. It was reviewed and approved by
the editor on 2026-09-08, revised 2026-09-09 to the framing of the editor's AI Weekly
Survey (compact highlights up top, items in a fixed form, the long detail behind a
link), and it replaces the block that used to live here.

That block described an issue by naming scripts to run and tables to paste, and that is
why the generated issues read as an audit of the survey. **No section of an issue is
specified by the script that fills it.** Scripts still produce the numbers; they produce
them into the workbook and into `docs/`, and the issue quotes the two or three that
change a decision.

Four things from that document are worth repeating here because they are the ones most
often broken:

- At most **10 second-level sections**; the shape uses eight, the last of them "The
  record", after a horizontal rule, where the catalog, the stealth listing, the churn
  list and the sources live. The top half links down to it and never repeats it.
- **Every item is in the item form**: a bold headline with the date or number in it,
  one or two sentences of substance, an italic *Why it matters:* sentence about what
  the reader does differently, then the sources as named links separated by a middle
  dot. "This week's highlights" is three to five one-liners in the same spirit, and
  it is the section a reader stops at.
- **No table wider than four columns.** A wider one is a link to the workbook.
- **Item counts are capped; word counts never are.** Capping items is selection. Capping
  words is the compression that welds three facts into one sentence.
- **The complete record is not in the issue** — not every model ever run, not both
  supervisors' cost tables, not the rubric, not the derivation of a figure.

**The generator review is not in the issue.** It goes to
`docs/generator-reviews/<date>.md`. See below.

**The section headings are the spec's, verbatim, in the spec's order.** The 2.6.0 run
met every count and still paraphrased: "New this week" for "What's new this week",
"Caveats" for "How far to trust this", the models ahead of the lessons, and "What this
is" promoted to a section of its own. A heading is an identifier. `scripts/generate_issue.py`
carries the list as `SECTIONS` and hands it to the writer with the spec, because the
prose pass cannot open a file and a pointer it cannot follow gets paraphrased.

**The standfirst is a sentence, not a byline.** The site shows the first paragraph
under the title as the archive card and the feed description, so it reads
`Issue N, YYYY-MM-DD.` and then one sentence that is the issue in a breath.

**The two-sentence block under the standfirst**, in these words every week, then the
link:

> The Oxbox Survey catalogs the free and cheap models on the public gateways, tries a
> few of them, and reports what it took to get a usable code review out of each one.
> Every model here was given the same job: review public code, through
> [oxbox](https://github.com/curtisgalloway/oxbox).
> [More about the survey](https://oxbox.ai/survey/).

A returning reader skips it on sight because it has not changed. Everything else a
new reader might want is on the linked page, not here.


**The cost comparison.** Run `python3 ratings.py --costs` for the text form and
`uv run --with openpyxl python3 costsheet.py <out.xlsx>` for the workbook, upload the
workbook to the Oxbox Survey Drive folder (it converts to a Google Sheet, one tab per
checking model plus the same-batch, per-fixture, ratings and rubric tabs), and link the
Sheet from "What a review cost" rather than pasting twelve-column tables into prose;
the editor found the pasted form unreadable (2026-09-06). The issue quotes two or three
numbers in sentences and names the checking model beside each; the same-batch table
appears inline only when it fits in four columns, and the full tables never do. It prints one table per checking model, and the editor's standing
direction (2026-09-06) is to run both Opus 5 and Fable 5.1 as checkers on each verified
batch so both tables fill and a reader can choose; where a run was checked by both, the
same-batch table shows each checker on its own tokens. A second checker is recorded as a
check record (see `observations/README.md`), never by editing the run's observation. It sets the paid frontier baselines, the cheap paid models and the free
models side by side on two halves: what the venue billed for the run, and what the
supervisor's verification window cost at the supervisor's list price with cache reads
and writes, counted once per window. The second half is why a free model is not free,
and the table exists to say so with the record's own numbers. **Always name the
checking model**: the checking half is that model's bill, and there is one table per
checking model for exactly that reason; a checking cost quoted without its supervisor
is a number without a unit. Where a check was metered (the verification task sent
through OpenRouter as one request, `harness_usd` on the check record) the figure is
the venue's bill and the table marks it ‡; say "metered" when quoting one, because a
metered checker reads the source and cannot reproduce anything. Never reprice one supervisor's
tokens at another's rates: the 2026-09-06 matched pair showed Opus 5 spending more
tokens than Fable 5.1 on the same job, so a comparison between supervisors is a second
run, not a multiplication. Never adjust a figure by
hand; if a window is shared or missing, the table says so and the caveat stands.

**The scores, and the Editor's Rating.** `python3 ratings.py` prints the score table,
and the table goes to the workbook beside the cost tables, never into the issue: every
model ever put through oxbox is a row of it, and the issue quotes a model's scores only
where that model appears, under "Top models to try". In the table, failures are rows too: a run the
venue refused shows its disqualifier and dashed scores; a run that answered with
nothing shows quality 0. A `benign` count (confirmed failures in the safe direction) appears beside real when present and is never counted as real. Three 0-5 scores per fixture, bucketed by the script from
observation frontmatter, never typed: quality (seeded defects found), cost (USD per real
defect, both halves, against the fixture's Fable 5.1 ceiling), speed (wall clock). A
dash is unmeasured, never zero. Every score sits beside its fixture id and n, because
the fixtures discriminate unequally. The rubric (`ratings.py --rubric`) is the workbook's
rubric tab, not a section of the issue; the issue says once, where its first score
appears, that the scores are measured and the rating is the editor's.

The Editor's Rating is Good / Acceptable / Marginal / Poor, from `editor-ratings.json`.
**You never write that file.** If a tried model has no rating, the row says `unrated`
and the issue says the editor has not rated it yet; if the rating is older than the
model's newest run, show its date and say so. The manifest follows the rating: Good and
Acceptable are in, Goods ranked above Acceptables in the editor's order, Marginal and
Poor out, and a standing disqualifier holds a model out whatever its rating. Baseline
rows carry no rating and never enter the manifest. **Ratings must not rely on color** —
the word, never a red/green dot as the only carrier of meaning, and never "the green
ones" in prose.

**The standing regulatory-exposure caveat.** Every issue's "How far to trust this"
section carries this, updated to the week's catalog, because a model's vendor can be on a United
States restricted-party list and nothing in a catalog card says so. Added at the
user's direction on 2026-09-06. State it as facts about lists, tiered, with a link to
the primary source for each, and never as legal advice; say once that a reader in a
regulated setting should check the lists themselves and their own procurement rules.

- **The Entity List** (United States Commerce Department export controls) restricts
  supplying listed companies with United States-origin items. Zhipu AI, the vendor behind the
  `z-ai/` models, was added effective 2025-01-16 `[M]`
  ([Federal Register, 2025-00704](https://www.federalregister.gov/documents/2025/01/16/2025-00704/addition-of-entities-to-and-revision-of-entry-on-the-entity-list)).
  Being listed does not by itself forbid a customer from calling the vendor's hosted
  API, but procurement and compliance policies commonly key on the list.
- **The 1260H list** (Defense Department, "Chinese military companies") bars the
  department from contracting with listed companies and, from June 2027, from buying
  their products through third parties. The June 2026 update added Alibaba, the vendor
  behind Qwen, and Baidu `[M]`
  ([WilmerHale, 2026-06-11](https://www.wilmerhale.com/en/insights/client-alerts/20260611-pentagon-adds-65-new-entities-to-the-1260h-list-of-chinese-military-companies);
  [CNBC, 2026-06-09](https://www.cnbc.com/2026/06/09/alibaba-baidu-byd-named-on-pentagons-china-military-list-.html)).
- **Pending additions.** The user reports that further Chinese AI vendors are on a
  non-public backlog for Entity List addition `[?]`. No citable source as of
  2026-09-06; name no vendor under this bullet until one exists.
- **Affiliates are not listings.** inclusionAI, the vendor behind the `inclusionai/`
  Ling models, is Ant Group's open-source arm, and Ant Group is an Alibaba affiliate;
  neither Ant nor inclusionAI appears in the two citations above, so their rows say
  "Ant Group, Alibaba affiliate; not itself listed" and never inherit Alibaba's flag.
  Say what the record shows, and say that the record is the two citations, not a
  fresh check of the lists.

When a vendor in the week's catalog is on either list, say so in the catalog table's
limitation column for each of its models, in the same words each week. A listing is a
card fact: it can never earn a rating, and it is not a disqualifier in the table's
sense, since the venue serves the model; it is a fact the editor weighs when rating.

## Maintaining providers/ (a separate report)

`providers/<venue>.md` is a standing reference, not part of the weekly issue. It is the
only document here that is **edited in place** rather than appended — nobody should have
to reconstruct "does this venue need a deposit" from eight months of observations.

After writing the issue, update a provider page if the week produced any of:

- a change to how you get in — signup, card requirement, deposit, rate limits
- a change to what the API accepts, or a route that turned out to work when the docs
  said otherwise
- a catalog quirk that would mislead the next person writing an adapter
- an evidence-tier upgrade: something previously `[R]` or `[?]` that got probed

Rules that hold on those pages: tier every claim inline (`[M]` measured, `[R]` reported,
`[?]` unverified), name the observation file behind each `[M]`, bump `last_verified`, and
**never upgrade a tier without new evidence** — a `[R]` claim repeated confidently for six
months is still `[R]`.

If nothing changed, leave the pages alone and say nothing about them in the issue. The
weekly issue gets at most one line pointing at a provider page that moved.

## Generator review (part 2)

After writing the report, evaluate whether this file still fits the landscape. Check
each trigger:

**Revision triggers** — if any fires, propose a specific edit to this file:

- **T1.** A new stealth listing appeared, or a previously cloaked one was claimed or
  revealed → the attribution history needs updating, and check whether the lab's
  pattern changes the priors. (The fetcher detects the first half of this; the reveal
  is something you notice.)
- **T2.** OpenRouter changed the free-tier rate-limit structure → the data table and the
  token-efficiency observation both need rewriting.
- **T3.** A new venue for cloaked models appeared, or an existing one stopped being used
  → scope may need to widen beyond OpenRouter.
- **T4.** Two or more catalog entries were delisted → churn may deserve its own standing
  section rather than a closing line.
- **T5.** A benchmark that actually measures *review* quality appeared — real defects
  found, false positives counted, calibration scored → that is a reason to promote
  benchmarks back out of the aside, and possibly to stop hand-running models.
- **T6.** A tried model's behavior contradicted the snapshot twice running → the catalog
  is being trusted further than it earns, and part 1 needs a reliability caveat.
- **T7.** The stealth slot has been empty for three consecutive weeks → consider folding
  the stealth section into a single line rather than a section.
- **T8.** The `oxbox` workflow itself changed → the scope section is stale.
- **T9.** Platform ownership or free-tier economics changed — a repricing, a policy
  change, or a deprecation date appearing on a previously open-ended free endpoint.
  OpenRouter's acquisition by Stripe is pending as of issue 0.1; the free tier is a
  subsidy line, and subsidy lines are the first thing a new owner reprices.
- **T10.** Part 2 has been empty for three consecutive weeks → the report has degenerated
  into a catalog diff, which `oxsurvey` already prints for free. Either the cadence is
  wrong or the survey has stopped earning its keep. Say so.

`oxsurvey` detects T1, T4, T7, and T9 mechanically from the snapshot diff and prints
them. The rest are judgment calls made while writing the issue. **A trigger the fetcher
printed is a fact; a trigger you noticed is an argument, and should be written up as one.**

**How to propose a revision:**

- State which trigger fired and what evidence fired it.
- Show the exact edit as a diff against this file — old text and new text.
- Bump `version` (minor for a rule change, major for a scope change) and set
  `last_generator_review` to today.
- **Do not apply the edit unilaterally.** Present it and wait. The user decides whether
  the landscape actually moved or whether it was noise.

If no trigger fired, say so in one line: `Generator review: no triggers fired; rules
unchanged since <date>.` Resist the urge to find something. A stable generator is a
working generator.

## Honesty rules for this report

- **Label the tier of every claim.** Measured (the snapshot), Observed (oxbox runs),
  Reported (anything a vendor said). A card's structured fields are Measured; a card's
  prose description is marketing and is Reported.
- **A manifest param is a claim too.** `params.effort` and `params.max_tokens` are
  Measured only when they come from the snapshot's own fields, and an entry's
  `provider` pin only when its `only` list is the routes the rated runs went to. A
  level inferred from a model's family, its name, or another venue's catalog is
  Reported in a Measured coat: omit the field instead. The manifest is executable, so a guess there is not
  a sentence a reader can discount — it is a parameter on a request that gets sent.
- Vendor benchmarks are vendor benchmarks, they appear as a labeled aside, and they
  never move a recommendation.
- A single-digit-sample community test is not a benchmark. Say "preliminary" and give
  the sample size. The same applies to the user's own runs — report the counts and the
  file, and never generalize past them.
- Community fingerprinting of a stealth model's origin has a poor track record. Report
  the guess, report that it is a guess, and report the base rate of past guesses being
  wrong.
- If a source contradicts another, show both and say which is better evidenced. Do not
  silently pick one.
- If the data for a field is missing, it reads "no data". Do not fill gaps with
  plausible-sounding estimates, and do not interpolate from an adjacent benchmark.
