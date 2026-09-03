<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-02
venue: openrouter
model: deepseek/deepseek-v4-flash
kind: findings
source: oxbox-run
agent: claude-opus-5
corpus: oxbox-clean-control
role: baseline
---

# DeepSeek V4 Flash baseline on the clean control: 0 emitted, 0 real, 0 invented — the key's best possible result, from the cheapest model

**What happened** — `oxbox-clean-control` (`jailtest.py` at `6302b12`, 6,096 B,
`--mode review`) put to `deepseek/deepseek-v4-flash`. The whole answer is 266
bytes: "No defects found. The code is correct and handles expected error
conditions properly. All probes correctly distinguish block/success, edge cases
(empty `EXISTING`, root user, missing environment variables) are handled, and no
resource leaks or race conditions exist." The three numbers the key asks for:
**emitted 0, genuinely new and real 0, inventions 0.** Verified by Claude Opus
5, including a read of the run's `reasoning.txt`.

## Evidence

Run `logs/2026-09-03T03-05-50Z`, `context_bytes` 6096, `finish_reason` stop.
Completion 2,400 tokens, 2,231 reasoning. Computed cost $0.0005.

Nothing was emitted, so the verdict table is empty. What the reasoning shows
is the part worth recording: it raised and rejected six candidates instead of
emitting them —

- both pre-registered false positives: "The `REPO_ROOT` variable is never used.
  Not a defect"; `write_probe` was never raised as one;
- the `label_for` empty-`REAL_HOME` case and the `stat_outside` TOCTOU window,
  both declined ("Not a reportable defect");
- and the offline-host case, one sentence from the real defect GPT and GLM
  found: "if the network is down, a block might not be due to the jail" — then
  "That's fine".

So it missed both defects that are real at this pin (the metadata oracle on
`/etc/shadow`, and the network probes passing vacuously offline; both fixed in
oxbox `0090c35`). The one sentence in its answer that overstates is "All probes
correctly distinguish block/success", which is exactly what the network probes
did not do.

## So what

The answer key says an empty answer with a short account of what was checked is
the best possible result here, and this is the first run to produce it. It came
from the cheapest of the five baselines and cost a twentieth of a cent. Read as
an invention measurement it is perfect; read as a discovery measurement it found
nothing, including two real defects two other baselines found. The fixture was
built to measure the first thing, and the key says so — "treat a clean result as
one data point against invention, never as a licence to skip verification on the
real runs" — and this run is the case that sentence was written for.

No marker: this is a baseline, not a candidate.

## Cost

### Under test

| run | model | mode | context | prompt | completion | reasoning | usd |
|---|---|---|---|---|---|---|---|
| `2026-09-03T03-05-50Z` | `deepseek/deepseek-v4-flash` | review | 6,096 B | 1,837 | 2,400 | 2,231 | $0.0005 |

usd is computed from the archived catalog price (2026-09-01.json), not billed: OpenRouter returns the billed figure only when asked, and ox does not ask. Reasoning tokens are inside completion and priced as output.

### Harness

| model | lane | turns | input | output | thinking | cache read | cache write |
|---|---|---|---|---|---|---|---|
| `claude-fable-5-1` | main | 3 | 204 | 3,978 | 846 | 854,867 | 4,300 |
| **total** | | 3 | 204 | 3,978 | 846 | 854,867 | 4,300 |

Window: 2026-09-03T03:22:00 .. 2026-09-03T03:45:00 (given).
Turns observed span 2026-09-03T03:22:33 .. 2026-09-03T03:23:02.

**Upper bound.** Anything else the session did in this window is counted here too.

Harness input+output is 1.0x the model's prompt+completion (4,182 vs 4,237); with cache reads it is 202.7x (859,049).

The harness window covers Fable's write-up of the DeepSeek and GLM runs; the Opus 5 verification ran as a subagent (109,182 tokens, 23 tool uses, 4 min 27 s for four runs) and is not in this session's transcript. Shared by the 2026-09-02 DeepSeek and GLM observations; an upper bound for each.
