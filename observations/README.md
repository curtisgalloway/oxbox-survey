<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

# observations/

The Observed tier's durable home. Everything here was seen by running something,
not read off a card and not quoted from a vendor.

Part 2 of each issue ("tried this week") is written from this directory plus the
oxbox run logs. Anything that stays in a chat transcript is lost by the next
issue, so if an agent notices something worth a sentence in the survey, it lands
here as a file or it did not happen.

## One observation per file

`observations/YYYY-MM-DD-short-slug.md`, dated the day it was observed. The week
is derivable from the date; there are no week directories. One file per
observation, not per session — two unrelated findings on the same day are two
files.

Per-file rather than a shared weekly log because agents run concurrently, and
two of them appending to one file is a merge conflict for no benefit.

## Format

```markdown
---
date: 2026-08-23
venue: zenmux            # openrouter | zenmux | opencode | requesty | aihubmix
model: z-ai/glm-5.3-free # or "-" when the observation is about the venue itself
kind: access             # see the table below
source: probe            # oxbox-run | probe | manual
agent: claude-opus-5     # who observed it; a human name is fine too
corpus: oxbox-review-queue  # optional: the fixture this run used, see corpora/
role: candidate          # optional: candidate (default) | baseline, see below
---

# Title

**What happened** — one or two sentences.

## Evidence
<The actual command and the actual output. Redacted of keys.>

## So what
<Why the survey should care. One paragraph at most.>

## Cost
<Output of costcheck.py: the model's tokens and the harness's, with the window.>
```

`kind` maps to the part 2 axes already defined in the generator, so the skill can
group observations without interpreting prose:

| kind | covers |
|---|---|
| `findings` | verified-real vs false-positive counts, calibration on a review run |
| `hygiene` | format contract — hunk headers, context lines, parseable structure |
| `access` | whether the endpoint can be called at all: auth, credit gates, refusals |
| `availability` | transient failures under load — 429s, pool contention, outages |
| `efficiency` | tokens spent to reach the same answer, on both sides of the run — the model's and the reviewing agent's |
| `card-contradiction` | served behavior disagreeing with the snapshot |

## Rules

- **`source: probe` can never justify a `USE`.** A curl against an endpoint proves
  the endpoint answers; it says nothing about review quality. Only `source:
  oxbox-run` carries a recommendation. This is the v2 rule — a recommendation
  requires a run — enforced at the evidence layer.
- **Never edit a published observation.** If it turns out wrong, write a new file
  that links the old one and says what changed. The archive's value is that it
  records what was believed at the time.
- **Paste the real evidence,** exact request and response, so a reader can judge
  it rather than trust the summary. Redact keys; never paste a prompt containing
  anything but public code.
- **A findings run reports both halves of its cost.** Any observation with
  `kind: findings` and `source: oxbox-run` carries a `## Cost` section, from
  2026-08-30 on. The model's own tokens are the cheap half and the only half the
  survey used to count; the expensive half is reading every finding against the
  source and deciding which are real, and that is paid in the reviewing agent's
  tokens. A free model that emits fifteen findings with two false positives can
  cost more to use than a paid one that emits five clean, and until this section
  existed nothing in the repo could say so.

  ```bash
  python3 costcheck.py --run ../oxbox/logs/<run> [--run <another>] \
      --session <uuid> --from 2026-08-30T01:05Z --to 2026-08-30T01:45Z
  ```

  **State the window and treat the number as an upper bound.** It includes
  anything else the session did in that window. A harness figure without its
  window is not a measurement, and `costcheck.py` prints the window for exactly
  that reason. Earlier observations are grandfathered — do not backfill them by
  editing; the archive records what was believed at the time.
- **A run against a fixture cites it.** If the payload came from
  `corpora/corpus-manifest.json`, put the task id in the `corpus:` field. That is
  what makes a matched comparison findable later instead of noticed by luck, and
  `surveytest.py` checks the id exists. A run assembled by hand simply omits the
  field.
- **A baseline is a reference, never a candidate.** `role: baseline` marks a run
  of a paid frontier model -- Sonnet, Gemini Flash -- against a corpus fixture,
  there so a free model's count on the same fixture means something. A baseline
  observation carries no status marker and appears in an edition only as the
  reference figure beside a candidate's ("Sonnet 5 on the same fixture: x of
  y"). A free model is never a baseline. A paid model may be both a manifest
  entry and a baseline (`z-ai/glm-5.3-flash` is), and then its baseline
  observations are not what move its entry -- a candidate run is. Omitting
  `role` means `candidate`. `surveytest.py` enforces the marker and free-model
  rules.
  Decided 2026-09-02; see `docs/decisions.md`.
- **Counts and filenames, never adjectives.** "4 of 10 findings verified on
  `oxbox/ox`" is an observation; "good at review" is not.
