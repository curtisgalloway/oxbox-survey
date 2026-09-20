<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-20
venue: openrouter
model: "-"
kind: access
source: probe
agent: claude-opus-5
---

# US-only routing keeps both paid entries, none of the free tier, and breaks both published pins

**What happened** — the in-region routing the editor put on the list on
2026-09-11 is live on this account, and the experiment that decision describes
has now run. Every one of the 25 free rows in the 2026-09-20 catalog fails
closed on the US edge. Both of the manifest's paid entries reach it. Neither
entry reaches it **with the pin the manifest publishes**, for two different
reasons.

## Evidence

One request per model to `https://us.openrouter.ai/api/v1/chat/completions`,
`max_tokens: 1`, anything that failed re-checked against the global edge.

**The free tier, 25 of 25 refused**, every one with the same message and the
same funnel step:

```
404 "No endpoints found supporting your data region." | Filter by Data Region
```

Nine of those 25 answered on the global edge in the same minute, so for at
least nine the region filter is demonstrably the only thing in the way. The
other sixteen were independently unavailable at that moment (403 on this
account's data policy, 404, 429, 502) and the region filter refused them
first regardless.

**The two paid entries, unpinned, both reach the US edge:**

| model | US provider | measured cost | in/out |
|---|---|---|---|
| `z-ai/glm-5.3-flash` | Sail Research | $0.0000009595 | 13 / 1 |
| `deepseek/deepseek-v4-flash` | Azure | $0.0000016100 | 5 / 1 |

Azure bills its published `azure/us` endpoint row exactly: 5 x $0.21/M +
1 x $0.56/M = $0.00000161, which is the figure returned. The Sail Research
figure does not reconcile with the global `sail-research/us` row of
0.1425/0.475 and is left unexplained here; one request at one prompt token
count is too little to derive a rate from.

**With the manifest's own pins, both entries fail closed**, at different
steps:

```
z-ai/glm-5.3-flash         us  404  Filter by Allowed Providers
deepseek/deepseek-v4-flash us  404  Filter by Max Price
```

Pinning each of entry 2's routes alone shows why they differ. Neither
`streamlake/fp8` nor `digitalocean` is available US-side at all — each
returns `Filter by Allowed Providers` on its own. With both named *and* a
`max_price`, the price filter runs first and removes the one US endpoint
(Azure) before the provider filter is reached, so the funnel names the price
step. Same underlying fact, two different error messages depending on which
filter bites first.

## So what

**For a reader who needs US-only, this publication's subject half vanishes.**
The survey is about the free and cheap pools. The free pool is 25 of 25
unreachable — not degraded, not slower, absent. The cheap pool survives, and
that is the whole of what a US-resident reader can take from the manifest.

**The published manifest does not work US-only.** Today's re-pin set
`max_price` and `only` from the endpoints API, which describes the global
endpoint set. Those are the wrong providers and the wrong prices for the US
edge, and the failure is silent in the sense that matters: it is a 404 at
routing, so a reader who switches base URLs and keeps the manifest gets
nothing at all rather than a warning.

**A US manifest would be a different document, not a flag.** Its entries would
pin Sail Research and Azure rather than GMICloud and StreamLake, and at
Azure's rate entry 2 costs 5.6x the prompt and 7.5x the completion of
StreamLake's 0.0372/0.0745. That is the price of the guarantee, and it is
large enough that it belongs in the issue as a number rather than a caveat.

**The 2026-09-11 reversal condition is partly met and needs the editor.** It
said the feature is a regulatory note rather than a venue "if the region
filter leaves nothing but paid frontier rows standing." What stands is not
frontier — it is both of the survey's own cheap paid entries, which is a
better outcome than the condition anticipated. What the condition did not
anticipate is that the pins break. So the question is not whether to build the
`openrouter-us` venue but whether to maintain a second set of pins for it, and
that is the editor's call.

## What this does not say

One probe per model, one evening, `max_tokens: 1`. Reachability only: nothing
here measures whether a US-resident route answers as well, as fast, or as
cheaply on real work. The next step the decision asks for — the same fixture
run both ways — is still unrun, and it is now a smaller experiment than
planned, because there are only two models it can be run on.
