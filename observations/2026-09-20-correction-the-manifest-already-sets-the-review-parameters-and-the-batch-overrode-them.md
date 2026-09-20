<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-20
venue: openrouter
model: deepseek/deepseek-v4-flash
kind: findings
source: manual
agent: claude-opus-5
role: candidate
corrects: 2026-09-20-the-first-genuine-work-finding-with-a-verdict-a-benign-watermark-ordering-bug.md
---

# Correction: the manifest already sets the review parameters, and the batch overrode them

**What changed** — the claim that "the fixture's parameters do not fit real
work" and that this is "worth a corpus decision before the next batch" is
wrong, and the conclusion drawn from it was too broad. The parameters for
genuine work were already correct and already separate. The batch did not
inherit them; it overrode them by hand with the fixture's.

`manifests/latest.json` carries `defaults.max_tokens` 100,000 and `effort:
high` on both entries. A batch sent through `--manifest` gets those. The
2026-09-20 batch was sent with `--max-tokens 8000 --temperature 1.0 --effort
medium`, copied from `oxbox-ask-grounding-v2` — the mitigated parameters the
editor set on 2026-09-10 for a ten-question quiz, after local models looped to
the cap on the zero-defect control.

So the truncated first attempt, its `finish=length`, and the $0.00073 it cost
for nothing are all real and all self-inflicted. Nothing about the corpus or
the manifest needed changing.

The finding itself, its benign verdict, the 429 on entry 1 and the costs are
unaffected; only the parameters paragraph and its recommendation are
withdrawn.

## The rule that was missing

Not a new parameter set — a line saying which of the two existing ones
applies. Fixture parameters belong to the fixture they were tuned on. A
genuine-work batch takes the manifest's, because the manifest is what a reader
of the survey would use and the point of collecting real batches is to measure
what a reader gets.

Written into the review skill so the next batch inherits it rather than
rediscovering it. The general form is worth stating too: **a corpus fixture's
params are a property of the fixture, not defaults.** They encode a decision
about one task — here, that 8,000 tokens is four times the longest answer
anyone had given on a quiz — and carrying them to a different task carries a
conclusion that was never about it.

## So what

The session's own instinct was to write a decision entry proposing a separate
parameter set for real work. That separation already existed, in the file whose
whole purpose is to say what a reader should send. The error was not a missing
rule but a collapsed distinction, and the fix is one sentence in the skill
rather than a new axis in the corpus.
