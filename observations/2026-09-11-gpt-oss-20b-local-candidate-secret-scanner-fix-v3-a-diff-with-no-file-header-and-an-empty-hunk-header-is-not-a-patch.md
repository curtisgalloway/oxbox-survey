<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-11
venue: ollama
model: gpt-oss:20b
kind: hygiene
source: oxbox-run
agent: claude-fable-5-1
corpus: oxbox-secret-scanner-fix-v3
role: candidate
run: 2026-09-11T02-27-08Z
wall_s: 46
applies: false
hits: 0
hits_of: 8
usd_model: 0
usd_total: 0
---

# gpt-oss 20B, local, on the secret-scanner fix (unified-diff arm, v3): a diff with no file header and an empty hunk header is not a patch

**What happened** — `oxbox-secret-scanner-fix-v3` (`ox` at `6072d56`,
39,467 B, `--mode diff`, effort medium, 16,000 tokens, temperature 1.0) put
to `gpt-oss:20b` through its `gpt-oss:20b-64k` tag served by ollama 0.34.0
on argenta, through the local setup described in
`2026-09-10-qwen3.8-27b-local-candidate-zero-defect-control-nothing-in-900-seconds-on-argenta.md`.
Forty-six seconds, 2,397 completion tokens, a two-sentence explanation and
a fenced diff that begins with a bare `@@` line and carries no `---`/`+++`
file header. `git apply` reports "No valid patches in input" and
`--recount` cannot help, because there is nothing to recount. The whole
`SECRET_PATTERNS` list is removed and re-emitted with one pattern changed
and comments added, so the pattern content is not scoreable either.
Its hosted sibling `openai/gpt-oss-120b` produced "a fenced diff with an
empty hunk header" on the same task on 2026-09-08, and this model's v1 run
on the task looped to the cap with nothing.

## Evidence

Log `logs/2026-09-11T02-27-08Z`, `context_bytes` 39467, `finish_reason`
stop. The scorer:

```
gate 1  APPLY   FAIL  git apply --check:
                      error: No valid patches in input (allow with "--allow-empty")
        (with --recount: still fails)
RESULT  FAIL  (gate 1)
```

## So what

The prior-art review's claim about this format, that a small model cannot
produce the headers a unified diff needs, at its most complete: not a wrong
count but no header at all, from the same family that emitted an empty one
hosted. Thirty seconds later the same model on the search/replace arm
delivered a block the scorer applied verbatim
(`2026-09-11-gpt-oss-20b-local-candidate-secret-scanner-fix-sr-one-block-applied-verbatim-seven-of-eight-in-36-seconds.md`).

## Cost

Nothing billed; mechanically scored, so `usd_total` equals `usd_model`.
