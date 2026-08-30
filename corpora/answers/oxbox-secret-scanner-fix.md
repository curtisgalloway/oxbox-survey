<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

# Answer key — `oxbox-secret-scanner-fix`

Task: `corpora/prompts/oxbox-secret-scanner-fix.txt`, mode `diff`, `ox` at
oxbox `6072d56830dd3f80d567bf8c71593bcab95fbc74`.

## Acceptance

Two gates, both mechanical. A candidate patch passes only if it clears both.

**1. It applies.** `git apply --check` against the pin, using the exact path `ox`
that the prompt supplied. Wrong path, missing context lines, or a fabricated hunk
header all fail here without anyone reading the diff.

**2. The scan changes behaviour in exactly this way.** Extract `SECRET_PATTERNS`
from the patched file and match it against the eight samples below. All eight
verdicts must hold; six of them already hold before the patch and are there to
catch a fix that overshoots.

| Sample | Before (`6072d56`) | Required after |
|---|---|---|
| `api_key = "abcdefghijklmnop"` | hit | hit |
| `client_secret=abcdefghijklmnopqrst` | **miss** | **hit** |
| `my_api_key = "abcdefghijklmnopqrst"` | **miss** | **hit** |
| `DB_PASSWORD=hunter2hunter2hunter2` | **miss** | **hit** |
| `token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9` | **miss** | **hit** |
| `aws_secret_access_key=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY` | **miss** | **hit** |
| `"max_tokens": 100000` | miss | miss |
| `completion_tokens = 512` | miss | miss |

The before column is measured, not quoted from a commit message: the table was
produced by exec-ing the `SECRET_PATTERNS` literal out of `git show 6072d56:ox`
and again out of the reference fix, and matching each sample with `re.search`.

The last two rows are the trap. `ox` is routinely asked to read its own source,
which is full of `max_tokens` and `completion_tokens`, and a pattern that fires
on those makes the tool refuse every run. A patch that catches the five misses by
matching `token` unconditionally has made the tool worse, and only these rows say
so.

## Reference

oxbox `6ba47d85f64eff108343f068e5638fb92b097a74`, "ox: the scanner missed
client_secret, and every unquoted credential". It is **a** solution, not **the**
solution — score a candidate on the table, never on similarity to this diff.

Its two mechanisms, for a reviewer's orientation: `\b` does not bound an
identifier, because `_` is a word character, so `\bsecret\b` never matches inside
`client_secret`; and the old pattern required the value to be quoted, which `.env`
files and shell exports never are. The reference keeps `max_tokens` clean with a
`token(?!s)` lookahead.

Note that the reference commit also carried four unrelated robustness fixes. Only
the `SECRET_PATTERNS` change is in scope for this task, and a candidate patch that
touches the rest is out of contract — the prompt says to change the pattern list
only.
