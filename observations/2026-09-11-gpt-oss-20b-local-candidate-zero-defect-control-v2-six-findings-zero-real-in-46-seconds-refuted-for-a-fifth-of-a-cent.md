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
run: 2026-09-11T02-18-42Z
wall_s: 46
findings: 6
real: 0
benign: 0
usd_model: 0
usd_total: 0.0022445
harness_model: z-ai/glm-5.3-flash
harness_venue: openrouter
harness_window: 2026-09-11T02:21Z..2026-09-11T02:22Z
harness_seconds: 14
harness_in: 11110
harness_out: 1156
harness_usd: 0.0022445
harness_note: metered; the cheap refuter of the checking order decided 2026-09-10, one `oxbox send --mode ask --force` request through OpenRouter (route Together) with the verifier contract and the five pinned files at 6302b12, log 2026-09-11T02-21-44Z; every finding refuted with a cited line the reader confirmed in the pin, so nothing went to the frontier check; the GLM check is its own record
---

# gpt-oss 20B, local, on the zero-defect control at the v2 parameters: six findings, zero real, in 46 seconds, refuted for a fifth of a cent

**What happened** — `oxbox-clean-control-v2` (`jailtest.py` at `6302b12`,
6,096 B, review mode, **effort medium, 16,000 tokens, temperature 1.0**) put
to `gpt-oss:20b` through its `gpt-oss:20b-64k` tag (`num_ctx` 65,536) served
by ollama 0.34.0 on argenta, through the local setup described in
`2026-09-10-qwen3.8-27b-local-candidate-zero-defect-control-nothing-in-900-seconds-on-argenta.md`.
A six-row table of defects and a conclusion that "all listed items are
confirmed logical bugs", in 46 seconds, 3,985 completion tokens, 13,902
characters of reasoning. At the v1 parameters the same model on the same
file wrote "Ok." a thousand times and returned nothing in 22 minutes. The
three numbers the key asks for: **emitted 6, genuinely new and real 0,
inventions 6.** Three of the six are the record's standing inventions and
three are hypothetical future edits presented as defects.

This is the first run checked under the order decided 2026-09-10: no
finding was executable, so the batch went to a cheap refuter,
`z-ai/glm-5.3-flash` through OpenRouter, which refuted all six with a cited
line each in 14 seconds for $0.0022. Each citation was confirmed against
the pin below, so nothing went on to a frontier check. That record is
`2026-09-11-check-glm-5.3-flash-metered-on-gpt-oss-20b-locals-zero-defect-control-v2-run-six-refuted-for-a-fifth-of-a-cent.md`.

## Evidence

Log `logs/2026-09-11T02-18-42Z`, `context_bytes` 6096, `finish_reason` stop,
prompt 1,795, completion 3,985.

| # | Finding | Verdict | Why |
|---|---|---|---|
| GO1 | `label_for` concatenates `REAL_HOME + os.sep` when `REAL_HOME` is empty, so every absolute path is labeled `~/…` | **invention** | `jailtest.py:43` reads `if REAL_HOME and path.startswith(…)`; the guard is the first clause. With it empty the raw path is returned. The launcher sets `REAL_HOME` anyway (`oxbox:350`). |
| GO2 | `env_canary` ignores an inherited empty-string variable | **invention** | The standing one (Opus 5's 8, Gemini 3.8 Flash's 2, qwen3.8's QW5): the launcher builds the environment from a fixed dict (`oxbox:348-358`) and `--clearenv` on Linux; nothing inherited reaches the jail, empty or not. |
| GO3 | `probe()` is "fragile" if `blocked` becomes non-boolean "in the future" | **invention** | `jailtest.py:51,53` assign the literals `False` and `True`; the scenario is a future edit. |
| GO4 | an `expect_blocked=False` probe records FAIL if its function raises by mistake, e.g. a `NameError` "temporarily" added to `env_canary` | **invention** | The scenario is a hypothetical edit to the test, and the effect it describes is a failure in the safe direction. |
| GO5 | empty `HOME` makes the work-dir probes write a relative path | **invention** | Standing (Sonnet's hedge, Opus 5's 2, qwen3.8's QW9): `oxbox:349` sets `HOME` to the work dir on both backends. |
| GO6 | `read_inside` would leak a descriptor "if the `with` statement were mistakenly removed" | **invention** | `jailtest.py:118` is a `with` block; the finding says so itself. |

The reasoning (13,902 characters) is not a loop: it reads the file once,
lists candidate concerns, and writes the table.

## So what

The parameters ended the loop and did not end the inventing. Forty-six
seconds instead of 22 minutes, six findings instead of none, and every one
of the six is either a standing invention or a hypothetical the file does
not contain. On the invention axis this row sits with GPT-5.6 Sol's 8/1/6
and Opus 5's 9/1/7, minus the real find. What is new is the bill for
reading it: a fifth of a cent through a cheap refuter that cited the right
line six times, against 34 cents for the Opus 5 read of qwen3.8's ten a few
hours earlier. Whether a cheap refuter is right when a finding is real is the
question the next confirmed batch answers; on an all-invented batch it was
right six times.

## Cost

Nothing billed for the run. The check was metered: one `oxbox send --mode
ask --force` request to `z-ai/glm-5.3-flash` through OpenRouter, 11,110
prompt and 1,156 completion tokens (443 reasoning), 14 seconds, $0.0022445
billed, log `2026-09-11T02-21-44Z`. Confirming its six citations against
the pin took the reader a few minutes and is the harness window above.
