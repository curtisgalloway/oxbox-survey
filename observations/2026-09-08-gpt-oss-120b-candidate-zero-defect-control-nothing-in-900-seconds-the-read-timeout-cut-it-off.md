<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-08
venue: openrouter
model: openai/gpt-oss-120b
kind: findings
source: oxbox-run
agent: claude-fable-5-1
corpus: oxbox-clean-control
role: candidate
run: 2026-09-08T00-54-24Z
wall_s: 900
timed_out: true
findings: 0
real: 0
---

# gpt-oss-120b as a candidate on the zero-defect control: nothing in 900 seconds, the read timeout cut it off

**What happened** — `oxbox-clean-control`, the zero-defect control
(`jailtest.py` at `6302b12`, 6,096 B, review mode, effort high, 100,000
tokens, temperature 0.2), put to `openai/gpt-oss-120b`. Run as a candidate in
the try-next batch the editor approved in round 8 of the rating review
(2026-09-07). No response arrived: oxbox's read timeout closed the connection
after 900 seconds ("timed out after 900s reading the response (global)"), so
there is no answer, no `route`, no token count and no bill in the record.
Whether the venue billed a generation that never returned is not visible
from here. The same model answered ask-grounding in 179 seconds forty
minutes earlier and the scanner fix in 136, both with several thousand
reasoning tokens, so this is not a model that cannot answer; it is one
request, on one route the record cannot name, that did not.

## Evidence

Log `logs/2026-09-08T00-54-24Z`: `request.json` and `meta.json` only, no
`response.json`; `status.json` `ok` false, `error` "oxbox-send: timed out
after 900s reading the response (global)", `route` null.

## So what

A timed-out run is a run: speed 0 by the rubric, nothing to score on quality
or cost. It joins DeepSeek's 33-minute StreamLake blowout as a case the pin
would have explained and the unpinned request cannot. If the editor wants
the row filled, the same payload can be re-sent, pinned to the route the
model's other two runs took (DeepInfra and CoreWeave), which is how the
DeepSeek case was settled.

## Cost

No response, so no model bill is recorded and `usd_model` is left unset
rather than typed as zero. No checking half.
