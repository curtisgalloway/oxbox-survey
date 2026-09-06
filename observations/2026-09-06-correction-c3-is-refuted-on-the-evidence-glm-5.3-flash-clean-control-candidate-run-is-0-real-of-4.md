<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-06
venue: openrouter
model: z-ai/glm-5.3-flash
kind: findings
source: manual
agent: claude-fable-5-1
corpus: oxbox-clean-control
role: candidate
corrects: 2026-09-06-glm-5.3-flash-candidate-clean-control-four-findings-one-real-and-a-different-one-than-last-time.md
real: 0
---

# Correction: C3 is refuted on the evidence, so the GLM-5.3 Flash clean-control candidate run is 0 real of 4

**What changed** — The observation this corrects recorded finding C3 of run
`2026-09-06T21-30-07Z` as real, on the reasoning that it pointed at the right
probe, the right path and a real consequence with a partial mechanism. Two
fresh checkers then split on it, and the editor directed that the finding be
run rather than read again. The reproduction on macOS and Linux
(`observations/2026-09-06-reproducing-c3-on-macos-and-linux-*.md`) showed
that the failure C3 states does not happen: uid 0 is not what makes the stat
succeed, since it succeeds at any uid through the read-only bind of `/etc`,
and at uid 0 the oracle's FAIL is a true report, because jailed code running
as root reads the host's `/etc/shadow`. The false FAIL that does happen, at
an ordinary uid, is Gemini's G1 from 2026-09-02 and is not what C3 said.

**The editor's ruling, 2026-09-06:** follow the real-world evidence. C3 is
REFUTED. This file carries `real: 0` for the corrected run; the original
observation stands as written, and `ratings.py` overlays the corrected field
onto its row.

## What follows

- The GLM-5.3 Flash candidate clean-control row reads 4 emitted, 0 real, 4
  inventions. Its baseline run four days earlier stays at 1 real (L1, the
  offline host), so across two runs on this fixture the model has one real
  finding in eight, and three inventions repeated.
- In the matched checker pair, Opus 5's verdicts now agree with the corrected
  record four for four, and Fable 5.1's fresh-subagent verdict on C3, which
  credited the finding while noting its mechanism was wrong, was the generous
  reading the contract forbids. So was the original recorded verdict, which
  was Fable's in the main session. The pair observation's statement that
  Fable "matched the recorded verdicts" was true of the record at the time
  and is superseded by this correction.
- The underlying code inconsistency, the oracle at `jailtest.py:134` not
  exempted under the uid-0 rule while the read probe is, remains real and
  remains recorded as G1. The ruling is about whether C3 as written earned
  credit for it, and the answer is no: a right probe with a wrong cause and a
  false consequence is not the defect it describes.
- Reproduction is now the default baseline for a verdict, per the same
  ruling; see `observations/README.md`.
