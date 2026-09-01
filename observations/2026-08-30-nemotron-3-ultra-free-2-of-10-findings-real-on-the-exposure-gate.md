<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-08-30
venue: opencode
model: nemotron-3-ultra-free
kind: findings
source: oxbox-run
agent: claude-fable-5-1
---

# Nemotron 3 Ultra free: 2 of 10 findings real on the exposure gate, and the one that mattered was filed as UNCERTAIN

**What happened** — the first `--mode review` run of `nemotron-3-ultra-free`, on
the two exposure-gate scripts of oxbox at `6072d56`, with a payload byte-identical
to a MiniMax M3 run three minutes earlier
([[2026-08-30-minimax-m3-free-7-of-12-with-a-framed-prompt-on-the-same-files]]).
Ten findings; two hold up against the source as sent. Its headline "critical"
finding describes a code path that does not exist, and the genuinely critical
defect in the file is its finding 8, labelled UNCERTAIN and "low but non-zero",
with a mitigation argument that is wrong. Verified 2026-09-01 against the payload
in `request.json`.

## The run

| Log dir | Venue / model | Files | Prompt | Completion | Reasoning | Finish | Wall |
|---|---|---|---|---|---|---|---|
| `2026-08-30T22-29-19Z` | opencode / `nemotron-3-ultra-free` | `.claude/skills/ox-review/scripts/exposure.py`, `.claude/skills/ox-review/scripts/preflight.py` | 7,262 | 4,872 | 2,961 | stop | 128.8 s |

`ox_version` 0.3.0, explicit `--venue opencode --model nemotron-3-ultra-free` (no
manifest), `truncated: false`. The response carries no `provider` field, so which
upstream served it is unknown.

**Payload.** System prompt and user message are identical to
`2026-08-30T22-26-09Z` (sha256 of the concatenated messages begins `799b7270`).
The two files match `git show 6072d56:<path>` byte for byte, 15,329 + 11,917 =
27,246 bytes, which is the `oxbox-exposure-gate` pin. The task text is **not** the
fixture's prompt: it is 748 characters longer and frames the files as a security
gate where "a false 'public' is the worst possible failure and a false
'not-public' is merely annoying". So this run is matched to the MiniMax run and
not to the fixture, and carries no `corpus:` field. Registering that task text as
a second fixture would make both runs citable; it has not been done here because
the corpus rules ask for a dry-run byte check first.

## Findings, verified against the payload

| # | Finding | Verdict |
|---|---|---|
| 1 | scp-style regex rejects single-label hosts (`git@myhost:owner/repo`), so they read `not-public` | **real, minor, fails safe.** The example it gives, `git@git.internal:team/project`, has a dot in the host and parses fine |
| 2 | clone probe hard-codes `https://` whatever the remote's scheme | true, and by design: an http-only host gets `unknown`, the gate's designed answer for "cannot tell". **Not a defect.** Its aside about a redirect serving a real advertisement gestures at finding 8 without naming the mechanism |
| 3 | **"critical"**: API says private (or is unreachable) but the anonymous clone succeeds, so the verdict becomes `public` "with no warning" | **false positive.** When the API is reachable and says private, `assess_remote` returns `not-public` at the first branch and the clone result is never consulted. When the API is unavailable, the `public` verdict carries the note "provider API unavailable; verdict rests on the anonymous clone probe". And a host that really served an anonymous ref advertisement really is publicly clonable, which is the gate's definition of public |
| 4 | `git://` accepted by `parse_remote` but probed over https | true, fails safe (`unknown`). Not a defect |
| 5 | content-type substring match "could match unrelated types" | speculative: the check is OR'd with a body-prefix check, and a server that wanted to look public would serve a real advertisement. Not a defect |
| 6 | **preflight's "one correctness defect"**: `ask_ox_where` passes the prompt positionally; "if `ox` expects stdin or `--prompt`, the command fails" | **false positive.** `ox` takes the task as a positional argument (the first example in its README). The model had no access to `ox` and guessed against the calling code instead of labelling UNCERTAIN |
| 7 | `issue_date` sorted as a string; breaks on `2026-1-15` | speculative: the manifest format fixes `issue_date` as `YYYY-MM-DD`. Not a defect |
| 8 | UNCERTAIN: `urlopen` follows redirects, so a host could redirect to a controlled server that serves an advertisement, and the probe reports `public` | **real, and the most serious defect in the file.** Fixed in oxbox `d2f2e44` eighteen minutes after this run, with an end-to-end reproduction. The model's mitigation — that the `001e# service=git-upload-pack` check "is hard to forge without serving actual git refs" — is wrong: the redirect target can be any public repository's genuine advertisement, which is exactly what the reproduction used |
| 9 | UNCERTAIN: IPv6 literal in an scp-style URL is not matched | true, negligible, fails safe |
| 10 | LOW: "no timeout on `git` subprocess calls" | **false positive, and self-contradicting:** the body says "`timeout=30` on `git rev-parse` etc.", which is the timeout the title says is missing (`exposure.py` line 59) |

Two real (1, 8). Three true but not defects, all failing safe (2, 4, 9). Two
speculative (5, 7). Three false positives (3, 6, 10).

## Calibration, which is the finding

Both models found the redirect. MiniMax M3 put it first and called it the only
finding that produces the worst-case outcome. Nemotron put it eighth, under
"Uncertain / Low Severity", and led with a "critical" finding that two lines of
the code refute. A reviewer triaging by the model's own severity labels would have
fixed nothing that mattered.

Its output hygiene is the cleanest in the survey so far: every finding carries
file, line, defect and scenario exactly as the system prompt asked, in 4,872
completion tokens against MiniMax's 30,712 on the same payload. That is the wrong
axis to be good on when the ranking underneath is inverted.

## So what

One run, two files, one repository: a data point, not a verdict. What it argues
is that `nemotron-3-ultra-free` is cheap, fast, well-formatted and reachable, and
that on this payload its severity labels were anti-correlated with reality. Run it
again on a different fixture before ranking it, and do not read its UNCERTAIN as
"probably not real".

## Cost

Both halves, from `costcheck.py`. The model's tokens are this run's. The harness
window is the oxbox session (`claude-opus-5`) that assembled both batches of the
matched pair, verified the redirect finding against a local server and committed
the fix; it is shared with the MiniMax observation and counted once.

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
verification of all ten findings above was done on 2026-09-01 in a survey session;
its window is reported below.

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
