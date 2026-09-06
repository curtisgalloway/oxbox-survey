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
checkers: claude-opus-5, claude-fable-5-1
run: 2026-09-06T21-30-07Z
harness_model: claude-opus-5
harness_window: 2026-09-06T21:59Z..2026-09-06T22:05Z
harness_in: 8
harness_out: 10758
harness_cache_read: 184557
harness_cache_write: 87230
harness_seconds: 308
harness_note: output is the Agent tool's reported total (97,996) minus input and cache writes; subagent transcripts do not record final output
---

# Opus 5 and Fable 5.1 check the same four findings: Opus spends 1.2x the tokens and 1.5x the output, and still costs 32% less, not the 47% that repricing Fable's tokens predicted

**What happened** — The editor challenged the cost table's "same checking at
Opus 5 prices" column: it reprices Fable 5.1's verification tokens at Opus 5's
list price, which assumes Opus would spend the same tokens on the same job,
and one of Fable's claims is that it spends fewer. So the job was run twice.
Two fresh Claude Code subagents, one on `claude-opus-5` and one on
`claude-fable-5-1`, received byte-identical instructions (the
`verify-findings.txt` contract, inlined) and the same five files from oxbox at
`6302b12` extracted into a scratch directory they were told was the only
source: `jailtest.py`, `oxbox`, `profiles/jail.sb`, `guardtest.py`,
`.gitignore`. The batch was the four findings GLM-5.3 Flash emitted on the
clean control as a candidate the same afternoon (run
`2026-09-06T21-30-07Z`). Neither checker could see the recorded verdicts.

| | Opus 5 | Fable 5.1 | ratio |
|---|---|---|---|
| harness-reported total tokens | 97,996 | 83,047 | 1.18 |
| model calls / tool uses | 4 / 6 | 3 / 6 | |
| wall clock | 308 s | 117 s | 2.6 |
| input (transcript) | 8 | 66 | |
| cache read (transcript) | 184,557 | 114,892 | 1.61 |
| cache write (transcript) | 87,230 | 75,858 | 1.15 |
| output, derived (total minus input minus cache write) | 10,758 | 7,123 | 1.51 |
| USD at own list price | $0.907 | $1.334 | 0.68 |
| USD if Fable's tokens are repriced at Opus's rates | | $0.710 | |

Prices from the 2026-09-01 OpenRouter catalog: Opus 5 $5 in, $25 out, $0.50
cache read, $6.25 cache write per million; Fable 5.1 $10, $50, $0.25, $12.50.

**Both directions at once.** Fable did use fewer tokens, on every axis the
record can measure, and finished in a third of the time. Opus was still
cheaper, because its unit prices are half Fable's on input, output and cache
write; only on cache read is Fable the cheaper model per token, and cache
read is the smallest dollar line here. Repricing Fable's tokens at Opus's
rates gave $0.71; Opus actually cost $0.91, so the repriced column understated
Opus by 28% on this batch. The column is withdrawn from `ratings.py --costs`
and replaced by this measurement, cited in the footer, until there are more
pairs.

## Evidence

Transcripts: `be37f5ce-2218-4a5c-b328-8de99b76b7a7/subagents/agent-a7b623340782f6574.jsonl`
(Opus) and `agent-a85200dd9783c88ed.jsonl` (Fable) under the survey project's
Claude Code directory, with `.meta.json` files naming the model.

**How the token figures were read, and one that could not be.** A subagent
transcript stores each message's start-of-stream usage: `stop_reason` empty,
`output_tokens` of 3 to 6 per message, while the main lane stores the final
usage. Input, cache read and cache write are final at stream start and were
summed over distinct message ids. Output is not in the transcript at all. The
Agent tool reports a total per subagent (`subagent_tokens`), and on both
transcripts that total minus input minus cache write leaves a residue of the
right size for the visible text plus thinking, so output is derived from it
on the stated assumption that the total is input plus output plus cache
writes. That assumption is the one unmeasured thing in the table and is
flagged rather than buried. A consequence for the repo's tooling:
`costcheck.py`'s subagent lane has always undercounted output for the same
reason, and now says so when it prints one.

**Verdicts.** Fable: C1 REFUTED, C2 REFUTED, C3 CONFIRMED, C4 REFUTED,
matching the verdicts recorded in the GLM candidate observation. Opus: C1
REFUTED, C2 REFUTED, C3 REFUTED, C4 REFUTED. The C3 dissent is not noise.
C3 as written says the stat oracle reports a false FAIL when `EXISTING[0]` is
`/etc/shadow` and the process runs as uid 0. Opus's reason: at uid 0 inside
the Linux jail, `/etc` is read-only bound and root can read `/etc/shadow`, so
the FAIL is genuine, not false; the false FAIL arises at other uids, which
the finding did not state. Fable's CONFIRMED noted the same thing in passing
("in fact this happens at any uid") and credited the finding anyway, which is
the generous reading the contract forbids. Under "score the finding as
written", Opus's verdict is the defensible one, and the recorded CONFIRMED on
that row deserves the maintainer's second look.

## So what

**Never reprice one model's tokens at another model's rates.** The cost
table names the checking model and prices its own tokens; a comparison
between supervisors is a second run, not a multiplication. This pair is n=1
on a four-finding batch and should be read as the first point, not the rate.

**The cheaper supervisor on this job was the one with lower unit prices,
despite spending more.** That is the ordinary case and it is why the
"Checked by" column exists.

**The one place the transcript lies.** Subagent output tokens are not
recorded; any tool summing them from the transcript reports a number near
zero and looks precise doing it. Read the harness's reported total, state
how the output was derived, or say the output is unmeasured.
