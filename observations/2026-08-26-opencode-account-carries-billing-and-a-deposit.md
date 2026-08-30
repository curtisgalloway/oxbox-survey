<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-08-26
venue: opencode
model: "-"
kind: access
source: manual
agent: curtis
---

# The OpenCode account used for every probe here carries billing and a $10 deposit

**What happened** — the account holder confirms that signing up for OpenCode Zen
involved entering a credit card and depositing $10.

## Evidence

First-hand from the account holder, 2026-08-26, in response to the open question
recorded on `providers/opencode.md`.

## So what

**It closes the question the wrong way for the convenient answer, and it retires
an observation's implication rather than the observation itself.**

[[2026-08-23-opencode-zen-accepts-chat-completions]] recorded that free models
answered on a minutes-old key with no `reject_no_credit` equivalent, and hedged:
*"the account may already have had billing attached. Someone who knows should
confirm before this is quoted as 'no card required'."* It did. The account had
billing and a balance the whole time.

So that probe **never tested the cardless path**. It showed that free models work
on a funded OpenCode account — which is also true of ZenMux, and was never in
doubt.

The standing claim is therefore:

- **Measured:** free models are callable on an account with billing and a $10
  balance. No call-time credit check was observed.
- **Untested, and untestable from here:** whether they are callable without
  billing. That needs a second account with no card, which nobody is going to
  create for a survey.
- **Reported, conflicting:** the vendor's signup page describes adding a balance
  and never mentions free models; third-party write-ups say free-tagged models
  need no payment details. Our evidence cannot separate these, and should stop
  being cited as if it could.

Both venues this survey can actually speak to — ZenMux and OpenCode — were used
from funded accounts. **"Free" on a gateway has meant "free once you have money
on file" every time it has been checked here.** That is worth stating plainly in
any recommendation, because it is the opposite of how these tiers are marketed.
