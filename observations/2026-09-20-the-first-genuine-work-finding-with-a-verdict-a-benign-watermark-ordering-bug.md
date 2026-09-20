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
role: candidate
run: 2026-09-20T19-27-53Z
wall_s: 185
findings: 1
real: 0
benign: 1
usd_model: 0.0008
usd_total: 0.0008
---

# The first genuine-work finding with a verdict: a real, benign watermark ordering bug

**What happened** — the first batch collected under the 2026-09-20 rule that
ratings come from real work. Whole file, no excerpt: `usagereport.py`, 17 KB,
57 lines of which were written the same day and reviewed by nobody. One
finding came back, it is true, it reproduces, and its only effect is in the
safe direction.

## The finding

> **Watermark `max` comparison breaks with multi-digit suffixes.** When two
> runs occur in the same second, ox appends a suffix like `-2` or `-10`.
> `max()` compares lexicographically, so `...Z-10` orders *below* `...Z-2`.

**The code claim is exactly right.** `usagereport.py:375` was
`through = max(r["dir"].name for r in covered)`, and oxbox's `claim_log_dir`
increments an unpadded decimal counter until `create_dir` succeeds, so `-10`
and beyond are reachable. Reproduced:

```
run directories, in creation order:
    2026-08-30T16-05-13Z
    2026-08-30T16-05-13Z-2
    2026-08-30T16-05-13Z-10

watermark max() picks: 2026-08-30T16-05-13Z-2
```

So the watermark names an earlier directory than the one the survey actually
read through. The file it is written into is a durable contract that a pruner
compares against by string.

**The stated failure scenario does not reach.** The model's scenario has a
pruner deleting an unread later run. It cannot: `stamp_to_iso` drops the
suffix, so every run claiming the same second carries the same stamp and is
inside or outside the window together. The runs that sort below a
lexicographic watermark have therefore already been read, and deleting them is
correct. Uncovered runs have later stamps and sort above regardless.

**Verdict: benign.** Confirmed true and reproducible, and its only effect is a
failure in the safe direction — the 2026-09-07 definition, and the first time
that bucket has been earned by genuine work rather than a fixture. Fixed
anyway in the same session: `max` now takes a key that orders the suffix
numerically, because a watermark that misstates how far reading got is a false
statement in a durable artifact even where it costs nothing.

## What the batch cost, and what it says about the parameters

Three requests:

| run | model | outcome |
|---|---|---|
| `19-24-51Z` | glm-5.3-flash | **429**, GMICloud shared pool, before anything was sent |
| `19-24-56Z` | deepseek-v4-flash | `finish=length` — truncated at the 8,000-token cap |
| `19-27-53Z` | deepseek-v4-flash | `finish=stop`, 8,973 out, 185 s, $0.0008 |

Two things worth carrying forward.

**Entry 1 was unreachable again**, this time on a rate limit rather than a
price guard, so the batch is not paired. The intent was both entries on the
same input, which is mitigation 2 of the 2026-09-20 decision; one model
answered. A pairing that depends on a shared free pool being quiet is not a
pairing.

**The fixture's parameters do not fit real work.** `oxbox-ask-grounding-v2`
caps completion at 8,000 tokens, which is four times the longest answer on
that fixture — and this review hit the cap with 33,315 characters of reasoning
behind it. Raised to 40,000 and the same request finished at 8,973. A real
review of a 17 KB file is a much longer generation than a ten-question quiz
about a 39 KB one, and a parameter set tuned on the quiz truncates the review.
Worth a corpus decision before the next batch.

## Cost

$0.00079949548 for the answering run, StreamLake at 0.0372/0.0745 per M; the
truncated attempt cost $0.00073029572 and bought nothing, which is the real
price of the low cap. The checking half is this agent's session and carries no
costcheck window: the verdict came from reading `usagereport.py:375` and
oxbox's `claim_log_dir`, and from a three-line ordering demonstration.
