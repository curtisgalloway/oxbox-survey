<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-06
venue: openrouter
model: "-"
kind: efficiency
source: manual
agent: claude-fable-5-1
checkers: claude-opus-5
run: 2026-09-06T21-22-57Z
harness_model: claude-opus-5
harness_venue: openrouter
harness_window: 2026-09-07T00:08Z..2026-09-07T00:11Z
harness_seconds: 142
harness_in: 17400
harness_out: 11173
harness_usd: 0.366325
harness_note: metered; one `oxbox send --mode ask` request through OpenRouter carrying the same verification instructions and five pinned files the in-harness checker had, log 2026-09-07T00-08-26Z; harness_usd is the venue_cost OpenRouter billed
---

# Opus 5, metered through OpenRouter, checks Fable's clean-control run: one request, 37 cents, and F4 flips from uncertain to refuted

**What happened** — At the editor's direction (round 4, question 3), the
checking half was metered instead of estimated: the same verification task
the in-harness Opus 5 subagent worked on 2026-09-06 (the five findings Fable
5.1 emitted on `oxbox-clean-control`, run `2026-09-06T21-22-57Z`, the same
instructions, the same five files at `6302b12`) was sent to
`anthropic/claude-opus-5` through OpenRouter as a single `--mode ask`
request, so the venue's bill is the checking half. 17,400 prompt tokens,
11,173 completion (9,323 reasoning), finish `stop`, 142 seconds, **$0.3663
billed**. No tools, no cache: one read of the payload, one answer.

Verdicts: F1 REFUTED, F2 CONFIRMED, F3 CONFIRMED, **F4 REFUTED**, F5
CONFIRMED. The in-harness Opus check of the same batch said F4 UNCERTAIN;
metered, with the source in front of it in one piece, it settles the order
of `sensitive_paths()` (`/etc/shadow` appended last) and then refutes on the
ground that an empty home is not "any host where oxbox is normally run", and
that even there the result is a spurious FAIL, a failure in the safe
direction. That is the reading the C3 ruling would give as well, and it is
the reading the record does not follow for F4: the finding stated the host
state, and the same-day reproduction on dev produced the FAIL by pointing
`HOME` at an empty directory. F4 stays real in the record, marked
safe-direction, and this check is on the file as the dissent.

## Evidence

Log `logs/2026-09-07T00-08-26Z`, `venue_cost` 0.366325, `finish_reason`
stop, context 36,731 B, five files. Sent with `--force` because ox's own
secret scanner refused `guardtest.py:240` and `:242`, two fixture strings
shaped like an OpenAI key and an AWS key id; they are test data in a public
file.

| id | metered Opus 5 | in-harness Opus 5 | in-harness Fable 5.1 | recorded |
|---|---|---|---|---|
| F1 | REFUTED | REFUTED | REFUTED | invention |
| F2 | CONFIRMED, Linux only, illustration wrong | CONFIRMED | CONFIRMED | true, negligible |
| F3 | CONFIRMED, diagnostic loss | CONFIRMED | CONFIRMED | true, negligible |
| F4 | REFUTED, safe direction, host state | UNCERTAIN | CONFIRMED | real |
| F5 | CONFIRMED, exit status not silent | CONFIRMED | CONFIRMED | real |

The in-harness Opus check of this run priced at list to a $0.79 floor with
its output tokens unmeasured, over 343 seconds and eight tool calls. The
metered request cost $0.37 and took 142 seconds, and its output is counted.

## So what

Metering removes two caveats at once: the output tokens are on the bill,
and the window is the request, not whatever else the session did. It costs
a design choice, though: the metered checker reads the payload once and
cannot run anything, so it is a reader and never a reproducer. The record's
verdict on F4 rests on a reproduction, and a reader with only the source
would not have it. Under the reproduce-first rule the metered check is the
fallback, and the cost it measures is the cost of the fallback.
