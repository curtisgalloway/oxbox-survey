<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-11
venue: ollama
model: gpt-oss:20b
kind: findings
source: oxbox-run
agent: claude-fable-5-1
corpus: oxbox-short-change-review
role: candidate
run: 2026-09-11T02-52-19Z
wall_s: 29
findings: 1
real: 1
benign: 0
hits: 1
hits_of: 1
usd_model: 0
usd_total: 0
---

# gpt-oss 20B, local, on the short change review: one finding, the seeded defect, in 29 seconds

**What happened** — `oxbox-short-change-review` (commit `6072d56`'s 16-line
change to `jailtest.py` as a diff in the task text, the 5,915-byte
post-change file attached, review mode, effort medium, 16,000 tokens,
temperature 1.0) put to `gpt-oss:20b` through its `gpt-oss:20b-64k` tag
served by ollama 0.34.0 on argenta, through the local setup described in
`2026-09-10-qwen3.8-27b-local-candidate-zero-defect-control-nothing-in-900-seconds-on-argenta.md`.
One finding in 29 seconds, 2,292 completion tokens, 8,589 characters of
reasoning, and it is the seeded defect: "the loop skips the file-reading
probe for `/etc/shadow` but still performs the metadata probe
(`stat_outside`) on that same path", with a seven-step scenario as root
ending in a false FAIL, and the fix the key names ("skip the metadata probe
for DAC-dependent paths when running as root, just as it does for the read
probe"). Its reason for the stat succeeding, that root ignores permission
bits, is not the key's (stat needs only search permission on `/etc`, at any
uid), but the key accepts the uid-0 framing because the state is one the
tree produces and the consequence is the one the fix addressed. **hits 1
of 1; emitted 1, real 1, invented 0**, which the key calls the best possible
answer on this fixture. Neither out-of-scope defect raised.

## Evidence

Log `logs/2026-09-11T02-52-19Z`, `context_bytes` 5915, `finish_reason` stop,
prompt 2,234, completion 2,292. Scored against the key and the pin; no
check was sent because the only finding is the seeded one.

## So what

The model that looped for 22 minutes on the 6 KB control at v1, and
invented six then five findings on it at v2, produced the ideal answer on
a 16-line change in half a minute. This is the regime the literature says
review works in, and the first two local models to run it both found the
defect that the whole-file runs of the same models had missed at every
parameter set. One run each, one change, one seeded defect; but the arm
has already separated "can review a change" from "can review a file" in a
way nothing else in the corpus does.

## Cost

Nothing billed, nothing to check.
