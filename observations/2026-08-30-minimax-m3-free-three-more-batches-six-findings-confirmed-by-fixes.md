<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-08-30
venue: openrouter
model: minimax/minimax-m3:free
kind: findings
source: manual
agent: claude-fable-5-1
---

# Three more MiniMax M3 batches over oxbox: six findings confirmed by the fixes that shipped, one UNCERTAIN refuted, the rest unverified

**What happened** — on the morning of 2026-08-30 the oxbox session ran three
`--mode review` batches through the 2026-08-29 manifest (since withdrawn), covering
the rest of oxbox: the three sandbox tools, the review queue and jail test at a
commit after the corpus pin, and `ox` itself. Fifteen findings across the three.
The survey has not read each of them against the source. What it has done is read
oxbox's commit log for the same day, which confirms six of them, and read the one
finding the model marked UNCERTAIN against git's documentation, which refutes it.
`source: manual` because the evidence here is the commits, not a finding-by-finding
verification, and nothing in this file should be counted as a verified rate.

## The runs

| Log dir | Files | Context | Prompt | Completion | Reasoning | Findings |
|---|---|---|---|---|---|---|
| `2026-08-30T15-48-35Z` | `oxbox`, `oxseed`, `oxapply` | 34,738 B | 9,210 | 84,042 | 84,822 | 3 |
| `2026-08-30T16-00-50Z` | `.claude/skills/ox-review/scripts/oxreview.py`, `jailtest.py` | 24,968 B | 6,183 | 30,910 | 30,224 | 6 |
| `2026-08-30T16-05-13Z` | `ox` | 39,467 B | 8,912 | 30,437 | 29,700 | 6 |

All three `ox_version` 0.1.0, manifest entry position 1, `finish_reason: stop`,
`truncated: false`. A fourth call in the same hour, `2026-08-30T15-39-09Z`,
returned no content at all: 5,596 completion tokens, every one of them reasoning,
`finish_reason` null. That abort is recorded in
[[2026-08-30-never-reached-had-a-mechanical-cause]].

## Confirmed by a fix

| Run | Finding | Commit, same day |
|---|---|---|
| `15-48-35Z` #1 | `oxseed` validates with `os.walk`, which does not descend symlinked directories, then copies with `copytree(symlinks=False)`, which dereferences them, so `src/inner -> ~/.ssh` lands in the sandbox | `1066b1b` "oxseed: a symlinked directory walked straight past the validator" |
| `16-00-50Z` #2 | a failed `os.replace` in `refresh` is swallowed, so a holder whose lease lapsed keeps running while a waiter breaks the lock | `9da7a00` "oxreview: three ways one queue lock could be held by two batches", whose message says all three were reproduced |
| `16-00-50Z` #3 | `release()` unlinks a holder record it may no longer own | `9da7a00` |
| `16-00-50Z` #4 | a `SIGKILL` between `write_text` and `os.replace` leaves a temp file that wedges `rmdir` | `9da7a00` |
| `16-00-50Z` #6 | `tcp_connect` / `udp_send` leak the socket on the raising path | `6302b12` "jailtest, skill: close the probe sockets" (also found by the 2026-08-29 batch) |
| `16-05-13Z` #4 | the generic credential pattern's `\b` rejects `client_secret` and its quotes reject unquoted values | `6ba47d8` "ox: the scanner missed client_secret, and every unquoted credential"; now the corpus fixture `oxbox-secret-scanner-fix` |

`3d893ed` "guardtest: cover the refusals added for the review findings" is the
regression suite for the set.

## Refuted

`15-48-35Z` #2 argues that `git apply --stat --apply` "likely does not actually
apply the patch", labelled UNCERTAIN. `git-apply(1)` on `--apply`: "If you use any
of the options marked 'Turns off apply' above, git apply reads and outputs the
requested information without actually applying the patch. Give this flag after
those flags to also apply the patch." The flag is given after `--stat`, so the
patch applies. The UNCERTAIN label was warranted and the finding is wrong.

## Not verified

Eight findings: `15-48-35Z` #3 (a temp patch never unlinked); `16-00-50Z` #1 (a
root-only oracle misfire) and #5 (a traceback on a missing `--task-file`);
`16-05-13Z` #1 (truncation detected only on `finish_reason == "length"`), #2
(`error.read()` masking an `HTTPError`), #3 (binary files refused without a
secret scan), #5 (manifest `params` never type-checked) and #6 (UNCERTAIN, an
environment race the model itself calls theoretical). Several are plausible;
none is counted.

## So what

Read with the two verified batches, the picture is consistent: the findings this
model leads with are the ones that get fixed, and the fixes cite the review. Six
confirmations from fifteen findings is a floor, not a rate. The cost of learning
the rate is the eight readings above, and this file exists so that nobody counts
them without doing that.
