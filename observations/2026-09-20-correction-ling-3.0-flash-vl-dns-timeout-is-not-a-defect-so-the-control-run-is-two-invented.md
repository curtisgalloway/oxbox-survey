<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-20
venue: openrouter
model: inclusionai/ling-3.0-flash-vl:free
kind: findings
source: manual
agent: claude-opus-5
corpus: oxbox-clean-control-v2
role: candidate
corrects: 2026-09-20-ling-3.0-flash-vl-free-finished-the-zero-defect-control-where-its-sibling-returned-nothing-two-findings-none-real.md
unresolved: 0
---

# Correction: the missing `dns_lookup` timeout is not a defect, so the control run is 2 emitted, 0 real, 2 invented

**What changed** — Finding 1 of run `2026-09-20T01-51-36Z` was recorded
`unresolved` on the ground that its claim about the code is true —
`dns_lookup` really does lack the `settimeout(5)` its two sibling probes
carry — and that the defect question needed the editor. The editor ruled the
same day: **not a defect.** `unresolved` goes from 1 to 0, so the run reads 2
findings emitted, 0 real, 0 benign, 2 invented. The original observation stays
as written.

**Why `unresolved` was the wrong bucket, and not just the wrong number.** The
field was added on 2026-09-08 for a finding *nobody has adjudicated* — not real,
not benign, not a refutation. It is a placeholder for an open question, not a
category for a finding whose factual claim survives while its defect claim does
not. Finding 1 was adjudicable and was adjudicated; recording it as open
deferred a call that the evidence already in the observation supports. The
probes exist to raise immediately inside the jail, the hang needs DNS
blackholed rather than refused, that state was never reproduced, and the
prescribed fix was measured not to work. A finding that survives none of that
is invented, whatever is true about the line it points at.

**The general rule this settles.** A true statement about the code is not a
finding. The review asked what is wrong with the file, and "these two probes
set a timeout and this one does not" is an observation about style unless
something follows from it. Scoring the factual half and the defect half
separately gives a model credit for reading carefully while it is being wrong
about the thing it was asked, which is the overcorrection the fixture exists to
measure. Under scored-as-written — the 2026-09-10 ruling that already governs
this corpus — the finding is what it claims, and it claimed a defect.

So the record still carries no `unresolved`. The field stays in the schema for
the case it was written for: a finding volunteered beyond a known defect that
nobody has ruled on yet.

## Cost

No run. One ruling and one edit to a count.
