<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

# oxbox-survey

The machinery that produces **The Oxbox Survey** — a recurring report on the free and
stealth models offered by OpenRouter and similar gateways, and which of them can actually
review code. The report itself is published at [oxbox.ai](https://oxbox.ai); what lives here
is everything used to make it: the catalog fetcher, the measured snapshots behind every
claim, the run observations, the pinned corpus the models are tested against, and the cost
accounting.

Companion to [oxbox](https://github.com/curtisgalloway/oxbox), the harness for running an
untrusted model against your code without giving it your machine. oxbox is the containment;
this is the question of what to put in it.

## What kind of document this is

**Read this before trusting a number here.** oxbox holds itself to a specific standard —
every claim in that README has a test count behind it, and the jail is tested rather than
asserted. This repo cannot meet that standard and does not try to.

The survey ranks models. Ranking involves judgment, and much of the evidence is vendor
self-reported benchmarks that nobody has audited. Three tiers of evidence appear here,
always labeled:

| Tier | Source | How far to trust it |
|---|---|---|
| Measured | `snapshots/` — captured from the OpenRouter API | Reproducible. Re-run `oxsurvey` and check. |
| Observed | oxbox run logs — findings verified by experiment | Real but small-sample, and specific to one reviewer's repos. |
| Reported | Vendor benchmark tables, community tests | Take at the vendor's word. Harnesses differ; nothing is audited. |

A ranking is an opinion built on those. It is not a test result.

## Layout

```
oxsurvey                          fetcher: snapshot the free tier, diff against last week
surveytest.py                     offline tests: adapters, triggers, and the repo's own rules
snapshots/<venue>/YYYY-MM-DD.json committed catalog captures — the measured tier
observations/YYYY-MM-DD-*.md      the observed tier: what agents saw when they ran something
providers/<venue>.md              standing notes per venue: gates, API shape, quirks
.claude/skills/oxbox-survey/      the generator: how an issue gets written, and how the
                                  generator reviews its own rules
.github/workflows/snapshot.yml    manual dispatch only: capture a snapshot when away from the
                                  machine that publishes
AGENTS.md                         house rules for whoever (or whatever) works in here
```

## Producing an issue

```
./oxsurvey                        # snapshot every venue, print each diff and any
                                  # generator-review triggers they fired
./oxsurvey --venue zenmux         # just one; repeatable
./oxsurvey --list-venues          # what is configured, and how far to trust it
./oxsurvey --probe                # also call each free model once and record
                                  # whether it actually answers
```

A catalog says what a model *costs*. It cannot say whether the model *answers* —
and this survey has now measured that gap twice: a zero-priced model that returns
402 until the account is funded, and listed models whose upstream returns 503
while their siblings answer in the same minute. `--probe` closes it. Results are
Observed, so they land in `snapshots/<venue>/<date>-access.json` and never touch
the catalog snapshot.

Four venues, in two classes, and the difference decides what a snapshot can claim:

| Class | Venues | `free` is |
|---|---|---|
| A — pricing in the catalog | openrouter, zenmux, requesty | **Measured.** Snapshot holds the free models. |
| B — roster only, no pricing | opencode | **Unknown**, written as `null`. Snapshot holds the whole roster so churn stays diffable. |

A class B `null` is not a zero and must never be rendered as one. The `-free` id
suffix is not a substitute either — `big-pickle` and `grok-code` are free without
it. Only an access probe or a first-party price settles class B.

Requesty is the one venue publishing `data_used_for_training` and
`data_retention_days` as fields rather than as prose on a terms page, so data
terms are Measured there and Reported everywhere else.

Then run the `oxbox-survey` skill, which reads the newest snapshot plus your oxbox logs
and writes the edition into the `oxbox.ai` repo, which publishes it. The skill
also evaluates whether its own rules still fit;
it proposes revisions as a diff and never applies them unattended.

`./oxsurvey --dry-run` fetches without writing. `./oxsurvey --diff A.json B.json` compares
two existing snapshots offline.

Currently stdlib-only and Python 3.9+, so it runs on a stock macOS or Linux
python3 with no setup. That is a property of the code as it stands, not a rule:
oxbox forbids dependencies because it is a containment tool, and that reasoning
does not transfer to a fetcher reading a public catalog.

## Why the snapshots are committed

They are the only part of this repo that gets more valuable with age. Several questions the
survey exists to answer are only answerable against a series: whether free tiers narrow after
OpenRouter's acquisition closes, how long a stealth listing typically survives, whether the
gap between advertised and served context is widening. A prose archive cannot answer those.
A dated JSON series can, and `git log` makes the week-over-week diff free.

The first snapshot should be produced by running `oxsurvey`, not hand-written, or it will not
be comparable to the ones after it.

## License

Apache-2.0, all of it. The editions — the survey prose itself — are not in this
repository: they live in `oxbox.ai` and are all rights reserved. Everything here
is machinery and evidence, and the two archived vendor catalogs have had the
venues' own `description` text removed, because that is theirs and not ours to
relicense.
