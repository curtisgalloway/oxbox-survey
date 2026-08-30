<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-08-30
venue: opencode
model: nemotron-3-ultra-free
kind: availability
source: manual
agent: claude-opus-5 (oxbox-survey), reporting a finding from the oxbox session
---

# "Never reached" had a mechanical cause as well as a ranking one, and the two look identical from the log

**What happened** — `usagereport.py` found that `nemotron-3-ultra-free` and
`mimo-v2.5-free` were never reached in either shipped manifest, and I read that
as the ranking feedback loop: the entry above them always worked, so ox never
walked down to them. That was incomplete. The oxbox session reports a batch that
tried to pin nemotron *explicitly* and never got a request out — `oxreview`
forwarded `--venue` alongside `--manifest`, which `ox` rejects — and that the
rejection took 1262 seconds while holding the machine-wide queue lock. Fixed in
oxbox `9da7a00`; the same rejection now takes 0.06s.

## What I verified, and what I did not

Verified here:

- `9da7a00` exists and is titled "oxreview: three ways one queue lock could be
  held by two batches", describing three paths by which one lock could be held
  by two batches, all reproduced.
- The free-pool abort in the same window is real and its shape is as described:
  `logs/2026-08-30T15-39-09Z/` holds `content.md` at **0 bytes** beside
  `reasoning.txt` at **22,172 bytes**. The whole answer went into reasoning and
  none into content.

Not verified here: the 1262-second figure and the `--venue` + `--manifest`
forwarding. No `status.json` in the window names nemotron at all, which is
consistent with a batch that never sent a request — a run that dies before the
call leaves nothing for `usagereport.py` to count. Taken on the oxbox session's
report.

## So what

**Absence of evidence had two causes and the report showed one.** A model that
was never reached because the rank above it kept working is a *ranking* fact and
argues for promoting it. A model that was never reached because the harness
wedged before sending is a *tooling* fact and argues for nothing at all. Both
render identically in `usagereport.py`: no runs, no attempts, silence.

So the survey must not read "never reached" as a signal about the model. For
`nemotron-3-ultra-free` and `mimo-v2.5-free` the position is unchanged and
should be stated plainly in the issue: **genuinely no data, not bad data.** They
have never been exercised, they have never failed, and the reason they were
never exercised is now partly a bug that is fixed.

It also argues for the tripwire (`oxsurvey --probe --tripwire`): a screen that
calls every model directly, rather than only whatever the manifest walks down
to, is the thing that would have given these two a verdict months before the
ranking loop ever reached them.

## A method correction that came with it

I read `ox` from the oxbox working tree while checking that the corpus prompts
do not trip its own secret scanner. That tree was mid-flight at the time — the
oxbox session had temporarily checked out pre-`6ba47d8` copies to prove new
guardtest cases actually fail against broken code — so I was comparing against
bytes that were deliberately broken and about to be restored.

Re-run against committed refs only: 8 patterns at `6072d56`, 9 at committed
HEAD, and all five prompts clean against both. The conclusion was right; the
method was not. **Read a target's source at a committed ref, never from a
working tree you do not control** — a checkout is somebody's workbench, and it
is allowed to be broken at any instant.
