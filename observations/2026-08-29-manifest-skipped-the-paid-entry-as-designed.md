<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-08-29
venue: openrouter
model: "-"
kind: access
source: oxbox-run
agent: claude-opus-5
---

# The survey manifest resolved a real run: paid entry skipped, free entry used, provenance recorded

**What happened** — the first runs driven by a survey manifest rather than by
explicit `--venue`/`--model` flags. `ox` read
`manifests/oxbox-manifest-2026-08-27.json`, skipped rank 1 because it is paid and
`--allow-paid` was not passed, and sent the request to rank 2.

## Evidence

From `logs/2026-08-30T01-11-26Z/status.json` (identical in the 01-14-28Z run):

```json
"attempts": [
 {"model": "z-ai/glm-5.3-flash", "position": 1,
  "skipped": "cost=paid (pass --allow-paid to use it)", "venue": "openrouter"},
 {"finish_reason": "stop", "model": "minimax/minimax-m3:free",
  "position": 2, "venue": "openrouter"}
],
"manifest": {"path": ".../manifests/oxbox-manifest-2026-08-27.json",
             "sha256": "92cfb2bae998c782bd0079f052e585a6fa78b5a20d0671ef0916f1b7fdc65d26"},
"ox_version": "0.2.0", "truncated": false, "exit_code": 0
```

## So what

Three things the design promised are now Measured rather than argued. Paid
entries are skipped by default, so a manifest cannot quietly spend money. The
run record carries the manifest's path *and* its sha256, so an issue can cite
which recommendation list produced a result and a reader can check that the file
has not changed since. And `ox_version` is in the record, so the version floor an
artifact was produced under is a fact rather than an assumption.

The skip is also visible in the attempts list rather than silent, which is what
makes the first two claims checkable at all.
