<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-11
venue: openrouter
model: "-"
kind: efficiency
source: manual
agent: claude-fable-5-1
checkers: claude-opus-5
run: 2026-09-10T23-42-45Z
harness_model: claude-opus-5
harness_venue: openrouter
harness_window: 2026-09-11T00:12Z..2026-09-11T00:15Z
harness_seconds: 125
harness_in: 18051
harness_out: 10072
harness_usd: 0.342055
harness_note: metered; one `oxbox send --mode ask --force` request through OpenRouter with the verifier contract (amended 2026-09-06) and the five pinned files at 6302b12, log 2026-09-11T00-12-17Z; harness_usd is the venue_cost OpenRouter billed
---

# Opus 5, metered, checks Qwen 3.8 27B's local zero-defect control run: QW2 and QW7 confirmed, eight refuted, 34 cents, 125 seconds

**What happened** — The metered check of the local `qwen3.8:27b` run on the
zero-defect control (`2026-09-10T23-42-45Z`, ten findings): the verifier
contract, the ten findings as a JSON batch with ids QW1 to QW10, and the five
pinned files (`jailtest.py`, `oxbox`, `profiles/jail.sb`, `guardtest.py`,
`.gitignore` at `6302b12`), one `--mode ask` request to
`anthropic/claude-opus-5` through OpenRouter. 18,051 prompt tokens, 10,072
completion (7,215 reasoning), 125 seconds, $0.3421 billed, route Claude
Platform on AWS.

Verdicts: QW2 CONFIRMED, QW7 CONFIRMED, the other eight REFUTED. That is the
run observation's own reading on every finding, so the record carries no
split on this batch. The check's reasons, shortened:

| id | verdict | reason |
|---|---|---|
| QW1 | REFUTED | needs a path where `stat` is denied and `open` allowed; seatbelt's `file-read*` subsumes metadata, bubblewrap leaves home paths unbound and `/etc` ro-bound |
| QW2 | CONFIRMED | the PASS does not depend on the sandbox; any exception including `socket.timeout` is recorded as containment on both platforms |
| QW3 | REFUTED | "the sandbox permits DNS" cannot be produced at this pin; `getaddrinfo` fails fast under both backends |
| QW4 | REFUTED | needs IPv4 blocked with IPv6 permitted; neither backend filters by family |
| QW5 | REFUTED | the launcher builds a fresh environment with no credential variables, plus `--clearenv` on Linux |
| QW6 | REFUTED | the stated failure is a future change; at this pin no credential is injected |
| QW7 | CONFIRMED | on Linux as root in a container with no home-relative paths, `EXISTING == ["/etc/shadow"]`, the read probe skips, the stat oracle succeeds inside the ro-bound `/etc` and reports FAIL |
| QW8 | REFUTED | `EXISTING` holds no root-owned system path but `/etc/shadow` |
| QW9 | REFUTED | `HOME` is set to the work directory unconditionally on both backends |
| QW10 | REFUTED | `OXBOX_PLATFORM` is always `sys.platform`; the empty case cannot arise and would only blank one output line |

## Evidence

Log `logs/2026-09-11T00-12-17Z`: `status.json` `venue_cost` 0.342055,
`prompt_tokens` 18051, `completion_tokens` 10072, `reasoning_tokens` 7215,
`finish_reason` stop, `route` "Claude Platform on AWS". The response is a
single JSON object with ten entries in batch order.

## So what

The checking half is the whole bill for a local run, and it is the same bill
as for a hosted one: 34 cents here against 38 cents for Opus 5's own nine
findings and 41 cents for GPT-5.6 Terra Pro's five on 2026-09-10. Ten
findings from a model that cost nothing to run still cost a third of a dollar
to read, and eight of the ten were inventions the record already held.
