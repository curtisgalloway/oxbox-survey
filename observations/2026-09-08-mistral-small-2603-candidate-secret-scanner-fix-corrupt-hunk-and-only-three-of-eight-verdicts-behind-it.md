<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-08
venue: openrouter
model: mistralai/mistral-small-2603
kind: hygiene
source: oxbox-run
agent: claude-fable-5-1
corpus: oxbox-secret-scanner-fix
role: candidate
run: 2026-09-08T00-49-12Z
wall_s: 19
applies: false
hits: 3
hits_of: 8
self_hits: 0
usd_model: 0.0035
usd_total: 0.0035
---

# Mistral Small 2603 as a candidate on the scanner fix: corrupt hunk header, and only three of eight verdicts behind it

**What happened** — `oxbox-secret-scanner-fix` (`ox` at `6072d56`, 39,467 B, `--mode diff`, effort high, 100,000 tokens, temperature 0.2) put to `mistralai/mistral-small-2603`. Run as a candidate in the try-next batch the editor approved in round 8 of the rating review (2026-09-07), seven models on the three fixtures, unpinned. The patch does not apply without `--recount`, and behind that gate it is also wrong: 3 of 8 pattern verdicts hold. It missed `client_secret=` and `my_api_key` (the two decoys that catch an under-generalized fix), `DB_PASSWORD=` and the AWS secret key, and it broke the one pattern that had worked, `api_key = "..."`, so the patched scanner catches less than the original. 19 seconds, $0.0035 billed, route Mistral.

## Evidence

`corpora/scorers/secret_scanner_fix.py`: gate 1 FAIL (applies only with `--recount`), gate 2 3 of 8, gate 3 PASS, patterns 8 before, 8 after, RESULT FAIL. `status.json`: `finish_reason` stop, prompt 9,930, completion 3,429, reasoning 2,814, `route` Mistral, `venue_cost` 0.0035.

## So what

The fastest scanner-fix run in the record and the worst-scoring patch behind the apply gate: a rewrite that regressed the existing pattern. Nemotron and MiMo failed the same gate the same minute with 8 of 8 behind it, so the hunk header is the tier's shared failure and the regex work is what separates them.

Verification here is the scorer, so `usd_total` equals `usd_model`; the fixture has no ceiling, so no cost score. Quality 0 because gate 1 is the gate.
