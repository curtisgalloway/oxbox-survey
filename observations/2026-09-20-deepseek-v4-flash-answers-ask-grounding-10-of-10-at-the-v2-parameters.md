<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-20
venue: openrouter
model: deepseek/deepseek-v4-flash
kind: findings
source: oxbox-run
agent: claude-opus-5
corpus: oxbox-ask-grounding-v2
role: candidate
run: 2026-09-20T01-11-49Z
wall_s: 26
hits: 10
hits_of: 10
usd_model: 0.0005
usd_total: 0.0005
---

# deepseek-v4-flash answers ask-grounding 10 of 10 at the v2 parameters, on the re-pinned routes

**What happened** — manifest entry 2, run on the fixture at the mitigated
parameters for the first time, through the pin corrected earlier today. It
routed to StreamLake and scored 10 of 10. Run as the paid comparison for the
new free `-0731` row.
[[2026-09-20-deepseek-v4-flash-0731-free-answers-ask-grounding-10-of-10-against-its-paid-twin]]

## Evidence

```
oxbox-send: venue=openrouter model=deepseek/deepseek-v4-flash mode=ask effort=medium context=39467B files=1
oxbox-send: finish=stop prompt_tokens=9917 completion_tokens=1704 reasoning_chars=5731 route=StreamLake
```

```
RESULT  PASS  (7 scored mechanically correct, 3 for a reader)
```

Adjudicated against `6072d56:ox`: **q2** refuses the redirect and says the
`Authorization` header is never sent to the new host; **q7** exits with the
HTTP 500 message and tries no further entries; **q9** says the source does not
specify provider latency and identifies 900 as the request timeout. All three
correct, so 10 of 10.

q6 and q9 are the two that moved the scorer today rather than the model. The
answer wrote the payload limit as `400 000` with a narrow no-break space,
which the digit pattern did not accept, and it put the qualifier in front of
the number — "a timeout of 900 seconds" — where the fabrication guard only
looks behind it. Both were scorer gaps and both are fixed; neither changes the
verdict here, which the reader path already reached.

## So what

Entry 2 works at the parameters the corpus now uses, on the routes the pin now
permits, and StreamLake priced it at 0.0372/0.0745 per M as its endpoint row
says. Costing $0.0005 for the run, it remains the cheapest paid row in the
survey by a wide margin.

The rating is not revisited on a smoke test. This is the fixture demoted on
2026-09-08, every model run today scored 10 of 10 on it, and what it certifies
is that the model reads a 39 KB file and answers questions about it — not that
it reviews well.

## Cost

$0.000496223 for the model's half, from `status.json`: 9,917 prompt and 1,704
completion tokens through StreamLake at 0.0372/0.0745 per M, with no cache hit
(`cached_tokens` 0 — this was the route's first sight of the context). The
checking half is this agent's session and carries no costcheck window: the
scorer is mechanical and the three reader questions were settled by reading
three line ranges of the pinned file.
