<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-20
venue: openrouter
model: deepseek/deepseek-v4-flash
kind: findings
source: oxbox-run
agent: claude-opus-5
role: candidate
run: 2026-09-19T02-03-00Z-2, 2026-09-19T02-03-48Z-2
wall_s: 62
findings: 5
real: 0
benign: 0
usd_model: 0.0010
usd_total: 0.0010
---

# The first genuine-work rows: one correct clean verdict, and five findings on real code, none of them real

**What happened** — the two runs that answered during the ten days the pin was
broken, adjudicated. Both are `curtisgalloway/paniolo`, both
deepseek-v4-flash routed to StreamLake on 2026-09-19, both `review` mode on
code the editor was actually working on. Under the 2026-09-20 rule that
ratings come from genuine work rather than fixtures, these are the first such
rows the record has.

## The clean verdict — correct

`02-03-00Z-2`, reviewing `packaging/scripts/postinstall.sh` and its test
(1,643 in / 2,792 out, $0.00035, 45 s). It returned:

> The code is correct. No defects found.

and then said what it had checked: that only `configure` is handled and other
dpkg actions exit 0 per Debian Policy, that the constructs are POSIX and run
under dash, and that quoting and word-splitting are right.

Verified against the file. It is `#!/bin/sh` with `set -e`, `case "$1"`, and
`[ -n "${2:-}" ]` to tell a fresh install from an upgrade — which is exactly
the Debian Policy 6.5 distinction the script's own comment cites. Quoting is
correct throughout. **Zero findings was the right answer, and the account of
what was checked is accurate rather than decorative.** That is the ideal
result on clean code, and the first time this record has one from real work
instead of the zero-defect fixture.

## The five findings — all invented

`02-03-48Z-2`, reviewing two release-workflow excerpts (4,201 in / 4,526 out,
$0.00064, 62 s). Five findings, adjudicated one at a time:

| # | claim | verdict |
|---|---|---|
| 1 | `$HELPERS` is undefined in the bottle loop | **refuted** — defined at workflow level, `release.yml:43` |
| 2 | verification does not reject extra files in the bottle | **not a defect** — a hardening preference, no failure demonstrated |
| 3 | the guard's regex misses `set -euo pipefail` | **refuted by execution** |
| 4 | the guard falsely flags POSIX `set -o errexit` | **refuted** — an explicit allowlist handles it |
| 5 | the macOS bottle step has no commands | **excerpt truncation**, as the model itself suspected |

Findings 3 and 4 were settled by running the real regex rather than reading it:

```
SET_O = re.compile(r"\bset\s+(?:-[a-z]+\s+)*-[a-z]*o\s+([A-Za-z_-]+)")

set -euo pipefail      match=True   group=pipefail
set -o errexit         match=True   group=errexit
```

So `set -euo pipefail` *is* matched — finding 3 is false, and the guard's own
test data asserts the same thing on its line 118. And `set -o errexit` is
matched *by design*: the captured option name is checked against `DASH_SET_O`,
an allowlist whose comment says it was verified against dash 0.5.12 precisely
so that writing `set -o errexit` does not fail a step. Finding 4 is false for
the reason the code already documents.

Findings 1 and 5 were both labeled UNCERTAIN by the model, and in both cases
its stated reason was the right one — that the excerpt might not show the
whole picture. It was right about the reason and still filed the finding.
Under the 2026-09-10 scored-as-written ruling a finding is what it claims, and
these claimed defects.

## So what

**Five inventions on real code, against zero on a clean file, from the same
model on the same afternoon.** That pairing is more informative than either
run alone: the model does not invent reflexively — handed a small correct
script it said so plainly — but handed excerpts of a larger system it produced
five confident, specific, wrong defects, two of them with line numbers.

**And three of the five trace to what it was given, not to what it is.** The
prompt names `test_workflow_container_shell.py`, describes what that guard
does, and asks "whether the guard has gaps" — while sending only the two YAML
excerpts. The file whose regexes findings 3 and 4 quote was never in the
request.
[[2026-09-20-the-review-prompt-named-a-file-it-did-not-send]]

**No rating is written from this.** Two runs on one project on one afternoon,
one of which was set up to fail. The 2026-09-20 rule asks for genuine work and
this is genuine work; it is not yet a week of it.

## Cost

$0.00099 for the two runs together, from `status.json`: $0.00035007588 and
$0.00064197532, both StreamLake at 0.0372/0.0745 per M. The checking half is
this agent's session and carries no costcheck window: the verdicts came from
reading `release.yml`, `postinstall.sh` and the guard, and from running the
guard's regex against five inputs.
