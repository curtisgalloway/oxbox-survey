<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-02
venue: openrouter
model: anthropic/claude-sonnet-5
kind: findings
source: oxbox-run
agent: claude-fable-5-1
corpus: oxbox-clean-control
role: baseline
---

# Sonnet 5 baseline on the clean control: 2 findings emitted, 0 new and real, 1 invention; 3 UNCERTAIN items, all correctly hedged

**What happened** — `oxbox-clean-control` (`jailtest.py` at `6302b12`, 6,096 B,
`--mode review`) put to `anthropic/claude-sonnet-5`. The answer key's expected
finding count is zero. It emitted two definite findings and three items it labelled
UNCERTAIN itself. The three numbers the key asks for: **emitted 2, genuinely new and
real 0, inventions 1** — the second definite finding is the `write_probe` dead code
the key pre-registers as a false positive. The first is a correct description of a
mechanism attached to a consequence neither jail backend can produce. None of the
three UNCERTAIN items is a defect, and each was hedged rather than asserted.

## Evidence

Run `logs/2026-09-03T02-27-05Z`, `context_bytes` 6096, `finish_reason` stop.
Verified against `git show 6302b12:jailtest.py`, `6302b12:profiles/jail.sb` and
`6302b12:oxbox`.

| # | Finding | Verdict |
|---|---|---|
| 1 | `read_probe`'s `os.path.isdir` branch is defeated by the jail's stat denial, so a leaked directory gets `open()` → `IsADirectoryError` → a false PASS | **mechanism accurate, consequence unreachable.** Inside the jail `isdir` does return False for every hidden path, so `listdir` never runs. But the claimed false PASS needs a jail that denies `stat` on a path while allowing it to be listed. seatbelt's profile is `(deny default)` with `file-read*` — data and metadata together — allowed per path (`jail.sb` lines 6, 28, 60–67; there is deliberately no global `file-read-metadata`), so a directory that leaks also leaks its `stat`, `isdir` is True, `listdir` runs and the leak is reported. bubblewrap never binds the hidden paths in at all. Not a defect at this pin. |
| 2 | `write_probe` is dead code; writability of sensitive paths is never tested | **invention**, the one the answer key names. The file's own comment block above `env_canary` explains why escape-write verification lives in `guardtest.py`: judged from inside the jail the two backends disagree. |

UNCERTAIN, in the model's own section under that heading:

| Item | Verdict |
|---|---|
| `udp_send`: `sendto` can succeed locally when a firewall silently drops | not applicable: `(deny network*)` makes the syscall raise, which is what the probe measures; the silent-drop model is a firewall's, not a sandbox's. Correctly hedged. |
| `WORK` from `HOME` could be empty, testing the wrong directory | unreachable as launched: `oxbox` sets `HOME` to the work dir in the jail environment (`oxbox` line 349), and the prompt states the file runs under `./oxbox`. Correctly hedged. |
| `env_canary`'s list is hand-maintained against `VENUES` | a maintenance note the file already makes in its own docstring ("the two lists move together"), not a defect. Correctly hedged. |

It closed with "No resource leaks or race conditions were found: all socket and
file operations use `with` blocks", which is true at this pin and is the defect
MiniMax found at the previous one.

Completion 15,546 tokens, 13,833 of them reasoning — the most expensive of the
three Sonnet runs, on the smallest file.

## So what

The fixture measures invention rate directly, and the baseline's is not zero: one
pre-registered false positive, asserted as a definite finding with a failure
scenario, on a 6 KB file. That is the number a free model's clean-control run
should be read against — not "did it find nothing" but "how many things did it
assert that a careful reader would strike". The UNCERTAIN section is the better
news: three things it was unsure about, all placed below a heading that says so,
none of them wrong to raise. The split between the two sections is exactly the
calibration the survey says it wants and has had no reference for until now.

Under a prompt asking for breadth, the ideal answer here is short. This one was
long and cost more reasoning than the 39 KB `ask` run by a factor of thirty.

No marker: this is a baseline, not a candidate.

## Cost

### Under test

| run | model | mode | context | prompt | completion | reasoning | usd |
|---|---|---|---|---|---|---|---|
| `2026-09-03T02-27-05Z` | `anthropic/claude-sonnet-5` | review | 6,096 B | 2,809 | 15,546 | 13,833 | $0.1611 |

usd is computed from the archived catalog price (2026-09-01.json), not billed: OpenRouter returns the billed figure only when asked, and ox does not ask. Reasoning tokens are inside completion and priced as output.

### Harness

| model | lane | turns | input | output | thinking | cache read | cache write |
|---|---|---|---|---|---|---|---|
| `claude-fable-5-1` | main | 16 | 3,638 | 37,379 | 12,965 | 2,492,296 | 60,532 |
| **total** | | 16 | 3,638 | 37,379 | 12,965 | 2,492,296 | 60,532 |

Window: 2026-09-03T02:24:00 .. 2026-09-03T02:36:00 (given).
Turns observed span 2026-09-03T02:24:03 .. 2026-09-03T02:32:39.

**Upper bound.** Anything else the session did in this window is counted here too.

Harness input+output is 2.2x the model's prompt+completion (41,017 vs 18,355); with cache reads it is 138.0x (2,533,313).

The harness window covers all three Sonnet runs and their verification, plus the scorer being written; it is shared by the three 2026-09-02 Sonnet observations and is an upper bound for each.
