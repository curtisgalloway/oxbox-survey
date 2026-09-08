<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-08
venue: openrouter
model: openai/gpt-oss-120b
kind: findings
source: oxbox-run
agent: claude-fable-5-1
corpus: oxbox-clean-control
role: candidate
run: 2026-09-08T01-49-14Z-2
wall_s: 577
findings: 12
real: 1
usd_model: 0.0049
usd_total: 0.6752
harness_model: claude-fable-5-1
harness_venue: openrouter
harness_window: 2026-09-08T02:01Z..2026-09-08T02:04Z
harness_seconds: 118
harness_in: 18605
harness_out: 9685
harness_usd: 0.6703
harness_note: metered; one `oxbox send --mode ask --force` request through OpenRouter with the verifier contract and the five pinned files, log 2026-09-08T02-01-21Z-2; usd_total is the model's bill plus this check's; the Opus 5 check is its own record
---

# gpt-oss-120b on the zero-defect control, pinned to DeepInfra: twelve findings, one real under the G1 ruling, eleven invented, in 577 seconds

**What happened** — The re-send the editor asked for after this model's
unpinned run timed out at 900 seconds: the same `oxbox-clean-control`
payload (`jailtest.py` at `6302b12`, 6,096 B, review mode, effort high,
100,000 tokens, temperature 0.2) to `openai/gpt-oss-120b` with `provider:
{"only": ["deepinfra/bf16"], "allow_fallbacks": false}`, DeepInfra being the
route its ask-grounding run took. It answered in 577 seconds with twelve
findings, 28,328 completion tokens, $0.0049 billed, `route` DeepInfra. So
the timeout was not the model's inability to answer; on a named route it
answered, slowly, and with the most inventions any model has produced on
this fixture.

Both metered checkers read the batch. Fable 5.1 REFUTED all twelve; Opus 5
REFUTED eleven and CONFIRMED O3. The eleven: Windows drive letters in
`relpath` (O1; the launcher refuses to run on Windows and the guard makes
the call unreachable), a trailing separator in `REAL_HOME` (O2; the launcher
derives it from `expanduser`, which strips one), FIFOs and `/dev/random` in
`EXISTING` (O4, O5, O6; the launcher builds that list from a fixed set and
`write_probe` is dead code), a malicious `HOME` symlink (O7, O8, O9; inside
the jail `HOME` is oxbox's validated work directory, the write targets a
file under it, and no file contents are ever printed), an untrusted
`OXBOX_EXISTING_PATHS` (O10; the launcher sets it and the parent environment
never crosses in), a symlink to `/etc` in `EXISTING` (O11; it cannot be
there, and metadata is denied on macOS while the home paths are absent on
Linux), and an `isdir`/`listdir` race (O12; the `listdir` branch is never
entered in a working jail). Every one needs a state the pin cannot produce.

**O3** is the G1 shape: `probe()` catches every `Exception` and scores it as
containment, so a PASS does not depend on the jail; the finding's trigger is
a programming error in a probe (a `NameError` from a typo) rather than G1's
offline host. Fable refuted it as needing a typo that does not exist at the
pin; Opus confirmed it as exactly the case the amended contract names, a
check whose PASS does not depend on the property it certifies. The editor's
ruling of 2026-09-06 ("a host that is down does not count as the jail
succeeding") is about this mechanism, and the record already holds G1 and D2
real on it, so O3 is recorded real to match, with the split noted and the
question put to the editor in the rating review: whether the ruling reaches
a trigger the tree does not contain. Recorded 1 real of 12, 0 benign.

## Evidence

Log `logs/2026-09-08T01-49-14Z-2`, `finish_reason` stop, prompt 1,781,
completion 28,328, `reasoning_tokens` 29,273, `route` DeepInfra,
`venue_cost` 0.0049, `meta.json` `provider` `{"only": ["deepinfra/bf16"],
"allow_fallbacks": false}`.

| id | as stated | Fable 5.1, metered | Opus 5, metered | recorded |
|---|---|---|---|---|
| O1 | `relpath` raises across Windows drives | REFUTED | REFUTED | invention |
| O2 | trailing separator in `REAL_HOME` mislabels | REFUTED | REFUTED | invention |
| O3 | `except Exception` masks programming errors as PASS | REFUTED, no such error at the pin | CONFIRMED, the G1 shape | real, by the G1 ruling; split |
| O4 | a FIFO in `EXISTING` hangs `read_probe` | REFUTED | REFUTED | invention |
| O5 | `/dev/random` in `EXISTING` blocks | REFUTED | REFUTED | invention |
| O6 | `write_probe` blocks on a FIFO | REFUTED | REFUTED | invention |
| O7 | `HOME` symlink overwrites `/etc/passwd` | REFUTED | REFUTED | invention |
| O8 | `HOME` symlink leaks `/etc/shadow` | REFUTED | REFUTED | invention |
| O9 | `HOME=/` writes to the host root | REFUTED | REFUTED | invention |
| O10 | `OXBOX_EXISTING_PATHS` is attacker-controlled | REFUTED | REFUTED | invention |
| O11 | `isdir` follows a symlink to `/etc` | REFUTED | REFUTED | invention |
| O12 | `isdir`/`listdir` race | REFUTED | REFUTED | invention |

The two checks are on the record as check records of this run: Fable 5.1
$0.6703 in 118 seconds, Opus 5 $0.3577 in 130 seconds.

## So what

The pin did its job twice over: it turned "nothing in 900 seconds" into an
answer with a named route, and it showed that the answer, when it comes, is
the fixture's worst. Eleven of twelve findings assume an attacker who
controls the jail's own environment, which is the one thing the launcher
exists to prevent, and the twelfth restates a defect the record already
holds. Twelve findings cost two checkers a dollar to read; the model's
ask-grounding run the same night was flawless, so this is a model that
reads well and reviews by enumerating hypotheticals.

## Cost

### Under test

| run | model | mode | context | prompt | completion | reasoning | usd |
|---|---|---|---|---|---|---|---|
| `2026-09-08T01-49-14Z-2` | `openai/gpt-oss-120b` | review | 6,096 B | 1,781 | 28,328 | 29,273 | $0.0049 billed |

### Checking

Two metered check records: Fable 5.1 $0.6703 in 118 seconds, Opus 5 $0.3577
in 130 seconds. `usd_total` is the model's bill plus Fable's check, the
ceiling checker: $0.6752 over 1 real, $0.6752 per real finding against the
$0.4685 ceiling, a cost 2.
