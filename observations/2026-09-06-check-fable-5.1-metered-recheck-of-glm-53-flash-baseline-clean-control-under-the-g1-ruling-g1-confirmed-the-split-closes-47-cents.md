<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-06
venue: openrouter
model: "-"
kind: efficiency
source: manual
agent: claude-fable-5-1
checkers: claude-fable-5-1
run: 2026-09-03T03-21-05Z
harness_model: claude-fable-5-1
harness_venue: openrouter
harness_window: 2026-09-07T01:35Z..2026-09-07T01:37Z
harness_seconds: 73
harness_in: 17418
harness_out: 5893
harness_usd: 0.46883
harness_note: metered; one `oxbox send --mode ask` request through OpenRouter carrying the amended verifier contract (the G1 exception, 2026-09-06 night) and the five pinned files, log 2026-09-07T01-35-47Z; the control for the ruling. harness_usd is the venue_cost OpenRouter billed
---

# Fable 5.1, metered, re-checks GLM-5.3 Flash's baseline clean-control batch under the G1 ruling: G1 confirmed and the split closes, G4 confirmed as benign, 47 cents

**What happened** — The Fable 5.1 half of the control. Same four findings
(run `2026-09-03T03-21-05Z`), same five files, the amended contract, one
`--mode ask` request to `anthropic/claude-fable-5.1` through OpenRouter.
17,418 prompt tokens, 5,893 completion (4,503 reasoning), 73 seconds,
$0.4688 billed.

**G1 CONFIRMED.** Fable's in-harness checker refuted G1 on 2026-09-06 under
the old wording, on the ground that no jail at the pin permits egress. Under
the amended wording it confirms, naming the exception and adding the sentence
the ruling turns on: today's seatbelt and bubblewrap do deny network, "but
the test would not detect their loss." The Fable/Opus split on G1, one of the
two splits in the record, is closed by a change of contract, not of reader.

G2 and G3 REFUTED, as the key has them. **G4 CONFIRMED** as a benign side
effect: the file persists in `sandbox/work` and nothing removes it, while
Fable notes that two of the finding's stated consequences do not hold (the
name is overwritten, `sandbox/` is gitignored). The key accepts only REFUTED
for G4, and Opus refuted it in the same minute on those two grounds; Fable
credits the persistence and calls it benign. That is the safe-direction
distinction the contract asks for, applied to a finding with no direction at
all, and the record keeps G4 as it was.

## Evidence

Log `logs/2026-09-07T01-35-47Z`, `venue_cost` 0.46883, `finish_reason` stop,
context 36,731 B. Sent with `--force` for the two fixture strings in
`guardtest.py`.

| id | Fable 5.1, in-harness (old contract) | Fable 5.1, metered (amended) | Opus 5, metered (amended) | key |
|---|---|---|---|---|
| G1 | REFUTED | CONFIRMED | CONFIRMED | CONFIRMED |
| G2 | REFUTED | REFUTED | REFUTED | REFUTED |
| G3 | REFUTED | REFUTED | REFUTED | REFUTED |
| G4 | REFUTED | CONFIRMED, benign | REFUTED | REFUTED |

## So what

The ruling did what it was meant to: stated in the contract, the G1 exception
is applied the same way by both checkers, and the one remaining disagreement
in this batch is about whether a harmless leftover deserves the word
CONFIRMED, which changes no row. Metered, the two requests cost $0.63
together against roughly $1.60 at list for the in-harness pair on the same
batch, and both were back inside two minutes.
