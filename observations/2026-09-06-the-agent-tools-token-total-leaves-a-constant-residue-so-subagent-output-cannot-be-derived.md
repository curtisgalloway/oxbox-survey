<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-06
venue: claude-code
model: "-"
kind: efficiency
source: manual
agent: claude-fable-5-1
---

# The Agent tool's token total leaves a near-constant residue over input and cache writes, so a subagent's output tokens cannot be derived from it

**What happened** — Six fresh checker subagents ran within three minutes on three batches. For the four ask-grounding checks the Agent tool's reported total minus the transcript's input and cache-write tokens came to 19,862, 19,990, 20,073 and 19,658, across two models, three to eight model calls, and replies of 2,200 to 2,500 visible characters. For the two clean-control checks the residue was 5,066 and 3,926; for the two clean-control checks earlier in the day, 9,744 (plausible for the reply) and 1,420 (smaller than the reply). A residue that is the same to within two percent for four different amounts of output is not output.

## Evidence

Transcripts under `be37f5ce-2218-4a5c-b328-8de99b76b7a7/subagents/`, agents a62944f8dc03a6f04, a8310a6a108e1b534, ab7ddf754c91cb2b1, a9c7ced6ae31f7cea (ask), a21f9155c55413b75, abf883a7664ca8b3d (clean control), with the Agent tool's `subagent_tokens` from each completion notice.

## So what

The derivation used for the first matched pair (output equals total minus input minus cache writes) is withdrawn as a method. The two derived figures already in the record stay with their notes and should be read as unverified. Every check record from this point carries no `harness_out` and says the output is unmeasured; the priced checking half is a floor. The only way to a fully measured checking half is a metered route, which is what `verifiercheck.py` already does by sending the verification to a model through `oxbox send` on OpenRouter, where the venue bills every token; that is toolless verification with the evidence inlined, a different job from a tool-using checker, and the survey should choose which it wants to price.
