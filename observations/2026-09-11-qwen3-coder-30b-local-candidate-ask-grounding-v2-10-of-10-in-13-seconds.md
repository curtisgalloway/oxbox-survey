<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-11
venue: ollama
model: qwen3-coder:30b
kind: findings
source: oxbox-run
agent: claude-fable-5-1
corpus: oxbox-ask-grounding-v2
role: candidate
run: 2026-09-11T02-49-26Z
wall_s: 13
hits: 10
hits_of: 10
usd_model: 0
usd_total: 0
---

# Qwen3-Coder 30B, local, on ask-grounding at the v2 parameters: 10 of 10 in 13 seconds

**What happened** — `oxbox-ask-grounding-v2` (`ox` at `6072d56`, 39,467 B,
`--mode ask`, effort medium, 8,000 tokens, temperature 1.0, the reasoning
field dropped because ollama refuses it for this model) put to
`qwen3-coder:30b` served by ollama 0.34.0 on argenta, through the local
setup described in
`2026-09-11-qwen3-coder-30b-local-candidate-zero-defect-control-a-thousand-findings-from-five-templates-zero-real-in-25-minutes.md`.
Ten of ten in 13 seconds, 461 completion tokens, the shortest answer on
this fixture in the record. Question 8: "ox does not retry; it immediately
fails," which is the key's answer and the shape it credited on 2026-09-02;
at v1 the same model had said ox "waits before retrying" and scored 9.

## Evidence

Log `logs/2026-09-11T02-49-26Z`, `context_bytes` 39467, `finish_reason`
stop. The scorer: all five executable facts match the key; 1, 3, 4, 5, 6, 8,
9 and 10 correct mechanically, 2 and 7 for a reader. By hand: 2 says the
redirect is refused and an `HTTPError` returned, adding that the header
"would be forwarded to the new host if the redirect was followed, but
since redirects are" refused it is not; 7 says ox exits with the
`AttemptFailed` error and tries no other entry. Both the key's answers.
10 of 10.

## So what

The fastest correct answer on the quiz, twice now, from the model that
produced a thousand invented findings on the control at v1. The quiz is a
smoke test and a non-thinking coder model passes it with time to spare;
what the parameters did to its review behavior is in its v2 control row.

## Cost

Nothing billed; mechanically scored, so `usd_total` equals `usd_model`.
