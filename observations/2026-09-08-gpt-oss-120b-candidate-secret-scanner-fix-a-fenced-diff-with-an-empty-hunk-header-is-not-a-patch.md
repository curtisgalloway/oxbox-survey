<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-08
venue: openrouter
model: openai/gpt-oss-120b
kind: hygiene
source: oxbox-run
agent: claude-fable-5-1
corpus: oxbox-secret-scanner-fix
role: candidate
run: 2026-09-08T00-52-03Z
wall_s: 136
applies: false
hits: 0
hits_of: 8
self_hits: 0
usd_model: 0.0026
usd_total: 0.0026
---

# gpt-oss-120b as a candidate on the scanner fix: a fenced diff with an empty hunk header is not a patch

**What happened** — `oxbox-secret-scanner-fix` (`ox` at `6072d56`, 39,467 B, `--mode diff`, effort high, 100,000 tokens, temperature 0.2) put to `openai/gpt-oss-120b`. Run as a candidate in the try-next batch the editor approved in round 8 of the rating review (2026-09-07), seven models on the three fixtures, unpinned. The answer is a
paragraph of prose, then a ` ```diff ` fence holding a hunk whose header is a
bare `@@` with no line numbers, then a closing fence. `git apply --check`
rejects it outright ("No valid patches in input"), with or without
`--recount`, so gate 1 fails in a different way from the other four models
this fixture has failed: theirs miscounted the header, this one did not
write it. The regex inside the fence would have been worth scoring (it
generalizes the credential pattern to prefixed names and unquoted values and
adds an AWS key pattern), but gate 2 never runs on a document that is not a
patch, so nothing held: 0 of 8 measured. 13,581 completion tokens, 14,043 of
them reasoning by the accounting, 136 seconds, $0.0026 billed, route
CoreWeave.

## Evidence

`corpora/scorers/secret_scanner_fix.py`: gate 1 FAIL, `error: No valid
patches in input`, still fails with `--recount`; gates 2 and 3 not reached;
RESULT FAIL. The answer's hunk header, verbatim: `@@`. `status.json`:
`finish_reason` stop, prompt 9,634, completion 13,581, `route` CoreWeave,
`venue_cost` 0.0026.

## So what

`--mode diff` asks for a unified diff and nothing else; this model wrapped
one in Markdown and left the header empty, which no `--recount` can repair.
The ask-grounding run three minutes earlier was flawless, so this is a
format-contract failure, not a reading failure, and it is the kind a harness
could catch before the patch reaches `git apply`.

## Cost

Scorer-verified, so `usd_total` equals `usd_model`; the fixture has no
ceiling, so no cost score. Quality 0 because gate 1 is the gate.
