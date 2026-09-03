<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-02
venue: openrouter
model: deepseek/deepseek-v4-flash
kind: hygiene
source: oxbox-run
agent: claude-fable-5-1
corpus: oxbox-secret-scanner-fix
role: baseline
---

# DeepSeek V4 Flash baseline on the scanner fix: corrupt hunk header, 7 of 8 verdicts, and 21 minutes for 5,000 tokens

**What happened** — `oxbox-secret-scanner-fix` (39,467 B, `ox` at `6072d56`, `--mode
diff`) put to `deepseek/deepseek-v4-flash`, the cheapest of the five baselines at
$0.07 in and $0.14 out per million. It fails two gates: the patch is rejected by
`git apply --check` on a hunk-count error, and after `--recount` the new pattern
still misses `aws_secret_access_key=...`, the one sample whose keyword is followed
by more identifier. Zero self-hits. The request took 21 minutes 29 seconds wall
clock for 5,097 completion tokens, the slowest run of the evening by a factor of
two against a payload identical to the others.

## Evidence

Run `logs/2026-09-03T02-43-57Z`, `context_bytes` 39467, `finish_reason` stop,
`truncated` false. `corpora/scorers/secret_scanner_fix.py`:

```
gate 1  APPLY   FAIL  git apply --check:
                      error: corrupt patch at line 11
        (with --recount: applies -- gate 2 below is informational)
gate 2  SCAN    7 of 8 verdicts hold
        aws_secret_access_key=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY  miss  hit  miss  <-- WRONG
gate 3  SELF    PASS  zero hits over ox at the pin and as patched
scope   in contract: nothing outside SECRET_PATTERNS changed
RESULT  FAIL  (gate 1: applies only with --recount; gate 2: 1 of 8 verdicts wrong)
```

The pattern:

```
(?i)(?<![A-Za-z0-9])(api[_\-]?key|secret|password|token)\b\s*[:=]\s*
(?:["']([^"'\s]{16,})["']|[A-Za-z0-9_\-/+=]{16,})
```

The explanation diagnoses the `\b`-before-the-keyword problem correctly and
replaces it with a lookbehind that admits an underscore prefix, which is why
`my_api_key` and `DB_PASSWORD` now hit. It leaves the `\b` *after* the keyword
in place, and `_` is a word character, so `secret\b` cannot match inside
`aws_secret_access_key` — the same fact the answer key's reference section
names as the first of the two mechanisms. The header `@@ -65,7 +65,7 @@` sits
over a hunk of six old lines and six new; git rejects the count, not the
offset, so this is the Sonnet failure again.

Timing, from the runner's log: started 02:43:56Z, exited 03:05:25Z. Prompt
10,021 tokens, completion 5,097 of which 4,491 reasoning. The three prior
baselines on this payload finished in 35 seconds to 6 minutes 45 seconds. No
error, no retry, no truncation; the endpoint simply took that long.

## So what

At this price the run computed to $0.0014 — the cost story is not dollars but
minutes, and a review pipeline that serialises requests (as the ox-review skill
does) would have spent its whole budget of patience on one call. That is an
availability observation as much as a hygiene one, and it should be re-measured
before it is believed: one run, one hour, one route.

On the fixture itself: the cheap open-weight tier's first result lands between
Sonnet and the two clean passes — right diagnosis, incomplete fix, wrong
header. The measured bar remains a clean apply and 8 of 8.

No marker: this is a baseline, not a candidate.

## Cost

### Under test

| run | model | mode | context | prompt | completion | reasoning | usd |
|---|---|---|---|---|---|---|---|
| `2026-09-03T02-43-57Z` | `deepseek/deepseek-v4-flash` | diff | 39,467 B | 10,021 | 5,097 | 4,491 | $0.0014 |

usd is computed from the archived catalog price (2026-09-01.json), not billed: OpenRouter returns the billed figure only when asked, and ox does not ask. Reasoning tokens are inside completion and priced as output.

### Harness

| model | lane | turns | input | output | thinking | cache read | cache write |
|---|---|---|---|---|---|---|---|
| `claude-fable-5-1` | main | 3 | 204 | 3,978 | 846 | 854,867 | 4,300 |
| **total** | | 3 | 204 | 3,978 | 846 | 854,867 | 4,300 |

Window: 2026-09-03T03:22:00 .. 2026-09-03T03:45:00 (given).
Turns observed span 2026-09-03T03:22:33 .. 2026-09-03T03:23:02.

**Upper bound.** Anything else the session did in this window is counted here too.

Harness input+output is 0.3x the model's prompt+completion (4,182 vs 15,118); with cache reads it is 56.8x (859,049).

The harness window covers the verification and write-up of the DeepSeek and GLM runs (the runs themselves happened while the session was doing other work and are not in it); it is shared by the 2026-09-02 DeepSeek and GLM observations and is an upper bound for each.
