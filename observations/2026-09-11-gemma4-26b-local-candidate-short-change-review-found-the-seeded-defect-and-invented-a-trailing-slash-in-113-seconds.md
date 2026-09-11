<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-11
venue: ollama
model: gemma4:26b
kind: findings
source: oxbox-run
agent: claude-fable-5-1
corpus: oxbox-short-change-review
role: candidate
run: 2026-09-11T02-50-25Z
wall_s: 113
findings: 2
real: 1
benign: 0
hits: 1
hits_of: 1
usd_model: 0
usd_total: 0.0016669
harness_model: z-ai/glm-5.3-flash
harness_venue: openrouter
harness_window: 2026-09-11T02:53Z..2026-09-11T02:54Z
harness_seconds: 2
harness_in: 10286
harness_out: 248
harness_usd: 0.0016669
harness_note: metered; the seeded defect is settled by the answer key, so only the second finding went to the cheap refuter, one `oxbox send --mode ask --force` request through OpenRouter pinned to Together with the verifier contract and the five files at 6072d56, log 2026-09-11T02-53-20Z; refuted with a checkable clause, so nothing went to the frontier read
---

# Gemma 4 26B, local, on the short change review: found the seeded defect and invented a trailing slash, in 113 seconds

**What happened** — `oxbox-short-change-review` (commit `6072d56`'s 16-line
change to `jailtest.py` as a diff in the task text, the 5,915-byte
post-change file attached, review mode, effort medium, 16,000 tokens,
temperature 1.0) put to `gemma4:26b` through its `gemma4:26b-64k` tag served
by ollama 0.34.0 on argenta, through the local setup described in
`2026-09-10-qwen3.8-27b-local-candidate-zero-defect-control-nothing-in-900-seconds-on-argenta.md`.
The first run on the fixture. Two findings in 113 seconds, 10,177 completion
tokens, 35,152 characters of reasoning. Defect 1 is the seeded defect,
stated the way the key describes it: the `stat_outside` probe is not
skipped when `IS_ROOT` and `EXISTING[0]` is `/etc/shadow`, "violating the
comment's promise that a probe that cannot test should skip", with the
scenario of `OXBOX_EXISTING_PATHS` set to `/etc/shadow` as root and the
`[FAIL] fs metadata: stat /etc/shadow (oracle) (succeeded)` line quoted.
Defect 2 says the skip's exact-string match misses `/etc/shadow/` with a
trailing slash. The launcher builds `EXISTING` from fixed literals and never
emits one. **hits 1 of 1; emitted 2, real 1, invented 1.** Neither of the
two real defects outside the change was raised, and nothing was labeled
OUT OF SCOPE.

## Evidence

Log `logs/2026-09-11T02-50-25Z`, `context_bytes` 5915, `finish_reason` stop,
prompt 2,479, completion 10,177. Defect 1 against the key: a hit, framed
as uid 0 with `EXISTING[0]` = `/etc/shadow`, a state a root CI container
produces; the key accepts that framing and names `a113e62` as the fix.
Defect 2 went to the cheap refuter (`z-ai/glm-5.3-flash`, pinned to
Together), which refuted it in two seconds for $0.0017: `sensitive_paths`
in `oxbox` joins fixed names onto the real home and appends the literal
`/etc/shadow`, so the list never carries a trailing slash and the skip
always matches. Confirmed against `oxbox:93-107` at the pin. That check is
`2026-09-11-check-glm-5.3-flash-metered-pinned-to-together-on-gemma4-26bs-short-change-review-run-the-trailing-slash-refuted-in-two-seconds.md`.

## So what

The first result on the short arm is the one the literature predicted and
the reason the arm exists: on a 16-line change, the model that gave the
zero-defect control "The code is fine." two minutes of reasoning ago found
the one real defect in the change in two minutes, and added one invention
the key had not pre-registered but which fell to the cheapest check in the
record. On the 6 KB whole file this model found neither real defect at
either parameter set. Same model, same day, same hardware; the difference
is the size of what it was asked to look at.

## Cost

Nothing billed for the run. The check was one refuter request, $0.0016669,
two seconds; the seeded defect needed no check.
