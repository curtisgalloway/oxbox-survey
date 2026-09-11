<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

# Answer key — the short change review (`oxbox-short-change-review`)

Task: `corpora/prompts/oxbox-short-change-review.txt`, mode `review`,
`jailtest.py` at oxbox `6072d56830dd3f80d567bf8c71593bcab95fbc74` attached in
full, with the diff of that same commit (16 lines added) in the task text as
the change under review.

## Why this fixture

Every other fixture is a whole file. The literature on LLM review says quality
peaks on changes of 10 to 50 lines and recommends splitting anything larger
(arXiv:2505.17928; see `docs/prior-art-2026-09-10.md`). This is the survey's
arm in that regime: a real commit, small, with one defect the commit failed to
handle and a later commit fixed. Written 2026-09-10 before any run.

## The seeded defect (hits_of: 1)

The commit adds a skip for the `/etc/shadow` read probe at uid 0, on the stated
rule that a probe that cannot test should skip. Two lines below the new skip,
unchanged, the metadata oracle still does `os.stat(EXISTING[0])`
(`jailtest.py:134`, `stat_outside` at `:93-94`). When nothing home-relative
exists, which is what a CI container looks like, `EXISTING[0]` is
`/etc/shadow` (the launcher appends it last, `oxbox:93-107`, and filters by
existence at `:343`). `stat()` on it needs only search permission on `/etc`,
which every uid has, and `/etc` is inside both jails, so the oracle succeeds
and reports FAIL on a jail that holds. The same commit's own comment says
`/etc/shadow` is protected by permissions, not by absence; the oracle is the
one probe the change did not apply that reasoning to.

**A hit is any finding that says the stat oracle can still target
`/etc/shadow` (or a DAC-dependent path) and report a false FAIL**, whether it
frames the condition as uid 0, as an environment with no home-relative paths,
or as the oracle needing the same skip. The scenario has to be one the tree
can produce; "the launcher emits system paths first" is not (OPUS1 ruling,
2026-09-10), "a container with an empty home" is. Reference fix: oxbox
`a113e62`, which picks the first path outside `DAC_DEPENDENT` and skips with
a reason when there is none. Found on the 6302b12 file by
`google/gemini-3.7-flash`, 2026-09-02.

## Real, and outside the change

The file at this pin carries two other defects the record knows. Both are
real; both are outside the 16 lines. A finding that names one counts in
`real` (and in `findings`) and not in `hits`, whether or not the model
labeled it OUT OF SCOPE; a label is asked for so the reader can see whether
the model understood the task, and that goes in prose.

- `tcp_connect` and `udp_send` (`:77-81`, `:87-91`) close the socket as a
  trailing statement, skipped when the call raises, which inside the jail is
  the expected path. Fixed in `6302b12`. Found by MiniMax M3, 2026-08-29.
- `probe()` scores any exception as containment (`:52-54`), so the three
  network probes pass on an offline host and a jail that permits TCP still
  reports PASS on a timeout. Fixed in `a113e62`. The record's L1.

## Pre-registered inventions

The record's standing false positives on this file all apply here and are
counted invented: `read_probe` misclassifying a directory when `stat` is
denied and `open` allowed (no backend expresses that policy); an inherited
empty-string credential variable (the launcher builds the environment from
scratch); empty `HOME` or empty `OXBOX_PLATFORM` (the launcher sets both);
`OXBOX_EXISTING_PATHS` missing (always set; an empty list prints `[SKIP]`);
`write_probe` and `REPO_ROOT` unused (accepted as not-defects 2026-08-29).
Two new shapes this change invites, also invented: that `geteuid` is missing
on some platform and the fallback misfires (the fallback returns -1, which is
never 0, so the skip simply does not apply, and the launcher refuses Windows
outright); and that `DAC_DEPENDENT` should hold more paths (`EXISTING` is
built only from `sensitive_paths`, which names no other system path).

## Scoring

Read every finding against `git show 6072d56:jailtest.py` and `oxbox` at the
same pin. Record `findings`, `real`, `benign`, `hits` (0 or 1) and `hits_of: 1`.
"The change is correct as written" is a miss here, not the ideal answer: the
fixture expects one. A model that reports only the seeded defect has the best
possible answer.

## What this cannot tell you

One change, one file, one seeded defect the record already knew before the
fixture was written, which means a model that has seen this repository's
history has an unfair advantage; the commit fixing it is public. Read a hit
as "found it on this diff", not as "would find it in yours".
