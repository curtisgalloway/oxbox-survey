<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

# oxbox-survey — notes for agents

The machinery that produces **The Oxbox Survey** — a recurring report on the free
and stealth models offered by OpenRouter and similar gateways. The report itself
is published at [oxbox.ai](https://oxbox.ai) and its text lives in that repo; this
one holds everything used to make it. Companion to
[oxbox](https://github.com/curtisgalloway/oxbox), which is the containment; this
repo is the question of what to put in it.

Read [README.md](README.md) first — in particular the evidence-tier table. Every
claim written here belongs to exactly one of **Measured** (`snapshots/`),
**Observed** (oxbox run logs), or **Reported** (vendor tables), and the tier is
always stated. A ranking is an opinion built on those; it is not a test result.

## Producing an issue

```bash
./oxsurvey                        # writes snapshots/<UTC date>.json, prints the
                                  # diff and any generator-review triggers
```

Then run the `oxbox-survey` skill (`.claude/skills/oxbox-survey/SKILL.md`). It
writes the edition and then reviews its own rules. **Both halves, every run** —
the self-review is the reason it is a skill and not a saved prompt.

**Editions are not in this repository.** They live in the `oxbox.ai` repo under
`editions/`, because they are the publication and are all rights reserved, while
everything here is Apache-2.0. That repo carries this one as a submodule and
builds the site from both halves: its own editions, and this repo's snapshots
and manifests. Write `<date>.md` there; everything below still applies.

**The generator review is not part of the edition.** Part 2 of the skill goes to
`docs/generator-reviews/<date>.md` here, one file per edition; the edition carries
only the report. Decided 2026-09-01: the review is for the maintainer and the
agent to iterate on the generator, not for readers.

The issue is then reviewed in a Google Doc before it is committed — see **The
review loop** below.

`./oxsurvey --dry-run` fetches without writing. `./oxsurvey --diff A.json B.json`
compares two existing snapshots offline, no network.

## The review loop

An issue is drafted in the repo, reviewed by the user in a Google Doc, and only
then committed. The edition in `oxbox.ai` is always the reference copy — the Doc
is a review surface, never the source of truth.

The Docs live in a Drive folder named **Oxbox Survey**, with superseded rounds in
its `Archive/` subfolder. Ask the maintainer for the folder ids; they are not
recorded here, because a public repo is the wrong place to enumerate someone's
private Drive. Rounds are numbered from `r1` per edition.

1. Write `editions/<date>.md` in the `oxbox.ai` repo.
2. Publish that content, minus the SPDX comment, as a new Doc titled
   `The Oxbox Survey — <date> r<N> [DRAFT — your turn]`. Use `create_file` with
   `contentMimeType: text/markdown`, `parentId` the folder above — Drive converts
   headings, tables, bold and links; code-span backticks land as plain text.
3. The user edits the Doc directly and leaves margin comments. **Direct edits are
   decisions, comments are usually instructions.** Treat them differently.
4. Read it back with `read_file_content` and `includeComments: true`, and diff it
   against the repo copy. Comments arrive as threads plus inline
   `<comment_start id=kix.*>` anchors — match thread to anchor by content and by
   timestamp order (threads are newest-first, anchors are in document order).
5. Apply everything to the edition, then publish round N+1 opening with a
   **What changed since r\<N\>** section: one line per comment thread and per direct
   edit, saying what was done with it. That section is Doc-only — it is the reply
   to the user's comments and it never enters the committed markdown.
6. Retitle the round just processed to
   `The Oxbox Survey — <date> r<N> [processed <MM-DD> → r<N+1>]` and move it into
   `Archive/`. One `update_file` call does both.
7. Repeat until the user says it is done. Then commit the edition and retitle the
   last Doc `The Oxbox Survey — <date> r<N> [CLOSED → editions/<date>.md]`,
   leaving it in the folder root. **There is no FINAL Doc** — the committed
   markdown is the report.

So the folder root holds exactly one Doc per issue, either awaiting the user or
closed, and `Archive/` holds every superseded round with its comment history
intact. A Doc with no bracketed status has not been looked at yet.

Two limits of the Drive tooling shape all of this, and neither is a preference:

- **Doc content cannot be updated in place** — `update_file` is metadata-only — so
  each round is a new Doc rather than a new version of one. Title and parent are
  the only things changeable after the fact, which is why status lives in the title.
- **Comments can be read but not written.** Replies go in the next round's *What
  changed* section and in the chat, never in the Doc margin. Do not leave a comment
  thread unanswered in both places.

## Where the survey runs

On a workstation, not in CI. Two halves, and only the first one is portable:

- **The snapshot** is stdlib-only against a public endpoint, so it runs anywhere.
- **The issue** is written by the skill, and axis 1 of its ranking — observed
  review quality from oxbox run logs — outranks every published number in it.
  Those logs are gitignored in oxbox and never leave the machine that produced
  them. A runner that cannot see them writes "no data" on the heaviest axis every
  week.

So the machine holding the oxbox logs runs `./oxsurvey`, runs the skill, commits
`snapshots/` and `observations/` here and the edition in `oxbox.ai`, and pushes.
**It is the single writer of all three.** `.github/workflows/snapshot.yml` is dispatch-only for exactly this
reason: a cron would race that machine on the timestamp and, across the PDT/UTC
boundary, file a second snapshot for the same week under a different date. Do not
put the schedule back without moving the publishing job somewhere else first.

## Tests

```bash
./oxsurvey --probe --probe-limit 6   # also call each free model once, and record
                                     # whether it actually answers
```

The probe is **off by default** because it spends requests against your daily cap
and needs an API key, while the catalog fetch needs neither.

**Its results are Observed, not Measured, and they are written to a separate
file** — `snapshots/<venue>/<date>-access.json`, never merged into the catalog
snapshot. A catalog records what the venue published; an access file records what
happened when we called it. Merging them would blur the one distinction this repo
exists to keep, and a test enforces the separation.

Read an access verdict as a moment, not a property: `rate_limited` and
`upstream_error` say as much about the hour as about the model.

```bash
python3 surveytest.py     # offline: adapters, diff/triggers, and the repo's own rules
python3 oxsurvey --list-venues
python3 costcheck.py --run ../oxbox/logs/<run> --session <uuid> --from <ts> --to <ts>
```

`surveytest.py` does two jobs. It exercises each venue adapter against a recorded
fixture of that venue's real catalog shape, so a parser change that silently
drops the free tier fails there rather than in a committed snapshot. And it
checks the rules this repo states in prose — a class B `free` is null and never
false, every observation carries valid frontmatter, no `source: probe`
observation assigns a `USE`, every active corpus fixture can still be reproduced,
every provider page dates its verification, every file carries an SPDX header. **A rule that lives only in a README is a hope.**

Every assertion is mutation-checked: break the behavior in `oxsurvey` and
confirm the test goes red before trusting it. Two of the original assertions
were wrong rather than the code — T7 correctly fires on a stealth-free catalog,
and "it cannot justify a `USE`" is the rule being stated, not broken.

## Rules

- **Third-party packages are allowed here; they are not allowed in oxbox.** That
  rule belongs upstream and does not transfer. oxbox's whole product is a
  containment claim, and a dependency there is code on the trusted side of the
  boundary, in the process holding the API key — so it stays small and hermetic.
  This repo builds manifests and reports against a public catalog. It is not
  guaranteeing anything, and a rule it cannot justify on its own terms is
  cargo-culted, not inherited.

  Nothing here needs a dependency yet, so everything is still stdlib. When
  something does, add it with **uv** (`uv add`), never `pip install` — the
  system `python3` on macOS is PEP 668-managed and refuses pip outright. Adding
  the first one means deciding the Python floor too; see below.
- **Python 3.9 is the floor, for now.** That is the system `python3` on macOS, so
  every tool here runs with no setup at all — checkout and go, which is also why
  CI has no install step. The floor is a consequence of the stdlib-only habit
  rather than a requirement of its own: the first dependency brings a uv-managed
  interpreter with it, and at that point 3.9 is a choice to re-make, not a
  constraint. Raising it to 3.11 would let `costcheck.py` drop its hand-rolled
  `parse_stamp` for `datetime.fromisoformat`, which only learned to parse a `Z`
  suffix in 3.11.
- **Never hand-write or hand-edit a snapshot.** They are the only measured
  evidence in the repo, and their value is that the series is comparable. A
  touched-up snapshot silently corrupts every week-over-week diff after it.
- **A class B venue's `free: null` is unknown, never false.** Do not render it as a
  zero, do not infer it from a `-free` id suffix, and do not let a catalog table
  present it beside a class A measured zero without saying which is which.
- **Snapshots are named by UTC capture date; issues are named by the local week.**
  They can differ by a day. That is expected — do not "fix" one to match the other.
- **Count both halves of what a run cost.** The model's tokens are in the ox run
  log; the tokens spent assembling the batch and verifying its findings are in the
  agent's own session transcript, and `costcheck.py` sums both into a table for the
  observation. The verification half is the one that decides whether a free model
  is actually cheap, and it was invisible until 2026-08-30. Always print the
  window; the harness figure is an upper bound.
- **Run a model against a pinned fixture where one exists.** `corpora/` names the
  targets and the exact prompts, so two models can be handed a byte-identical
  payload and the difference is theirs. Cite the task id in the observation's
  `corpus:` field. A fixture that already has evidence against it is frozen —
  changing it retroactively breaks every comparison, so add a new task id and
  retire the old one.
- **Noticed something while running a model? Write it to `observations/`.** A finding
  that stays in a chat transcript is gone by the next issue. See
  `observations/README.md` for the schema and the probe-is-not-a-run rule.
- **Never apply a generator revision unattended.** The skill proposes edits to its
  own SKILL.md as a diff and stops. The user decides whether the landscape moved
  or whether it was noise.
- **No color-only status.** Use the text labels `USE` / `TRY` / `HOLD` / `AVOID`.
  Never "the green ones".
- **"No data" is an allowed answer** and the preferred one. Do not interpolate a
  missing axis from an adjacent benchmark.

## Layout

```
oxsurvey                          fetcher: snapshot the free tier, diff against last week
surveytest.py                     offline tests — see Tests above
snapshots/<venue>/YYYY-MM-DD.json committed catalog captures — the measured tier
observations/YYYY-MM-DD-*.md      the observed tier — see observations/README.md
manifests/latest.json             symlink to the newest manifest, for --manifest
manifests/oxbox-manifest-*.json   which model ox should call — regenerated per issue
corpora/corpus-manifest.json      what to send it — pinned targets, see corpora/README.md
costcheck.py                      what a run cost: the model's tokens, and the harness's
providers/<venue>.md              standing notes per venue — see providers/README.md
.claude/skills/oxbox-survey/      the generator, and how it reviews its own rules
.github/workflows/snapshot.yml    manual dispatch only — see below
```

## License

Code is Apache-2.0 (see [LICENSE](LICENSE)); mark new source and instruction
files with the two-line SPDX header, not the full boilerplate. The license for
issue prose is still undecided — see the README.
