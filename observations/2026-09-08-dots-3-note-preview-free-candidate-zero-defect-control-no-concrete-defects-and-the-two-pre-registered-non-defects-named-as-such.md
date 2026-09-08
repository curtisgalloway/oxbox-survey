<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-08
venue: openrouter
model: dots-studio/dots-3-note-preview:free
kind: findings
source: oxbox-run
agent: claude-fable-5-1
corpus: oxbox-clean-control
role: candidate
run: 2026-09-08T01-23-01Z
wall_s: 139
findings: 0
real: 0
usd_model: 0
usd_total: 0
---

# Dots 3 Note Preview free as a candidate on the zero-defect control: "no concrete defects", and the two pre-registered non-defects named as such

**What happened** — `oxbox-clean-control`, the zero-defect control
(`jailtest.py` at `6302b12`, 6,096 B, review mode, effort high, 100,000
tokens, temperature 0.2), put to `dots-studio/dots-3-note-preview:free`. Run
as a candidate in the try-next batch the editor approved in round 8 of the
rating review (2026-09-07). Zero findings. The answer walks the five
categories the prompt names and says why each holds, then lists two "minor
observations (not defects)": the dead `REPO_ROOT` binding and the unused
`write_probe`, the exact two items the answer key pre-registers as false
positives if reported as defects, here reported as not defects with the
comments that explain them cited. It also declined the root stat oracle
shape by getting its mechanism half wrong in the safe direction ("the jail
denies stat() itself"), without turning it into a finding. 12,792 completion
tokens, 12,677 reasoning, 139 seconds, route AtlasCloud, $0 billed.

## Evidence

Log `logs/2026-09-08T01-23-01Z`, `finish_reason` stop, prompt 1,723,
completion 12,792, `reasoning_tokens` 12,677, `route` AtlasCloud,
`venue_cost` 0. Nothing to check. The answer's conclusion: "The file is
correct as written. No changes are needed."

## So what

The first free model to produce the fixture's ideal answer, and it did so
while naming the two decoys and declining them. Three of the batch's seven
models (Nemotron, MiMo, this one) invented nothing here; two timed out; two
invented. Against the two known defects at this pin it found neither, which
the key treats as expected for a clean read.

## Cost

Free; no findings, so no checking half and `usd_total` equals `usd_model`,
$0. Nothing real to divide by, so the cost score is the floor by rule; speed
4.
