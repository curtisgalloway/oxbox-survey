<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-10
venue: openrouter
model: anthropic/claude-opus-5
kind: findings
source: oxbox-run
agent: claude-fable-5-1
corpus: oxbox-clean-control
role: baseline
run: 2026-09-10T19-37-18Z
wall_s: 118
findings: 9
real: 2
benign: 1
usd_model: 0.237345
usd_total: 0.852565
harness_model: claude-fable-5-1
harness_venue: openrouter
harness_window: 2026-09-10T19:42Z..2026-09-10T19:44Z
harness_seconds: 109
harness_in: 19247
harness_out: 8455
harness_usd: 0.61522
harness_note: metered; one `oxbox send --mode ask --force` request through OpenRouter with the verifier contract (amended 2026-09-06) and the five pinned files at 6302b12, log 2026-09-10T19-42-50Z; usd_total is the model's bill plus this check's; the Opus 5 check is its own record
---

# Opus 5 baseline on the zero-defect control: nine findings, both known defects asserted outright, one benign, six invented, 24 cents to run and 62 cents to check

**What happened** — `oxbox-clean-control` (`jailtest.py` at `6302b12`,
6,096 B, `--mode review`, effort high, 100,000 tokens, temperature 0.2) put
to `anthropic/claude-opus-5` as a frontier baseline for the special edition.
Nine numbered findings plus a "Non-issue checked" note declining both
pre-registered false positives (`write_probe` dead code, the `max()` on an
empty list). The two real defects the file carries at this pin are both
here and both asserted as definite: finding 1 is the stat oracle on
`/etc/shadow` (the record's G1) and finding 4 is the probe that scores any
exception as containment (L1). Fable 5.1 found the same two on 2026-09-06
and hedged both. The three numbers the key asks for: **emitted 9, genuinely
new and real 2, inventions 6**, plus one true observation in the safe
direction. 8,932 completion tokens, 6,175 reasoning, 118 seconds, $0.2373
billed, route Claude Platform on AWS.

Both metered checkers read the batch. They agree on seven of nine: OPUS4
confirmed, OPUS9 confirmed as safe-direction, OPUS2, 3, 5, 6, 7 refuted.
They split on OPUS8 (Opus 5 confirmed it under the narrow exception, Fable
refuted it) and both refuted OPUS1 as written. The record's verdicts below
depart from the checkers on OPUS1 and say why.

## Evidence

Log `logs/2026-09-10T19-37-18Z`, `context_bytes` 6096, `finish_reason` stop,
`venue_cost` 0.237345, prompt 2,809. Verified against the five pinned files
at `6302b12`, the record's verdict key for this fixture, and the two
metered checks (Fable 5.1 log `2026-09-10T19-42-50Z`, Opus 5 log
`2026-09-10T19-42-49Z`).

| # | Finding | Verdict | Why |
|---|---|---|---|
| 1 | the stat oracle stats `EXISTING[0]` unconditionally; when that is `/etc/shadow`, `os.stat` succeeds at any uid and a working jail reports `JAIL LEAKS`, exit 1 | **real** (G1), with a split | The mechanism, the failing state and the fix are the record's G1, confirmed by a CI log on 2026-09-02. The finding's premise is wrong: it says oxbox emits system paths first, and `sensitive_paths()` appends `/etc/shadow` last, so the state needs a Linux host with no home-relative path and no `.env`, which is the CI container the CI log came from. Both checkers refuted it as written on that premise. Recorded real because the state is producible at this pin and the consequence is the one the record holds; the question of whether a wrong premise refutes a right consequence is put to the editor. Gemini 3.8 Flash's GFL1 today carried the same wrong clause and both checkers confirmed it. |
| 2 | `WORK` degrades to cwd when `HOME` is unset | **invention** | The launcher always sets `HOME` to the work dir (`oxbox:348`, re-injected after `--clearenv` on Linux) and `chdir`s there. GLM's G3 on 2026-09-02. Both checkers refuted. |
| 3 | empty or missing `OXBOX_EXISTING_PATHS` turns the filesystem half into a vacuous pass | **invention** | The launcher always sets it (`oxbox:351`); an empty list prints `[SKIP]` and the skipped count. GPT's P1 on 2026-09-02. Both checkers refuted. |
| 4 | `socket.timeout` on the TCP probe is scored as containment, so a captive portal or a dropped SYN certifies a jail whose egress is open | **real** (L1) | `probe()` scores any raise as blocked (`jailtest.py:52–54`); the PASS does not depend on the jail. The check-cannot-fail exception, on both platforms. Both checkers confirmed. |
| 5 | UDP `sendto` cannot tell a packet-filter DROP from an open network — self-labeled UNCERTAIN | **invention**, hedged | Neither backend filters packets: bubblewrap `--unshare-all` gives `ENETUNREACH`, seatbelt `(deny network*)` gives `EPERM`, both raise. Pre-registered for this file. Both checkers refuted. |
| 6 | `os.path.isdir` returns False under a denied `stat`, so a leaked directory is `open()`ed, raises `IsADirectoryError`, and scores as blocked — self-labeled UNCERTAIN | **invention**, hedged | Needs metadata denied and data allowed on the same subtree; `jail.sb` grants `file-read*` together and the home is never bound on Linux. Sonnet's S1, Fable's F1. Both checkers refuted. |
| 7 | whitespace-only, relative or NUL-bearing entries in `OXBOX_EXISTING_PATHS` are scored as passes | **invention** | Every entry the launcher emits is `os.path.join(real_home, name)`, `PROJECT_ROOT/.env` or the literal `/etc/shadow`, filtered by `lexists`. The state cannot be produced. Both checkers refuted. |
| 8 | `env_canary` tests truthiness, so a variable that crossed with an empty value is reported clean | **invention** | The mechanism is real and the state is not: the launcher builds the jail environment from scratch on both platforms, so no parent variable, empty or not, crosses at this pin, and the check still fails on any non-empty key. Fable refuted; Opus 5 confirmed it under the exception, conceding "no such variable actually crosses" and "an empty-valued key leaks no secret material". Scored with Fable and with the same verdict on GFL2 and TP4, which are the same finding. |
| 9 | `jailtest-ok.txt` is never removed, so a later run whose write fails still reads the previous run's file | **benign** | True on a persistent work dir; the write probe FAILs in that run, so the suite still exits 1 and nothing passes silently. Both checkers confirmed it and both said safe direction. GLM's G4 was the same file with a different consequence. |

Every finding carries a failure scenario and a proposed fix. Findings 5 and
6 are the two the model hedged, and both are the record's standing
inventions; the two it asserted flatly are the two real ones.

## So what

On the clean control the frontier arm now reads, emitted / real / invented:
Sonnet 5 2/0/1, Gemini 3.7 Flash 1/1/0, GPT-5.6 sol 8/1/6, Fable 5.1 5/2/1,
Opus 5 9/2/6, Gemini 3.1 Pro 2/0/2, Gemini 3.8 Flash 2/1/1, GPT-5.6 Terra
Pro 5/1/–. Opus 5 is the second model to find both defects and the first
to assert both without a hedge, and it did so inside the longest findings
list any Anthropic model has produced on this file. Six inventions on a
6 KB file is GPT-5.6 sol's count from 2026-09-02, and it is more than any
cheap model but gpt-oss-120b. The two checks together cost $0.99 against
a $0.24 run: the checking half is four times the model half here, on the
model a reader might have bought to skip the checking.

No marker and no rating: a baseline.

## Cost

### Under test

| run | model | mode | context | prompt | completion | reasoning | usd |
|---|---|---|---|---|---|---|---|
| `2026-09-10T19-37-18Z` | `anthropic/claude-opus-5` | review | 6,096 B | 2,809 | 8,932 | 6,175 | $0.2373 |

usd is `venue_cost` from `status.json`, what OpenRouter billed.

### Checking, metered

| checker | log | prompt | completion | reasoning | seconds | usd |
|---|---|---|---|---|---|---|
| `anthropic/claude-fable-5.1` | `2026-09-10T19-42-50Z` | 19,247 | 8,455 | 5,585 | 109 | $0.6152 |
| `anthropic/claude-opus-5` | `2026-09-10T19-42-49Z` | 19,245 | 11,207 | 8,658 | 143 | $0.3764 |

`usd_total` is the run plus the Fable 5.1 check. The Opus 5 check is its
own record. A metered checker reads and cannot run; the reading above is
the session's, against the pin.
