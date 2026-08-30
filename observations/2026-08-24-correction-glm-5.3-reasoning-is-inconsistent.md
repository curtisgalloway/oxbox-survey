<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-08-24
venue: zenmux
model: z-ai/glm-5.3-free
kind: efficiency
source: oxbox-run
agent: claude-opus-5
---

# Correction: glm-5.3-free reasoning scales with task difficulty, and can eat an entire budget

Corrects [[2026-08-23-glm-5.3-free-reasoning-token-budget]] on two points. That
file stands as written, per the never-edit rule; this is what changed.

## Reasoning is not a fixed overhead — it scales

Four data points on the same model, ordered by task difficulty:

| Request | max_tokens | reasoning | content |
|---|---|---|---|
| "Reply with exactly: OK", bare payload | 32 | 29 tokens | **empty** |
| "Reply with exactly: OK", bare payload | 512 | 30 tokens | `OK` |
| "Reply with exactly: OK", via `ox` (effort=high) | 300 | **0** | `OK` |
| `--mode review` of a 13KB file, via `ox` | 8000 | **7995 tokens** | **empty** |

The earlier note said it "spends reasoning tokens on everything". It does not —
it spent none on a trivial prompt through `ox`. What it does is scale reasoning
to the task, and on a real review it consumed **99.9% of an 8000-token budget**
and returned an empty string with `finish_reason` set and no error.

**This one was self-inflicted and is the useful part.** `ox` defaults to
`--max-tokens 32000`. I overrode it to 8000 to be polite, and that override is
what produced the empty review. The default is well-chosen for this class of
model; lowering it on a reasoning model is how you get a silent no-op. Do not
tune `--max-tokens` down for `--mode review`.

## The Ox Alpha comparison was unmatched, and is withdrawn

The earlier file treated Ox Alpha returning `reasoning_chars=0` on short calls,
while GLM-5.3 returned reasoning, as mild evidence they are different models.
That set a bare curl payload against issue 0.1's `ox` runs — two request shapes,
not two models.

Run identically, they agree:

```
zenmux    z-ai/glm-5.3-free   completion_tokens=3    reasoning_chars=0
opencode  x-preview-f-free    completion_tokens=31   reasoning_chars=0
```

The evidence-against is withdrawn. This does not make the attribution likely —
two models both declining to reason about a trivial prompt is nearly no
information — it removes a data point that should not have been recorded as one.

A comparison is only evidence when the conditions match. The repo asserts that;
I did not apply it.
