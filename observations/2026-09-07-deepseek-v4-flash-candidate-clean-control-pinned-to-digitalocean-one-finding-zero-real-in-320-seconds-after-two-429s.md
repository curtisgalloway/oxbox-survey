<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-07
venue: openrouter
model: deepseek/deepseek-v4-flash
kind: findings
source: oxbox-run
agent: claude-fable-5-1
corpus: oxbox-clean-control
role: candidate
run: 2026-09-07T21-48-29Z
wall_s: 320
findings: 1
real: 0
usd_model: 0.0007
harness_model: claude-fable-5-1
harness_window: 2026-09-07T21:53Z..2026-09-07T21:57Z
harness_in: 4
harness_out: 456
harness_cache_read: 239535
harness_cache_write: 558
harness_note: the finding is C3 restated, so the check was a lookup against the standing ruling and its reproduction of 2026-09-06, one turn; no new reproduction was run
---

# DeepSeek V4 Flash on the clean control, pinned to DigitalOcean: one finding, zero real, 320 seconds, on the third attempt and the cheapest route

**What happened** — The second of the two pinned runs made the day oxbox
1.1.0 shipped the provider pass-through. The `oxbox-clean-control` payload
(`jailtest.py` at `6302b12`, 6,096 B, review mode, effort high, 100,000
tokens, temperature 0.2, byte-identical to every other run on this fixture)
went to `deepseek/deepseek-v4-flash` with `provider: {"only":
["digitalocean"], "allow_fallbacks": false}`. The first two attempts were
refused 429 by DigitalOcean's shared pool (recorded separately as an
availability observation of this date); the third, five minutes later, was
served by DigitalOcean and answered in 320 seconds: 3,546 completion tokens,
2,956 of them reasoning, finish `stop`, `route: DigitalOcean`, $0.0007
billed. One finding.

**F1**, stated as a defect without an UNCERTAIN label: `stat_outside` stats
`EXISTING[0]` unconditionally, so when that is `/etc/shadow` and the suite
runs as root the stat succeeds, the probe reports FAIL, and "the jail
actually does contain the path (it is not present in the bind-mounted
filesystem), so the failure is spurious". **Invention, by the C3 ruling.**
This is C3 (GLM-5.3 Flash, 2026-09-06) and D1 (this model, yesterday, from
Novita) in a third wording, and the editor ruled it on the reproduction of
2026-09-06: `/etc` *is* bound into the jail (`oxbox:190-197` `--ro-bind`s it
on Linux; the seatbelt profile allows the read), the stat succeeds at any
uid because it needs only search permission on the directory, and at uid 0
the FAIL is true — root reads the host's shadow file from inside the jail.
The finding's own premise, that the path is absent from the jail, is the
part that is false. Recorded 0 real of 1.

Compared with the same model's other answers to these bytes: "no defects
found" as a baseline on 2026-09-02 (from DigitalOcean); nothing in 33
minutes, then D1 and D2, as a candidate yesterday (StreamLake, then Novita);
one DNS-timeout invention from StreamLake three hours ago; and now C3 again
from DigitalOcean. Five answers, all different, one right.

## Evidence

```
oxbox send --venue openrouter --model deepseek/deepseek-v4-flash --mode review \
  --stdin --files jailtest.py --max-tokens 100000 --temperature 0.2 --effort high \
  --provider '{"only": ["digitalocean"], "allow_fallbacks": false}' \
  --log-dir /Users/curtisg/src/oxbox/logs < corpora/prompts/oxbox-clean-control.txt
oxbox-send: log -> /Users/curtisg/src/oxbox/logs/2026-09-07T21-48-29Z
oxbox-send: venue=openrouter model=deepseek/deepseek-v4-flash mode=review effort=high context=6096B files=1
oxbox-send: finish=stop prompt_tokens=1837 completion_tokens=3546 reasoning_chars=11861 route=DigitalOcean
```

`meta.json` records `"provider": {"only": ["digitalocean"], "allow_fallbacks":
false}` and `ox_version` 1.1.0; `status.json` records `route: DigitalOcean`,
`venue_cost` 0.00072046, `truncated` false. The endpoints listing at 21:43Z
had DigitalOcean at $0.0679 in / $0.168 out per million — the cheapest of the
fifteen routes and below the catalog row — quantization `unknown`, output
cap 943,718.

The answer's statement of defect, as written (1,694 bytes in full, in
`content.md`):

> The `stat_outside` probe uses `EXISTING[0]` unconditionally, but if the
> first sensitive path is `/etc/shadow` (which is listed in `DAC_DEPENDENT`)
> and the test is run as root, the `os.stat` call succeeds because root
> bypasses DAC permissions. The probe then incorrectly reports a failure
> because it expects the operation to be blocked, even though the jail is
> actually containing the path via absence (since `/etc/shadow` is inside a
> directory not bind-mounted). This produces a false-positive "JAIL LEAKS"
> result.

| id | as stated | ruling | recorded |
|---|---|---|---|
| F1 | root stat of `/etc/shadow` gives a false FAIL; the path is absent from the jail | C3, 2026-09-06: `/etc` is bound, the stat succeeds at any uid, and at uid 0 the FAIL is true | invention |

## So what

The route that served this model's one ideal answer on this fixture (the
2026-09-02 baseline, "no defects found", also DigitalOcean) served an
invention today on the same bytes, and the route that served nothing
yesterday served a different invention this afternoon. Across the two pinned
runs and the three unpinned ones, the route explains price and latency and
does not explain what the model says. That is the useful result of the
pinned pair: the manifest's `provider` field, when the survey fills one, is a
price guard and a reproducibility aid, not a quality lever. On price it is a
real lever — this run cost $0.0007 against $0.0015 for the identical payload
on StreamLake three hours earlier, with fewer than half the completion
tokens.

Four candidate runs on this fixture now stand for this model, 1 real of 4
findings emitted, the one being D2 under the G1 ruling.

## Cost

### Under test

| run | model | mode | context | prompt | completion | reasoning | usd |
|---|---|---|---|---|---|---|---|
| `2026-09-07T21-48-29Z` | `deepseek/deepseek-v4-flash` | review | 6,096 B | 1,837 | 3,546 | 2,956 | $0.0007 billed |

usd is the `venue_cost` OpenRouter returned for the DigitalOcean route; the
archived catalog price (2026-09-01.json) computes $0.0006, so this route
bills about 1.1x the list row on this token mix (its input rate is below
list, its output rate above). Reasoning tokens are inside completion and
priced as output.

### Harness

| model | lane | turns | input | output | thinking | cache read | cache write |
|---|---|---|---|---|---|---|---|
| `claude-fable-5-1` | main | 1 | 4 | 456 | 0 | 239,535 | 558 |

Window: 2026-09-07T21:53:00 .. 2026-09-07T21:57:00 (given). The verification
was one turn: the finding is C3 in different words, and the ruling on C3
rests on a reproduction already on the record, so nothing was re-run. The
window is therefore a floor as much as a ceiling: the reproduction it leans
on cost what the 2026-09-06 reproduction observation records, not what this
window holds.
