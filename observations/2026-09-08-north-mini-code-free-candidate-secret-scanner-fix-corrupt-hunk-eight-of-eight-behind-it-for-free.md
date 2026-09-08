<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-08
venue: openrouter
model: cohere/north-mini-code:free
kind: hygiene
source: oxbox-run
agent: claude-fable-5-1
corpus: oxbox-secret-scanner-fix
role: candidate
run: 2026-09-08T00-51-29Z
wall_s: 243
applies: false
hits: 8
hits_of: 8
self_hits: 0
usd_model: 0
usd_total: 0
---

# North Mini Code free as a candidate on the scanner fix: corrupt hunk header, eight of eight behind it, for free

**What happened** — `oxbox-secret-scanner-fix` (`ox` at `6072d56`, 39,467 B, `--mode diff`, effort high, 100,000 tokens, temperature 0.2) put to `cohere/north-mini-code:free`. Run as a candidate in the try-next batch the editor approved in round 8 of the rating review (2026-09-07), seven models on the three fixtures, unpinned. The patch
does not apply without `--recount`; behind that gate all eight verdicts hold,
zero self-hits, nothing outside the pattern list changed, eight patterns
rewritten in place. 9,980 completion tokens, 9,451 reasoning, 243 seconds,
route Cohere, $0 billed. The first free model on this fixture, and it lands
exactly where the paid tier does: right regex, wrong header.

## Evidence

`corpora/scorers/secret_scanner_fix.py`: gate 1 FAIL (applies only with
`--recount`), gate 2 8 of 8, gate 3 PASS, patterns 8 before, 8 after, RESULT
FAIL. `status.json`: `finish_reason` stop, prompt 9,452, completion 9,980,
reasoning 9,451, `route` Cohere, `venue_cost` 0.

## So what

Six models have now written a working pattern list and a hunk header `git
apply` rejects; only the paid frontier baselines and Gemini Flash have
cleared gate 1 as written. The gate is the fixture's point, and it stands,
but a reader who runs `--mode diff` on any of these should expect to
`--recount`.

## Cost

Free, scorer-verified, so `usd_total` equals `usd_model`; the fixture has no
ceiling, so no cost score. Quality 0 because gate 1 is the gate.
