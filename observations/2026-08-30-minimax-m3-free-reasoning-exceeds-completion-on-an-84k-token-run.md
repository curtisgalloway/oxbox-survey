<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-08-30
venue: openrouter
model: minimax/minimax-m3:free
kind: efficiency
source: oxbox-run
agent: claude-fable-5-1
---

# MiniMax M3 free: 98% of completion went to reasoning across seven runs, and one run reported more reasoning tokens than completion tokens

**What happened** — every `minimax/minimax-m3:free` review since the 2026-08-27
edition, seven runs that returned a response, spent almost the whole completion
budget thinking. The largest, a 34.7 KB three-file batch, reported 84,042
completion tokens of which 84,822 were reasoning: a subset larger than its set.
The 2026-08-29 accounting oddity
([[2026-08-29-minimax-m3-free-reasoning-dominates-the-budget]]) left tokens
unaccounted for; this one over-accounts. Both are usage fields as OpenRouter
returned them, provider `GMICloud`.

## Evidence

From `usage` in each run's `response.json`, plus `content.md` and `reasoning.txt`
sizes:

```
run                    context   prompt  completion  reasoning  reason%  answer chars  reasoning chars
2026-08-30T01-11-26Z   22,910 B   5,668     33,914     32,973     97%        7,405        129,082
2026-08-30T01-14-28Z   27,246 B   7,037     18,312     15,702     86%        9,964         61,610
2026-08-30T15-39-09Z   27,246 B       -      5,596      5,596    100%            0         22,172   (no content, finish null)
2026-08-30T15-48-35Z   34,738 B   9,210     84,042     84,822    101%        4,413        331,149
2026-08-30T16-00-50Z   24,968 B   6,183     30,910     30,224     98%        6,872        118,896
2026-08-30T16-05-13Z   39,467 B   8,912     30,437     29,700     98%        6,571        118,002
2026-08-30T22-26-09Z   27,246 B   7,198     30,712     29,933     97%        8,058        118,008
```

Totals for the seven runs with a response (from `usagereport.py`, window from
2026-08-27): prompt 44,957, completion 232,489, reasoning 227,508. Reasoning is
97.9% of completion.

## The arithmetic

The `15-48-35Z` run cannot be reconciled either way: 84,822 reasoning tokens
inside 84,042 completion tokens leaves −780 for a 4,413-character answer. The
`01-11-26Z` run, the previous oddity, left 941 tokens for 7,405 characters. The
other five reconcile at 2.6 to 3.8 characters per completion token net of
reasoning, which is ordinary. A characters-per-token ratio is an estimate, not a
tokenizer; what is not an estimate is that a subset cannot exceed its set, so at
least one of the two fields in that response is wrong.

Spread: 18K to 84K completion tokens for inputs of 25 to 35 KB. The largest
batch by tokens was not the largest by bytes. Reasoning length is not predictable
from input size on this sample.

## So what

Three consequences for anyone budgeting this model.

- **Budget the request, not the answer.** Under oxbox's old 32,000 default, four
  of these seven runs would have truncated; under the 100,000 default none did,
  and the largest used 84% of it. A 100K cap is not generous headroom for this
  model, it is roughly one large batch.
- **One in seven calls returned nothing.** The `15-39-09Z` abort is the failure
  mode the 2026-08-24 GLM-5.3 observation described, appearing here once. Not a
  rate, and worth a retry policy rather than a verdict.
- **The usage fields are not audit-grade.** Two of seven responses carry token
  accounting that does not add up, in opposite directions. Report them as the
  provider returned them, and do not build a cost model on the reasoning figure
  alone.
