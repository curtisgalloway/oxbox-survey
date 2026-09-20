<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-20
venue: openrouter
model: "-"
kind: access
source: oxbox-run
agent: claude-opus-5
run: 2026-09-11T00-35-34Z, 2026-09-11T00-35-43Z, 2026-09-11T00-36-16Z, 2026-09-11T00-38-20Z, 2026-09-11T00-38-22Z, 2026-09-11T00-53-23Z, 2026-09-19T01-44-41Z, 2026-09-19T01-44-43Z, 2026-09-19T01-44-53Z, 2026-09-19T01-47-58Z, 2026-09-19T02-03-00Z, 2026-09-19T02-03-48Z
---

# Twelve genuine-work review attempts in ten days, and not one reached a model

**What happened** — a survey of the `logs/` directories of the editor's other
projects, prompted by the 2026-09-20 ruling that ratings should come from real
work rather than fixtures. Between the 2026-09-10 issue shipping and the pin
being fixed on 2026-09-20, oxbox was pointed at real code twelve times across
two public projects. Every one failed before a model saw the request. This is
recorded on 2026-09-20 because that is when anyone looked; the runs are older
and went unrecorded at the time.

## Evidence

Eight distinct review tasks, twelve attempts, zero answers.

**`curtisgalloway/shoephone`, 2026-09-11** — the day after the issue that set
the guard:

| run | target | context | outcome |
|---|---|---|---|
| 00-35-34Z | `src/ca.rs`, `src/store.rs` | 31,374 B | 404, Filter by Max Price |
| 00-35-43Z | `src/bin/shoephone.rs`, `src/bin/shoephoned.rs` | 36,775 B | 404, same |
| 00-36-16Z | `tests/loop.rs`, `tests/page.rs` | 11,361 B | 404, same |
| 00-38-20Z | four files | 32,204 B | 404, same |
| 00-38-22Z | the same four, under `--failover` | 32,204 B | entry 1 404; **entry 2 timed out at 900 s** |
| 00-53-23Z | five files | 21,969 B | 404, same |

**`curtisgalloway/paniolo`, 2026-09-19** — three targets, each attempted twice:

| target | context | attempts | outcome |
|---|---|---|---|
| `packaging/scripts/postinstall.sh` + its test | 4,923 B | 01-44-41Z, 02-03-00Z | 404, Filter by Max Price |
| console and dashboard excerpts | 25,431 B | 01-44-43Z, 01-47-58Z | 404, same |
| release-workflow excerpts + a container test | 13,524 B | 01-44-53Z, 02-03-48Z | 404, same |

Eleven of the twelve are the `max_price` guard matching no endpoint — the
defect recorded on 2026-09-19 and fixed on 2026-09-20. The twelfth is the one
time failover was tried, and it found the second wall.
[[2026-09-20-deepseek-v4-flash-timed-out-at-900-seconds-on-a-real-32kb-review]]

Only three of the twelve were in the record before today: the 2026-09-19
observation cites `01-44-41Z`, `-43Z` and `-53Z`. The other nine — including
every shoephone run and the timeout — existed only as log directories.

## So what

**The survey's own first recommendation was unusable for its author's real
work for ten days, and the record did not know.** The fixtures kept passing
the whole time. That is the gap between a fixture suite and a channel someone
actually uses, and it is the same shape as the release-train lesson in the
sibling repo: the arm that is never run is the one that fails.

**It is also the reason the 2026-09-20 rating rule has nothing to stand on
yet.** Ratings are now meant to come from adjudicated real batches. The real
batches from this period produced no model output at all, so there is nothing
to adjudicate — not a single verified finding from genuine work in the window.
The rule is right and the corpus for it is empty, which is a thing to say out
loud rather than discover in three weeks.

**The retries say something too.** Both projects show the same targets
attempted twice, minutes apart — the shape of a person re-running a thing that
did not work rather than reading the 404. Nothing routed either time, and
nothing was recorded either time, so the failure was invisible to the survey
until someone went looking at the filesystem.

## What would have caught it

A routability check on each manifest entry at issue time, which the 2026-09-19
observation already asked for and which the 2026-09-20 re-pin now performs
before publishing. And something that notices a `logs/` directory full of
`error.txt` and no `content.md` — the evidence was sitting on disk for nine
days.
