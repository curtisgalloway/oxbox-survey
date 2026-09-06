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
run: 2026-09-03T02-41-40Z   # the ox log directory (comma-separated if several)
wall_s: 12                  # longest run's wall clock, from the log timestamps
findings: 8                 # review mode: findings emitted ...
real: 1                     # ... and how many verified real
hits: 10                    # fixture with a seeded set: hits ...
hits_of: 10                 # ... of the fixture's total (see the task's quality field)
applies: true               # diff mode: did git apply --check pass at the pin
self_hits: 0                # diff mode: the patched scanner refusing its own source
usd_model: 0.0273           # the model's half, computed from the archived catalog
usd_total: 0.0273           # both halves; equals usd_model on a mechanically scored fixture
timed_out: false            # the request never returned
disqualifier: not_found     # access/availability: the venue refused the run
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

- **A probe is not a run, and only a run gets a row.** A curl against an endpoint
  proves the endpoint answers; it says nothing about review quality. Only
  `source: oxbox-run` observations of kind `findings` or `hygiene` become rows in
  the catalog table, and only rows can carry the measured fields above. A probe
  may record a `disqualifier`, which annotates the catalog listing. This is the
  v2 rule — a recommendation requires a run — enforced at the evidence layer.
- **The measured fields are the record the digits are bucketed from.** Every
  run-backed `findings` or `hygiene` observation from 2026-09-06 on carries
  `run` and `wall_s`, plus `findings`/`real` for a review run or `hits`/`hits_of`
  for a fixture with a seeded set (`applies` and `self_hits` in diff mode).
  `ratings.py` turns them into the 0-5 digits; **never write a `quality`, `cost`
  or `speed` key yourself.** `wall_s` comes from the log directory's timestamps
  (its name is the start, its newest file the end) and reproduces the durations
  the bodies state to within a second. Observations before 2026-09-06 had these
  fields transcribed into their frontmatter from figures their bodies already
  stated or their logs already held; nothing was measured after the fact.
- **`usd_total` is both halves, and on a mechanically scored fixture the second
  half is the scorer.** A run on `oxbox-secret-scanner-fix` or
  `oxbox-ask-grounding` is verified by `corpora/scorers/` or the answer key, not
  by a reviewing agent, so its `usd_total` equals its `usd_model` and the cost
  digit can be computed. A human-verified run (`oxbox-clean-control`, any real
  batch) carries `usd_total` only when the verification half was measured for
  that run alone; a shared window is an upper bound, not a figure, and the digit
  stays a dash.
- **A disqualifier is open until a later run clears it.** `disqualifier:` on a
  run-backed access or availability observation names why the venue refused
  (`not_found`, `upstream_error`, `unauthorized`, `rate_limited`, ...). It stands
  until a run-backed row for the same model is dated on or after it; a refusal
  fixed the same afternoon is not standing. An open disqualifier holds a model
  out of the manifest whatever its Editor's Rating.
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
  `role` means `candidate`. A baseline run is a row in the catalog table with
  digits like any other, marked baseline; a model whose only runs are baselines
  carries no Editor's Rating and cannot enter the manifest. `surveytest.py`
  enforces the rating and free-model rules.
  Decided 2026-09-02, amended 2026-09-06; see `docs/decisions.md`.
- **The Editor's Rating is not written here.** Good / Acceptable / Marginal / Poor
  lives in `editor-ratings.json` at the repo root, written by the editor and only
  read by the tools. An observation records what happened; the verdict is a
  separate act by a different author.
- **Counts and filenames, never adjectives.** "4 of 10 findings verified on
  `oxbox/ox`" is an observation; "good at review" is not.
