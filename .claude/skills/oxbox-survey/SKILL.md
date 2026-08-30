---
name: oxbox-survey
description: Generate an issue of the Oxbox Survey — a catalog of the free and stealth models on OpenRouter built from measured card facts and their limitations, plus observations from the ones actually run through oxbox that week, plus a self-review of the generator's own rules. Use this whenever the user asks for the weekly free-model report, the stealth model report, "what's free on OpenRouter this week", an update on cloaked models, or when a scheduled routine fires this skill by name. Also use it after ./oxsurvey has written a new snapshot. Also use it when the user asks whether the report rules need revising, or mentions oxbox alongside model selection.
version: 2.0.0
last_generator_review: 2026-08-23
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

**The rule that keeps this honest: a recommendation requires a run.** See the status
markers below — `USE` is reserved for models the user has actually put through oxbox.
Card facts can earn a model a `TRY`, never a `USE`.

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

**A probe is not a run.** An `observations/` file with `source: probe` proves an endpoint
answers; it says nothing about review quality and can never justify a `USE`. Only
`source: oxbox-run` carries a recommendation.

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
- **oxbox run logs** — `logs/*/metadata.json` and the review outputs, on the machine that
  holds them.

If neither has anything new, part 2 is one line.

## Report format

Markdown. Keep it scannable — this is read weekly, not studied.

```
# OpenRouter free models — week of <date>

## Verdict
<2–3 sentences: what to point oxbox at this week, what changed, and what you ran.>

## Catalog
<Generated table, every free model, with the limitations column. Then a short
paragraph only for entries whose limitation needs explaining.>

## Stealth tier
<Per cloaked model: slug, listed date, endpoint context, stated free window and
days left, terms, suspected or confirmed attribution with the evidence and the
base rate of such guesses being wrong.>

## Tried this week
<Per model actually run: the observations above, with counts and filenames.
One line if nothing was run.>

## Caveats
<Bulleted. Anything that would make a number in this report misleading.>

## Churn since last report
<Added, delisted, repriced, revealed. One line each, from the fetcher's diff.>

## Generator review
<See below.>
```

**Status markers, and what earns each:**

| Marker | Requires |
|---|---|
| `USE` | Run through oxbox, results in part 2, and they were good. |
| `TRY` | A specific card fact makes it worth a run. Name the fact. |
| `HOLD` | Was tried, or has a card fact, that says wait — expiring, degraded, churning. |
| `AVOID` | Tried and bad, or a card fact that disqualifies it for this job. |

Never a `USE` on a model nobody ran. **Markers must not rely on colour** — use the text
labels, never a red/green dot as the only carrier of meaning, and never "the green ones"
in prose.

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
