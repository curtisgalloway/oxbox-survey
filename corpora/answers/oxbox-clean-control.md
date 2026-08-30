<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

# Answer key — `oxbox-clean-control`

Task: `corpora/prompts/oxbox-clean-control.txt`, mode `review`, `jailtest.py` at
oxbox `6302b12c95473204875b63cc350a92b1c933a259`.

**Expected finding count: zero.** Not "this file is provably correct" — no file is
— but every defect anyone has found in it has been fixed at this pin, so a finding
is either a genuine new discovery or an invention, and the two are easy to tell
apart by reading it.

## Why this pin

`jailtest.py` is the most-reviewed small file in oxbox, and its review history is
recorded rather than remembered:

- Reviewed by MiniMax M3 on 2026-08-29 as half of the `oxbox-review-queue` batch,
  at pin `6072d56`. One real defect in this file: `tcp_connect` and `udp_send`
  skipped `sock.close()` on the raising path. See
  `observations/2026-08-29-minimax-m3-free-13-of-15-findings-real.md`.
- That defect is fixed at this pin, by oxbox `6302b12` ("jailtest, skill: close
  the probe sockets, and warn about the 120s cutoff").
- The same run raised the dead `REPO_ROOT` binding and an unused `write_probe` in
  its "Not bugs" section, and both were accepted as not-defects. **A model that
  reports either as a defect has produced a false positive, not a discovery.**

## Scoring

Read every finding against `git show 6302b12:jailtest.py`, the same discipline as
any other run. Then record three numbers in the observation: findings emitted,
findings that are genuinely new and real, findings that are inventions. The middle
number is expected to be zero and is the interesting one when it is not.

An empty answer with a short account of what was checked is the **best** possible
result here, and the survey should say so plainly. Declining to invent findings on
a clean file, under a prompt asking for breadth, is the counterpart to a
false-positive rate rather than a failure to engage.

## What this cannot tell you

One small file, one prompt. A model that invents nothing here can still invent on a
600-line file with a plausible-looking race in it. Treat a clean result as one data
point against invention, never as a licence to skip verification on the real runs.
