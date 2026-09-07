<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-06
venue: openrouter
model: deepseek/deepseek-v4-flash
kind: findings
source: oxbox-run
agent: claude-fable-5-1
corpus: oxbox-clean-control
role: candidate
run: 2026-09-07T00-06-45Z
wall_s: 47
findings: 2
real: 1
usd_model: 0.0016
---

# DeepSeek V4 Flash re-run on the clean control: two findings in 47 seconds from a fourth provider, so the 33-minute blowout was the route

**What happened** — At the editor's direction (round 4, question 5), the
clean-control candidate run that had returned nothing after 33 minutes was
repeated: same `oxbox-clean-control` payload (`jailtest.py` at `6302b12`,
6,096 B, review mode, the same params). This time OpenRouter routed
`deepseek/deepseek-v4-flash` to Novita, the fourth provider this model has
been served from in five runs, and the model answered in 47 seconds:
4,774 completion tokens, 3,692 of them reasoning, finish `stop`, $0.0016
billed, which is double the catalog computation because Novita's route is
priced above the list row. Two findings.

**D1**, stated as a concrete correctness bug: the stat oracle is not skipped
for root, so a root run with `/etc/shadow` first in the list gets a FAIL that
"falsely indicates a jail leak". This is C3 again, in the same words, and the
editor ruled C3 refuted on the same-day reproduction: the stat succeeds at
any uid because `/etc` is bound, and at uid 0 the FAIL is true, root reads
the host's shadow file inside the jail. Recorded as an invention under that
ruling. Both metered checkers were run anyway for the cost record: Opus 5
REFUTED it and named the reproduction's mechanism (stat needs only search
permission, uid changes nothing); Fable 5.1 CONFIRMED it as a safe-direction
failure while noting the finding's cause is wrong. The same split, the same
way round, as C3.

**D2**, stated as UNCERTAIN and "a design limitation rather than a coding
error": the network probes count any exception as containment, so a host
with no route certifies a leaking jail. This is G1's mechanism with the
trigger stated correctly (no default gateway, connect times out, PASS). The
record holds G1 real (L1 in the key, fixed upstream), so D2 is recorded real
to match; both metered checkers REFUTED it as written, because at this pin
both backends deny the network unconditionally and no leaking jail exists
for the vacuous pass to conceal. That is the same reading Fable's checker
gave G1, and round 4 question 2 (does G1 stand?) decides D2 with it. If G1
is reversed, this row becomes 0 real of 2 by a correction observation.

Verified by the standing reproductions (C3 on both platforms on 2026-09-06;
the offline-network mechanism raised as `OSError` inside a working jail on
dev the same day) and by two metered checks, on the record as check
records.

## Evidence

Run `logs/2026-09-07T00-06-45Z`, `context_bytes` 6096, `finish_reason`
stop, `venue_cost` 0.0015939, provider Novita, 1,837 prompt tokens.

| id | as stated | Opus 5, metered | Fable 5.1, metered | recorded |
|---|---|---|---|---|
| D1 | root stat FAIL is a false leak report | REFUTED | CONFIRMED, safe direction, cause wrong | invention, by the C3 ruling |
| D2 | UNCERTAIN: offline host passes a leaking jail | REFUTED as written | REFUTED as written | real, as G1 is; question 2 decides both |

Five runs of this model on OpenRouter have now gone to four providers: the
2026-09-02 baselines elsewhere, the ask candidate to StreamLake, the
33-minute clean-control candidate to StreamLake, this one to Novita.

## So what

The blowout was the route. On the same payload the model produced a
complete review in under a minute from Novita and nothing in 33 minutes
from StreamLake, so the earlier row measures a provider, not the weights.
The row that stands beside it is unremarkable: two findings, both of them
claims the record has already adjudicated on other models, one ruled an
invention and one hanging on an open ruling. On this fixture the model is
fast and cheap and finds nothing new. The manifest cannot pin a provider,
so a user who calls this model through OpenRouter gets one of four routes
at one of at least two prices, and the 33-minute case is one of them.

## Cost

### Under test

| run | model | mode | context | prompt | completion | reasoning | usd |
|---|---|---|---|---|---|---|---|
| `2026-09-07T00-06-45Z` | `deepseek/deepseek-v4-flash` | review | 6,096 B | 1,837 | 4,774 | 3,692 | $0.0016 billed |

usd is the `venue_cost` OpenRouter returned (Novita route); the archived
catalog price (2026-09-01.json) would compute $0.0008. Reasoning tokens are
inside completion and priced as output.

### Checking

Two metered check records attach to this run, one per checker, each a
single request through OpenRouter with the bill recorded: Opus 5 $0.2319
in 79 seconds, Fable 5.1 $0.3664 in 49 seconds. The cost digit uses the
Fable record, the fixture's ceiling checker.
