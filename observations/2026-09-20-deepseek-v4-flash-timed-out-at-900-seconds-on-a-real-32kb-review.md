<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-20
venue: openrouter
model: deepseek/deepseek-v4-flash
kind: availability
source: oxbox-run
agent: claude-opus-5
role: candidate
run: 2026-09-11T00-38-22Z
wall_s: 900
answered: false
timed_out: true
---

# deepseek-v4-flash timed out at 900 seconds on a real 32 KB review, the one time failover was tried

**What happened** — the only run in the ten-day window that got past the
`max_price` guard, and it did not finish either. With `--failover`, entry 1
refused with the 404 and oxbox moved to entry 2, which held the connection for
the full read timeout and returned nothing. Recorded 2026-09-20 from the log
directory; it was never written up at the time.
[[2026-09-20-twelve-genuine-work-review-attempts-in-ten-days-and-not-one-reached-a-model]]

## Evidence

`status.json` from the run, which records both legs:

```
oxbox-send: no manifest entry produced an answer:
  [1] openrouter/z-ai/glm-5.3-flash: oxbox-send: HTTP 404: {"error":{"message":
      "No endpoints found that satisfy the max price for this request", ...
      "failed_routing_step":"Filter by Max Price"}}
  [2] openrouter/deepseek/deepseek-v4-flash: oxbox-send: timed out after 900s
      reading the response (global)
```

`finish_reason`, `prompt_tokens`, `completion_tokens`, `venue_cost` and
`route` are all null — nothing came back to measure. The target was four files
of `curtisgalloway/shoephone`, 32,204 bytes, in `review` mode. Wall clock from
the log directory's own timestamps is 15 minutes, which is the read timeout
exactly.

## So what

**Every timeout in this record until now was a fixture timeout.** gpt-oss-120b,
North Mini Code twice, qwen3.8-27b on argenta — all of them on the zero-defect
control, all on free or local models. This is the first recorded instance of a
**paid manifest entry** timing out, and it happened on real work rather than on
a fixture.

That matters for what the manifest promises. Entry 2 exists so that a refusal
from entry 1 has somewhere to go; the 2026-09-19 observation noted that
`--failover` "moved them to entry 2, which routed" and treated that as the
working escape hatch. On this earlier run, with a real 32 KB payload, it was
not one. So during the ten days the pin was broken, a caller who followed the
advice to pass `--failover` still got nothing — the first entry could not be
reached and the second did not answer in fifteen minutes.

**One run is not a rate.** This says the entry timed out once on a 32 KB
review; it does not say how often, and the 2026-09-20 ask-grounding run through
the same model answered a 39 KB prompt in 26 seconds. The difference worth
testing is `review` mode against a real multi-file diff versus `ask` mode
against a single file, which is a much longer generation. No disqualifier is
recorded: the model has answered since, on the re-pinned route, and a single
timeout nine days ago is not a standing access fact.

## Cost

$0 — nothing was billed, because nothing was returned. `venue_cost` is null.
No checking window: the verdict is two fields of `status.json`.
