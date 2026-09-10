<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-10
venue: openrouter
model: "-"
kind: efficiency
source: manual
agent: claude-fable-5-1
checkers: claude-opus-5
run: 2026-09-10T19-37-02Z
harness_model: claude-opus-5
harness_venue: openrouter
harness_window: 2026-09-10T19:45Z..2026-09-10T19:46Z
harness_seconds: 52
harness_in: 16664
harness_out: 3714
harness_usd: 0.17617
harness_note: metered; one `oxbox send --mode ask --force` request through OpenRouter with the verifier contract (amended 2026-09-06) and the five pinned files at 6302b12, log 2026-09-10T19-45-12Z; harness_usd is the venue_cost OpenRouter billed
---

# Opus 5, metered, checks Gemini 3.1 Pro's zero-defect control run: both refuted, 18 cents, 52 seconds

**What happened** — The Opus 5 half of the metered pair on Gemini 3.1 Pro's
baseline clean-control run (`2026-09-10T19-37-02Z`, two findings): the
verifier contract, the two findings as a JSON batch, and the five pinned
files, one `--mode ask` request through OpenRouter. 16,664 prompt tokens,
3,714 completion (3,012 reasoning), 52 seconds, $0.1762 billed.

GPRO1 REFUTED: on macOS the only read grant is `file-read*`, which includes
metadata, so a leaked directory stats fine and `listdir` runs; on Linux the
home is never bound and the path is absent. GPRO2 REFUTED: `(deny
network*)` raises `EPERM` and the unshared namespace raises `ENETUNREACH`,
and no packet filter is configured anywhere in the launcher. Fable 5.1's
check of the same batch reached the same two verdicts.

## Evidence

Log `logs/2026-09-10T19-45-12Z`, `venue_cost` 0.17617, `finish_reason` stop,
context 36,731 B, sent with `--force` for the two fixture strings in
`guardtest.py`. Verdicts as returned, in `content.md`.

## So what

The cheapest check of the day, because the batch was two findings, and
still more than the run it checked.
