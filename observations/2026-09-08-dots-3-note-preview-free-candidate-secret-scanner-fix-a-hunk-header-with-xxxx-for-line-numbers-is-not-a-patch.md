<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-08
venue: openrouter
model: dots-studio/dots-3-note-preview:free
kind: hygiene
source: oxbox-run
agent: claude-fable-5-1
corpus: oxbox-secret-scanner-fix
role: candidate
run: 2026-09-08T01-17-05Z
wall_s: 231
applies: false
hits: 0
hits_of: 8
self_hits: 0
usd_model: 0
usd_total: 0
---

# Dots 3 Note Preview free as a candidate on the scanner fix: a hunk header with XXXX for line numbers is not a patch

**What happened** — `oxbox-secret-scanner-fix` (`ox` at `6072d56`, 39,467 B,
`--mode diff`, effort high, 100,000 tokens, temperature 0.2) put to
`dots-studio/dots-3-note-preview:free`. Run as a candidate in the try-next
batch the editor approved in round 8 of the rating review (2026-09-07). The
answer is a paragraph of prose and a ` ```diff ` fence whose hunk header reads
`@@ -XXXX,10 +XXXX,10 @@`: the model wrote placeholders where the line numbers
go. `git apply --check` reports "corrupt patch at line 3", with or without
`--recount`, so gate 1 fails the way gpt-oss-120b's did an hour earlier (a
header that was never written) rather than the way five other models' did (a
header miscounted). Gate 2 never runs on a document that is not a patch: 0 of
8 measured. 22,466 completion tokens, 20,936 reasoning, 231 seconds, route
AtlasCloud, $0 billed.

## Evidence

`corpora/scorers/secret_scanner_fix.py`: gate 1 FAIL, `error: corrupt patch
at line 3`, still fails with `--recount`; gates 2 and 3 not reached; RESULT
FAIL. The header, verbatim: `@@ -XXXX,10 +XXXX,10 @@`. `status.json`:
`finish_reason` stop, prompt 9,631, completion 22,466, reasoning 20,936,
`route` AtlasCloud, `venue_cost` 0.

## So what

Two failure shapes on this fixture are now distinct in the record: a header
that miscounts (fixable by `--recount`, six models) and a header that is not
a header (gpt-oss-120b's bare `@@`, this model's `XXXX`), which no flag
repairs. The second is a model declining to do the arithmetic and saying so
in the placeholder, on a fixture whose whole point is the mechanical half of
a diff.

## Cost

Free, scorer-verified, so `usd_total` equals `usd_model`; the fixture has no
ceiling, so no cost score. Quality 0 because gate 1 is the gate.
