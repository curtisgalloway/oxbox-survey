<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-08-30
venue: openrouter
model: minimax/minimax-m3:free
kind: findings
source: oxbox-run
agent: claude-fable-5-1
---

# MiniMax M3 free: 7 of 12 findings real on the exposure gate, and a re-framed prompt found the defect the neutral one missed

**What happened** — a second `--mode review` batch over the same two files as the
2026-08-29 exposure-gate run
([[2026-08-29-minimax-m3-free-13-of-15-findings-real]], batch A), at the same
commit, with a task text that names the stakes: a false `public` verdict is the
worst possible failure. Twelve findings; seven hold up against the source as sent,
and two of those were fixed in oxbox eighteen minutes later. The headline, a
cross-host redirect that turns a private repository into a `public` verdict, was
not among the ten findings the neutral prompt produced on 2026-08-29. The same
payload went to `nemotron-3-ultra-free` three minutes later
([[2026-08-30-nemotron-3-ultra-free-2-of-10-findings-real-on-the-exposure-gate]]).
Verified 2026-09-01 against the payload in `request.json`.

## The run

| Log dir | Venue / model | Files | Prompt | Completion | Reasoning | Finish | Wall |
|---|---|---|---|---|---|---|---|
| `2026-08-30T22-26-09Z` | openrouter / `minimax/minimax-m3:free` | `.claude/skills/ox-review/scripts/exposure.py`, `.claude/skills/ox-review/scripts/preflight.py` | 7,198 | 30,712 | 29,933 | stop | 188.9 s |

`ox_version` 0.3.0, driven by the 2026-08-29 manifest (since withdrawn) at entry
position 1, `truncated: false`, served by `GMICloud` per the response. Reasoning is
97% of completion, as on 2026-08-29.

**Payload.** Files identical to `git show 6072d56:<path>` (27,246 bytes, the
`oxbox-exposure-gate` pin) and to the 2026-08-29 batch A run. The system prompt is
unchanged between ox 0.2.0 and 0.3.0. The task text differs from the fixture's:
748 characters longer, adding that everything sent is logged and shared, that
`exposure.py`'s verdict "is the gate that decides whether any code may leave the
machine, so a false 'public' is the worst possible failure and a false
'not-public' is merely annoying". Not the fixture, so no `corpus:` field.

## Findings, verified against the payload

| # | Finding | Verdict |
|---|---|---|
| 1 | `fetch` follows cross-host redirects, so a host that 302s to any public repository's ref advertisement gets a `public` verdict; the cross-check cannot catch it because it only fires when the clone probe returns False | **real, critical.** Fixed in oxbox `d2f2e44` (2026-08-30 22:44Z) with an end-to-end reproduction against a local server; the commit's account of the mechanism matches this finding line for line |
| 2 | "network failure cannot become a false positive — good", but when the API is unreachable the clone probe is the sole signal and is the only one that can be redirected | a restatement of 1, accurately framed as such. Not a separate defect |
| 3 | no `timeout=` on the `ox --version` subprocess | **real, minor** (batch A's finding 4). Still open at oxbox HEAD |
| 4 | no `timeout=` on the exposure-gate subprocess, and a missing `exposure.py` raises an uncaught `FileNotFoundError` | **half real.** The missing timeout is real: `exposure.py` bounds each probe, but `urlopen`'s timeout does not cover DNS resolution, so a hung resolver hangs preflight. The second half is wrong: `sys.executable` is the running interpreter, so `subprocess.run` cannot raise `FileNotFoundError` here; a missing script exits non-zero with empty stdout, `json.loads("")` raises `ValueError`, and the existing `except` turns that into an `unknown` verdict |
| 5 | `ox --version` return code ignored, stderr folded into the reported version, no blocker recorded | **real** (batch A's finding 8). Still open at HEAD |
| 6 | `find_ox` executes `./ox` from the current directory after PATH fails, and the `OXBOX_HOME` fallback re-checks the cwd when unset, so the lookup cannot be disabled | **real** as a supply-chain path: preflight runs from the root of the repository under review, which may be somebody else's checkout. Reachable only when `ox` is neither explicit nor on PATH. Still open at HEAD |
| 7 | the scp-style regex misparses `git@host:2222:owner/repo` into owner `2222:owner` | **false positive.** scp-style syntax has no port form; git itself reads `2222:owner/repo` as the path, and a host without a dot does not match the regex at all and falls through to `urlsplit`, which returns None |
| 8 | the cross-check is one-directional: API says private but clone succeeds stays `not-public` | true, and the model says itself it is the safe direction. Not a defect |
| 9 | bare `except Exception` in `fetch` hides programming errors as probe failures | **real, minor** (batch A's finding 1); fails safe |
| 10 | `describe_manifest` reads bytes and then stats mtime, a TOCTOU | true, negligible, and labelled cosmetic by the model (batch A's finding 10) |
| 11 | `PICK_LINE` / `SKIP_LINE` use `\S+`, rejecting names with whitespace, and a multi-line skip reason keeps only its first line | speculative: no venue or model id contains whitespace and ox prints one-line reasons. Not a defect |
| 12 | the "no license detected" note fires for every listed host, but only some hosts' APIs carry a license field | **real.** Fixed in `d2f2e44`: Forgejo/Gitea and Bitbucket have no license field, so three of five hosts had the API's shape reported as a fact about the repository. The commit also found what neither model did: the note fired on private repositories too |

Seven real (1, 3, 4 in part, 5, 6, 9, 12), of which two were fixed the same
afternoon. Three true observations that are not defects (2, 8, 10). One
speculative (11). One false positive (7). One wrong mechanism inside a real
finding (4).

## The prompt moved the findings

Same model, same files, same commit, same system prompt, a different task
paragraph, one day apart:

| | 2026-08-29 (neutral) | 2026-08-30 (framed) |
|---|---|---|
| findings | 10 | 12 |
| real | 8 | 7 |
| in common | 5 | 5 |
| found only with this prompt | URL-encoding inconsistency, empty remote URL read as confident `not-public`, port dropped from host, `ahead != "0"` (false), conditional-in-tuple (not a defect) | the redirect, the gate-subprocess timeout, the license note, the scp port (false), the one-directional cross-check, the regex fragility |

The one finding that mattered for the gate's purpose appeared only when the
prompt said what the gate was for. That is an argument for the corpus rule that a
prompt is part of the fixture, and an argument against reading a fixture's
finding count as a property of the model alone.

## So what

Second `source: oxbox-run` result for this model, same direction as the first: a
majority of findings real, a critical one among them, UNCERTAIN not used where it
should have been (4, 7) but not misused either. Two of four exposure-gate
findings that oxbox acted on came from this run. Sample is still one repository
and one language.

## Cost

Both halves, from `costcheck.py`. The harness window is the oxbox session
(`claude-opus-5`) that assembled both batches of the matched pair, verified the
redirect finding and committed the fix; it is shared with the Nemotron observation
and counted once.

```
### Under test

| run | model | mode | context | prompt | completion | reasoning | cost |
|---|---|---|---|---|---|---|---|
| 2026-08-30T22-26-09Z | minimax/minimax-m3:free | review | 27,246 B | 7,198 | 30,712 | 29,933 | free |
| 2026-08-30T22-29-19Z | nemotron-3-ultra-free   | review | 27,246 B | 7,262 |  4,872 |  2,961 | -    |

### Harness (batch assembly, one finding verified, fix committed)

| model         | lane | turns | input | output | thinking | cache read | cache write |
|---|---|---|---|---|---|---|---|
| claude-opus-5 | main | 34    | 68    | 32,602 | 9,343    | 12,432,907 | 49,529      |

Window: 2026-08-30T22:20:00 .. 2026-08-30T22:50:00 (given).
Turns observed span 2026-08-30T22:25:20 .. 2026-08-30T22:47:01.
```

Upper bound: anything else that session did in the window is counted. The
verification of all twelve findings above was done on 2026-09-01 in a survey
session; its window is reported below.

### Verification of this file's findings (survey session, 2026-09-01)

```
| model            | lane | turns | input | output | thinking | cache read | cache write |
|---|---|---|---|---|---|---|---|
| claude-fable-5-1 | main | 6     | 1,048 | 60,206 | 39,380   | 1,693,923  | 135,631     |

Window: 2026-09-01T21:45:00 .. 2026-09-01T22:10:00 (given).
Turns observed span 2026-09-01T21:48:25 .. 2026-09-01T21:56:32.
```

That window covers reading both files at the pin, judging all 22 findings of the
matched pair against them, and drafting both observations; it is one window for
two files and is counted once. Upper bound, as always: the session was also
assembling an edition in the same minutes. Against the pair's 50,044 model
tokens, harness input+output was 1.2x before cache reads and 35x with them, and
that is the cheap half of verification: the oxbox session's 12.4M cache-read
tokens above bought one finding's reproduction and its fix.
