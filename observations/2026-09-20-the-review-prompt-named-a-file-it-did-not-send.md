<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-20
venue: openrouter
model: "-"
kind: hygiene
source: manual
agent: claude-opus-5
---

# The review prompt named a file it did not send, and got invented defects about it

**What happened** — while adjudicating the first genuine-work runs, two of the
five findings turned out to quote regular expressions that do not exist in the
file they cite. The file was never in the request. The prompt named it,
described what it does, and asked the model to assess it.

## Evidence

From `request.json` of `2026-09-19T02-03-48Z-2`, the task text:

> `test_workflow_container_shell.py` is a guard added after a bash-only
> `set -o pipefail` in that Linux step broke a release build; it parses the
> workflows and fails on bash-only syntax in container-job steps. Pay
> particular attention to: ... **whether the guard has gaps that would let the
> same class of bug through.**

The request's `### File:` blocks contain two excerpts —
`release_linux_bottle_excerpt.yml` and `release_macos_bottle_excerpt.yml`.
Probing the full 15,774-character prompt:

```
test_workflow_container_shell    PRESENT     (named in the prose)
SET_O                            absent
DASH_SET_O                       absent
```

The guard's source is not there. The model then produced two findings against
it, quoting `\bset\s+-[a-z]*o\s+pipefail\b` and `\bset\s+-[a-z]*\bo\b` at
"line ~45" and "line ~44". Neither pattern nor either line number exists; the
real expression is
`\bset\s+(?:-[a-z]+\s+)*-[a-z]*o\s+([A-Za-z_-]+)`.

## So what

**Asking about a file you do not send is an invitation to invent.** The prompt
did three things that compound: it named the file, it explained its purpose
convincingly enough to reason about, and it directed attention at it with
"whether the guard has gaps". A model that answers such a prompt at all must
make the content up; declining would have been the only honest response, and
the two findings it produced are otherwise plausible-looking, specific and
cited.

That reframes the run's invention count. Five findings, none real — but two of
the five were solicited by the harness rather than volunteered by the model.
The remaining three stand as the model's own.
[[2026-09-20-deepseek-v4-flash-the-first-genuine-work-rows-one-clean-verdict-and-five-findings-none-real]]

**It also bears on what genuine work can measure.** The 2026-09-20 rule moves
ratings onto real batches, and real batches are assembled by a skill that
chooses excerpts. If the assembler can name a file it does not include, the
invention counts it produces are partly a property of the assembler. A rating
built on that measures two things at once.

**The narrower lesson for the excerpting itself:** finding 5 complained that
the macOS bottle step contains only `set -euo pipefail` and no commands, which
is true of the excerpt and false of the workflow. The model labeled it
UNCERTAIN and named truncation as the likely cause, which is the correct
reading — but an excerpt that ends mid-step will keep producing that finding
from every model that sees it.

## What to check next

Whether the review skill's prompt builder can reference a path it did not
attach — and if so, whether it should either attach it or stop naming it.
Worth a look in the assembler before the next genuine-work batch goes out,
since every batch from here is meant to feed a rating.
