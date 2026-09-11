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
corpus: oxbox-clean-control-v2
role: candidate
run: 2026-09-11T02-25-14Z
wall_s: 85
findings: 5
real: 0
benign: 0
usd_model: 0
usd_total: 0.1154344
harness_model: claude-opus-5
harness_venue: openrouter
harness_window: 2026-09-11T02:35Z..2026-09-11T02:36Z
harness_seconds: 17
harness_in: 16484
harness_out: 1223
harness_usd: 0.112995
harness_note: metered; the frontier read of the checking order, one `oxbox send --mode ask --force` request through OpenRouter with the verifier contract and the five pinned files at 6302b12 carrying only GP4, the one finding the cheap refuter confirmed, log 2026-09-11T02-35-38Z; usd_total is the pinned GLM-5.3 Flash refuter's bill (0.0024394, its own check record) plus this one; the unpinned refuter attempt that failed billed nothing
---

# gpt-oss 20B, local, on the zero-defect control at the v2 parameters, second run: five findings, zero real, in 85 seconds, checked cheap then dear

**What happened** — `oxbox-clean-control-v2` (`jailtest.py` at `6302b12`,
6,096 B, review mode, effort medium, 16,000 tokens, temperature 1.0) put to
`gpt-oss:20b` through its `gpt-oss:20b-64k` tag served by ollama 0.34.0 on
argenta, a second time seven minutes after the first
(`2026-09-11-gpt-oss-20b-local-candidate-zero-defect-control-v2-six-findings-zero-real-in-46-seconds-refuted-for-a-fifth-of-a-cent.md`);
the repeat came from a batch driver that should have been stopped, and
both runs are valid at the task's parameters. Five findings in 85 seconds,
5,977 completion tokens, 21,923 characters of reasoning, two of them
carried over from the first run (the empty-string variable, `label_for`)
and three new. The three numbers the key asks for: **emitted 5, real 0,
inventions 5.**

This run went through the whole checking order. No finding was executable.
The cheap refuter, `z-ai/glm-5.3-flash`, failed unpinned on Wafer and then,
pinned to Together, refuted four and confirmed GP4 for a quarter of a
cent. GP4 alone went to the frontier read, `anthropic/claude-opus-5`, which
refuted it in 17 seconds for 11 cents: nothing in the tree makes the file
read-only, the scenario needs an out-of-tree chmod inside a gitignored,
re-seeded sandbox, and even then the effect is a spurious FAIL, the safe
direction. Three check records:
`2026-09-11-glm-5.3-flash-as-the-cheap-refuter-routed-to-wafer-spent-13k-tokens-reasoning-and-returned-an-error-in-317-seconds.md`,
`2026-09-11-check-glm-5.3-flash-metered-pinned-to-together-on-gpt-oss-20bs-repeated-zero-defect-control-v2-run-four-refuted-one-confirmed.md`,
`2026-09-11-check-opus-5-metered-on-gp4-of-gpt-oss-20bs-repeated-zero-defect-control-v2-run-refuted-in-17-seconds-for-11-cents.md`.

## Evidence

Log `logs/2026-09-11T02-25-14Z`, `context_bytes` 6096, `finish_reason` stop,
prompt 1,795, completion 5,977.

| # | Finding | Verdict | Why |
|---|---|---|---|
| GP1 | the summary prints `len(results)` twice, so a failing run still shows N/N | **invention** | `jailtest.py:168-171`: a run with any failure exits through the JAIL LEAKS branch at `:170` and never reaches the "jail holds" line; when that line prints, every probe passed and N/N is true. |
| GP2 | `env_canary` ignores an inherited empty-string variable | **invention** | Standing; the launcher builds the environment from a fixed dict (`oxbox:348-358`). |
| GP3 | `label_for` leaves a path equal to `REAL_HOME` unlabeled | **invention** | No path in `EXISTING` is ever `REAL_HOME` itself (`oxbox:93-107` joins a name onto it); and the finding says itself the effect is cosmetic. |
| GP4 | `jailtest-ok.txt` is never deleted, so a later chmod to read-only from outside makes `write_inside` FAIL | **invention** | Refuted by the frontier read as written: the state needs an out-of-tree chmod inside the sandbox work dir that oxseed re-seeds, and the consequence is a false FAIL, the safe direction. The refuter had confirmed it by taking the scenario as given. |
| GP5 | a race "in a future revision" with threads | **invention** | The finding concedes no race exists at this pin. |

## So what

Two runs at the same parameters gave six and five inventions with two in
common, and the second run's reading cost 12 cents where the first cost a
fifth of a cent, because the cheap refuter let one hypothetical through
and the order sent it up. That is the order working as written: the
frontier read saw one finding instead of five, and its bill was a third of
what reading all nine of Opus 5's own findings cost on 2026-09-10. The
refuter's one confirm was a finding whose mechanism is real and whose
scenario needs an outside actor, which is the shape the contract's
"cannot produce" clause exists for and the shape a cheap reader is most
likely to wave through.

## Cost

Nothing billed for the run. Checks: the unpinned GLM attempt, nothing
billed, 317 seconds; the pinned GLM check, $0.0024394, 61 seconds; the
Opus 5 read of GP4, $0.112995, 17 seconds. `usd_total` is the two bills.
