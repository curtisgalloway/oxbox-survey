<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-11
venue: ollama
model: qwen3-coder:30b
kind: findings
source: oxbox-run
agent: claude-fable-5-1
corpus: oxbox-clean-control-v2
role: candidate
run: 2026-09-11T02-49-04Z
wall_s: 21
findings: 7
real: 1
benign: 0
usd_model: 0
usd_total: 0.1574901
harness_model: claude-opus-5
harness_venue: openrouter
harness_window: 2026-09-11T02:53Z..2026-09-11T02:54Z
harness_seconds: 37
harness_in: 16408
harness_out: 2922
harness_usd: 0.15509
harness_note: metered; the frontier read of the checking order, one `oxbox send --mode ask --force` request through OpenRouter with the verifier contract and the five pinned files at 6302b12 carrying only QC1, the finding the cheap refuter confirmed, log 2026-09-11T02-53-10Z; usd_total is the pinned GLM-5.3 Flash refuter's bill (0.0024001, its own check record) plus this one
---

# Qwen3-Coder 30B, local, on the zero-defect control at the v2 parameters: seven findings, one real, in 21 seconds, and the refuter and the frontier agreed

**What happened** — `oxbox-clean-control-v2` (`jailtest.py` at `6302b12`,
6,096 B, review mode, effort medium, 16,000 tokens, temperature 1.0, the
reasoning field dropped because ollama refuses it for this model) put to
`qwen3-coder:30b` served by ollama 0.34.0 on argenta, through the local
setup described in
`2026-09-11-qwen3-coder-30b-local-candidate-zero-defect-control-a-thousand-findings-from-five-templates-zero-real-in-25-minutes.md`.
Seven numbered findings and a summary in 21 seconds, 1,009 completion
tokens, where the v1 run of the same model on the same file produced a
thousand findings from five templates in 25 minutes. The first finding is
real: `probe()` catches every exception as containment, so a timeout or a
network misconfiguration that has nothing to do with the jail is scored
PASS, "leading to false confidence in the jail's containment". That is the
record's L1, found by GLM-5.3 Flash and GPT-5.6 Sol on 2026-09-02 and by
qwen3.8 at v1. The other six are inventions. The three numbers the key
asks for: **emitted 7, genuinely new and real 1, inventions 6.**

The batch went through the checking order. The cheap refuter,
`z-ai/glm-5.3-flash` pinned to Together, confirmed QC1 and refuted the six
with cited clauses in 17 seconds for a quarter of a cent. QC1 went to
`anthropic/claude-opus-5`, which confirmed it in 37 seconds for 16 cents
under the contract's narrow exception: the three network probes' PASS does
not depend on the jail blocking anything, so an absent jail certifies as
contained, the silent false-negative direction. Both noted that the
finding's cited line is `IS_ROOT` rather than `probe()` and that its
wording of the detail string is inverted; both scored the substance.
Check records:
`2026-09-11-check-glm-5.3-flash-metered-pinned-to-together-on-qwen3-coder-30bs-zero-defect-control-v2-run-qc1-confirmed-six-refuted.md`,
`2026-09-11-check-opus-5-metered-on-qc1-of-qwen3-coder-30bs-zero-defect-control-v2-run-confirmed-in-37-seconds-for-16-cents.md`.

## Evidence

Log `logs/2026-09-11T02-49-04Z`, `context_bytes` 6096, `finish_reason` stop,
prompt 1,729, completion 1,009.

| # | Finding | Verdict | Why |
|---|---|---|---|
| QC1 | `probe()` catches all exceptions as blocked; a timeout or misconfiguration is reported as containment | **real** | L1 at this pin: `jailtest.py:52-54` scores any raise as `blocked`; the network probes at `:122-124` run unconditionally; a host with no route or a 5-second timeout raises and passes. Confirmed by both checks. |
| QC2 | `listdir` errors in `read_probe` are "not caught by the outer try/except" | **invention** | `read_probe` returns an action that runs inside `probe()`'s `try` (`:50`); every exception is caught. |
| QC3 | a manipulated `HOME` redirects the work-dir writes | **invention** | `oxbox:349` sets `HOME` from the validated work dir and clears the parent environment; the jail confines writes to the work dir. |
| QC4 | a race between parallel jailtest instances on the same file | **invention** | Single-process, sequential; the scenario needs concurrent instances the tree never starts. |
| QC5 | `label_for` mislabels when `REAL_HOME` is empty | **invention** | Standing; the `if REAL_HOME and …` guard at `:43`. |
| QC6 | `env_canary` cannot tell a jail leak from an accidentally present key | **invention** | The parent environment never reaches the jail (`oxbox:348-358`, `--clearenv`); nothing accidental can be present. |
| QC7 | `read(1)` in binary mode may raise `UnicodeDecodeError` | **invention** | Binary mode decodes nothing. |

## So what

A thousand template findings at v1 became seven readable ones at v2, one
of them the network defect that four of five frontier baselines missed on
this file, in 21 seconds on a 14 GB model with no reasoning channel. The
reading cost 16 cents, most of it the frontier read of one finding, and
the order's two readers agreed with each other and with the record. That
is the local row the survey's thesis wants: a cent of electricity, a
quarter of a cent to refute the noise, and the frontier paid only for what
survived.

## Cost

Nothing billed for the run. Checks: the pinned GLM refuter, $0.0024001,
17 seconds; the Opus 5 read of QC1, $0.15509, 37 seconds. `usd_total` is
both, over one real finding.
