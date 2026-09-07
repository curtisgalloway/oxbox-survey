<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-06
venue: openrouter
model: deepseek/deepseek-v4-flash
kind: hygiene
source: oxbox-run
agent: claude-fable-5-1
corpus: oxbox-secret-scanner-fix
role: candidate
run: 2026-09-06T23-19-44Z
wall_s: 986
applies: false
hits: 8
hits_of: 8
self_hits: 0
usd_model: 0.0024
usd_total: 0.0024
---

# DeepSeek V4 Flash as a candidate on the scanner fix: corrupt hunk header again, eight of eight verdicts behind it, sixteen minutes, back on its first provider

**What happened** — `oxbox-secret-scanner-fix` (`ox` at `6072d56`, 39,467 B, `--mode diff`) put to `deepseek/deepseek-v4-flash` as a candidate. The patch does not apply without `--recount`; behind that gate all eight verdicts hold, zero self-hits, nothing outside the pattern list changed, and the model added a ninth pattern rather than rewriting one. Gate 1 is the gate: quality 0, the same failure as its baseline run and as GLM-5.3 Flash's candidate run. 986 seconds, $0.0024 billed, provider DigitalOcean, where its first run on 2026-09-02 had gone; three providers have served this model in the record. (Corrected 2026-09-06: this line first said "the fourth provider"; the count was wrong.)

## Evidence

`corpora/scorers/secret_scanner_fix.py`: gate 1 FAIL (applies only with `--recount`), gate 2 8 of 8, gate 3 PASS, patterns 8 before, 9 after, RESULT FAIL. `status.json`: `finish_reason` stop, prompt 10,021, completion 10,406, reasoning 9,365, `venue_cost` 0.0024286.

## So what

n=2 on this fixture for this model, both runs failing the apply gate on the hunk header with the regex work right behind it. That is the same shape as GLM-5.3 Flash's two runs, one pass and one fail, except DeepSeek has not passed yet. The mechanical half of a diff is where the cheap paid tier is losing this fixture, and a reader using either route for `--mode diff` should plan on `--recount`.

Verification here is the scorer, so `usd_total` equals `usd_model`; the fixture has no ceiling, so no cost digit.
