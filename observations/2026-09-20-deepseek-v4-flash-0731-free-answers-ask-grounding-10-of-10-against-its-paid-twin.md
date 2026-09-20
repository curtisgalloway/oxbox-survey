<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-20
venue: openrouter
model: deepseek/deepseek-v4-flash-0731:free
kind: findings
source: oxbox-run
agent: claude-opus-5
corpus: oxbox-ask-grounding-v2
role: candidate
run: 2026-09-20T01-09-15Z
wall_s: 120
hits: 10
hits_of: 10
usd_model: 0
usd_total: 0
---

# deepseek-v4-flash-0731:free answers ask-grounding 10 of 10, and costs its paid twin four and a half minutes of wall clock to match

**What happened** — the first run of one of the four free rows OpenRouter added
between the 2026-09-10 and 2026-09-20 catalogs. It answered the fixture 10 of
10 for nothing. The paid `deepseek/deepseek-v4-flash` was run immediately after
at the same parameters on the same fixture, and also scored 10 of 10 — for
$0.0005 and a fifth of the wall clock.
[[2026-09-20-deepseek-v4-flash-answers-ask-grounding-10-of-10-at-the-v2-parameters]]

## Evidence

```
oxbox-send: venue=openrouter model=deepseek/deepseek-v4-flash-0731:free mode=ask effort=medium context=39467B files=1
oxbox-send: finish=stop prompt_tokens=9917 completion_tokens=4440 reasoning_chars=15606 route=OpenInference
```

```
RESULT  PASS  (7 scored mechanically correct, 3 for a reader)
```

The three the scorer hands to a reader, adjudicated against `6072d56:ox`:

- **q2** — "ox refuses to follow the redirect ... the `Location` header's host is
  never contacted and the `Authorization` header is never sent there." Correct;
  `NoRedirects.redirect_request` returns `None` (line 114), opener built with it
  (line 423).
- **q7** — "exits with status 1; it does not try the next manifest entry,
  because `--failover` was not given." Correct; `if not args.failover:
  sys.exit(str(failure))` (line 801).
- **q9** — "ox does not know and states no such timing. The only bound in the
  script is its 900-second socket read timeout." Correct, and it walked up to
  the trap and named it as ox's own. The scorer punted because its want pattern
  does not know the phrasing "does not know", not because anything was wrong.

That is 10 of 10.

**Side by side with the paid row**, same fixture, same parameters, same hour:

| | free `-0731` | paid `deepseek-v4-flash` |
|---|---|---|
| route | OpenInference | StreamLake |
| score | 10 of 10 | 10 of 10 |
| wall | 120 s | 26 s |
| completion tokens | 4,440 | 1,704 |
| reasoning chars | 15,606 | 5,731 |
| cost | $0 | $0.000496 |

## So what

The free row answers, and on this fixture it answers as well as the paid one.
What it spends instead of money is time and tokens: 4.6x the wall clock and 2.6x
the completion for the same ten answers, and nearly three times the reasoning.
For a reader choosing a free model that is the trade, stated in the two units
that are not dollars.

Two cautions against reading this as a free-versus-paid verdict. The fixture is
a smoke test, demoted on 2026-09-08 and saturated here — every model run today
scored 10 of 10, so it separates nothing at the top and this row says "answers
correctly", not "reviews well". And the two are not the same weights: the paid
slug resolves to `deepseek-v4-flash-20260423`, which OpenRouter names in its own
routing errors, while this is the `0731` snapshot. Same family, three months
apart, one free.

## Cost

$0 for the model's half — a free row, and `status.json` records `venue_cost`
0 against 9,917 prompt and 4,440 completion tokens. The cost that is not
dollars is in the table above: 120 s of wall clock and 15,606 characters of
reasoning. The checking half is this agent's session and carries no costcheck
window: the scorer is mechanical and the three reader questions were settled by
reading three line ranges of the pinned file.
