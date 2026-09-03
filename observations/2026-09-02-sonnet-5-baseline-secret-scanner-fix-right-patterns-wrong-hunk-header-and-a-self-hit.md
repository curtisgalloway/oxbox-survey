<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-02
venue: openrouter
model: anthropic/claude-sonnet-5
kind: hygiene
source: oxbox-run
agent: claude-fable-5-1
corpus: oxbox-secret-scanner-fix
role: baseline
---

# Sonnet 5 baseline on the scanner fix: all eight verdicts right, hunk header wrong, and the patched scanner refuses ox's own source

**What happened** — the first baseline run of the corpus. `anthropic/claude-sonnet-5`
was given `oxbox-secret-scanner-fix` byte-identical to the fixture (39,467 B, `ox` at
`6072d56`), `--mode diff`, effort high, temperature 0.2. The patch it produced is
the right change to the right line and clears all eight sample verdicts — and it
fails two of the three mechanical gates: `git apply --check` rejects it as a corrupt
patch, and the new pattern fires on `max_tokens = DEFAULT_MAX_TOKENS` in `ox`
itself, which is the exact failure the prompt says a fix must not introduce.

## Evidence

Run `logs/2026-09-03T02-24-15Z`, `context_bytes` 39467, `finish_reason` stop,
`ox_version` 0.5.0. Scored with `corpora/scorers/secret_scanner_fix.py`:

```
gate 1  APPLY   FAIL  git apply --check:
                      error: corrupt patch at line 14
        (with --recount: applies -- gate 2 below is informational)

gate 2  SCAN
        sample                                                         before required  after
        api_key = "abcdefghijklmnop"                                   hit    hit       hit
        client_secret=abcdefghijklmnopqrst                             miss   hit       hit
        my_api_key = "abcdefghijklmnopqrst"                            miss   hit       hit
        DB_PASSWORD=hunter2hunter2hunter2                              miss   hit       hit
        token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9                    miss   hit       hit
        aws_secret_access_key=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY miss   hit       hit
        "max_tokens": 100000                                           miss   miss      miss
        completion_tokens = 512                                        miss   miss      miss
        8 of 8 verdicts hold

gate 3  SELF    FAIL  the patched scanner refuses ox's own source:
                      ox@6072d56:734: 'max_tokens = DEFAULT_MAX_TOKENS' (hardcoded credential assignment)
                      ox(patched):735: 'max_tokens = DEFAULT_MAX_TOKENS' (hardcoded credential assignment)

scope   in contract: nothing outside SECRET_PATTERNS changed
patterns: 8 before, 8 after

RESULT  FAIL  (gate 1: applies only with --recount; gate 3: 2 self-hit(s))
```

The hunk header is `@@ -84,8 +84,10 @@` over a hunk that actually holds 7 old and
8 new lines, at a list that sits at lines 69–79 of the pin; git tolerates the
offset and rejects the counts. The replacement pattern:

```
(?i)\b[A-Za-z0-9_]*(?:api[_\-]?key|secret|password|token)[A-Za-z0-9_]*\b
\s*[:=]\s*(?:"[^"\s]{16,}"|'[^'\s]{16,}'|[A-Za-z0-9_\-./+=]{16,})
```

`max_tokens` matches the identifier half, and `DEFAULT_MAX_TOKENS` is eighteen
unquoted identifier characters, so the value half matches too. The two trap rows
in the prompt carry three- and six-character values and cannot represent that
case, which is why gate 3 now exists: it is the prompt's own requirement ("a
scanner that fires on them refuses every run") measured over the whole file. It
was added before any evidence was recorded against this task, and the reference
fix `6ba47d8` and the pin both score zero hits under it.

Completion was 15,479 tokens, of which 14,757 were reasoning; the visible answer
is a ten-line explanation and a 13-line diff.

## So what

The thing the survey has been scoring free models on — "does the patch apply" —
fails here for a model nobody would call weak, on a hunk-header miscount, the
same defect class as the `--recount` observations in earlier editions. That is a
useful calibration: a strict gate 1 is a hygiene measurement, not a competence
one, and the observation should say which it was. The self-hit is the more
interesting failure. It is a real regression that the eight-row table could not
see, and it argues that the mechanical fixtures need to measure the stated
requirement directly rather than through samples whenever the requirement is
"does not fire on this file".

No marker: this is a baseline, not a candidate.

## Cost

### Under test

| run | model | mode | context | prompt | completion | reasoning | usd |
|---|---|---|---|---|---|---|---|
| `2026-09-03T02-24-15Z` | `anthropic/claude-sonnet-5` | diff | 39,467 B | 14,847 | 15,479 | 14,757 | $0.1845 |

usd is computed from the archived catalog price (2026-09-01.json), not billed: OpenRouter returns the billed figure only when asked, and ox does not ask. Reasoning tokens are inside completion and priced as output.

### Harness

| model | lane | turns | input | output | thinking | cache read | cache write |
|---|---|---|---|---|---|---|---|
| `claude-fable-5-1` | main | 16 | 3,638 | 37,379 | 12,965 | 2,492,296 | 60,532 |
| **total** | | 16 | 3,638 | 37,379 | 12,965 | 2,492,296 | 60,532 |

Window: 2026-09-03T02:24:00 .. 2026-09-03T02:36:00 (given).
Turns observed span 2026-09-03T02:24:03 .. 2026-09-03T02:32:39.

**Upper bound.** Anything else the session did in this window is counted here too.

Harness input+output is 1.4x the model's prompt+completion (41,017 vs 30,326); with cache reads it is 83.5x (2,533,313).

The harness window covers all three Sonnet runs and their verification, plus the scorer being written; it is shared by the three 2026-09-02 Sonnet observations and is an upper bound for each.
