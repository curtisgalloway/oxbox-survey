<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-08
venue: openrouter
model: cohere/north-mini-code:free
kind: findings
source: oxbox-run
agent: claude-fable-5-1
corpus: oxbox-clean-control
role: candidate
run: 2026-09-08T00-57-37Z
wall_s: 900
timed_out: true
findings: 0
real: 0
---

# North Mini Code free as a candidate on the zero-defect control: nothing in 900 seconds, the second timeout on the fixture in an hour

**What happened** — `oxbox-clean-control`, the zero-defect control
(`jailtest.py` at `6302b12`, 6,096 B, review mode, effort high, 100,000
tokens, temperature 0.2), put to `cohere/north-mini-code:free`. Run as a
candidate in the try-next batch the editor approved in round 8 of the rating
review (2026-09-07). No response: oxbox's 900-second read timeout closed the
connection, so there is no answer, no `route`, no token count and no bill.
The same model answered ask-grounding in 25 seconds and the scanner fix in
243 seconds within the previous ten minutes, both on the Cohere route. This
is the second zero-defect control run of the batch to time out, three
minutes after gpt-oss-120b's, on a 6 KB payload that three other models in
the same batch answered in under four minutes.

## Evidence

Log `logs/2026-09-08T00-57-37Z`: `request.json` and `meta.json` only, no
`response.json`; `status.json` `ok` false, `error` "oxbox-send: timed out
after 900s reading the response (global)", `route` null.

## So what

Two timeouts on the same fixture inside four minutes, from two vendors, on
requests sent while the venue was answering the same payload for others,
is either two models that reason without end on a clean file or a window
when their routes stalled; the record cannot tell without a pinned re-send.
A timed-out run is a run: speed 0, nothing to score on quality or cost. The
free route has no price to guard, so a re-send costs only the wait.

## Cost

No response, so no model bill is recorded and `usd_model` is left unset. No
checking half.
