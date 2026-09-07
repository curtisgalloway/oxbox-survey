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
run: 2026-09-07T21-39-41Z
wall_s: 151
findings: 1
real: 0
usd_model: 0.0015
harness_model: claude-fable-5-1
harness_window: 2026-09-07T21:39Z..2026-09-07T21:45Z
harness_in: 392
harness_out: 14832
harness_cache_read: 3214201
harness_cache_write: 46985
---

# DeepSeek V4 Flash on the clean control, pinned to StreamLake: one finding, zero real, 151 seconds, and the route named in the request is the route that answered

**What happened** — The first pinned run the survey has made. oxbox 1.1.0
shipped the OpenRouter provider pass-through earlier today, so the
`oxbox-clean-control` payload (`jailtest.py` at `6302b12`, 6,096 B, review
mode, effort high, 100,000 tokens, temperature 0.2 — byte-identical to the
2026-09-06 runs, `user` message 6,603 B in both) was sent to
`deepseek/deepseek-v4-flash` with `provider: {"only": ["streamlake/fp8"],
"allow_fallbacks": false}`. StreamLake is the route that returned nothing in
33 minutes on 2026-09-06. This time it answered in 151 seconds: 7,682
completion tokens, 7,533 of them reasoning, finish `stop`, `route:
StreamLake` in `status.json`, $0.0015 billed. One finding.

**F1**, stated as a defect without an UNCERTAIN label: `dns_lookup` calls
`socket.getaddrinfo` with no timeout, so "if the jail blocks DNS by silently
dropping packets" the resolver hangs and the suite never completes.
**Invention.** The jail does not drop packets; it denies the calls. At the
pin, `profiles/jail.sb:7` is `(deny network*)` and the Linux launcher runs
bubblewrap with `--unshare-all` (`oxbox:179`), so there is no interface to
send a query on. Reproduced on macOS inside the current seatbelt jail (same
profile line): `getaddrinfo("example.com", 443)` raised `gaierror [Errno 8]`
in 0.006 s, and `openrouter.ai` in under a millisecond. The Linux half is the
settled verdict on L2 and P4 (verdict key, 2026-09-03), which is this
finding's shape — a firewall DROP is a different system from the sandbox
being tested — and is cited rather than re-run. The stated consequence needs
a state the pin cannot produce, which is the C3 rule for a refutation; the
G1 exception does not apply, because the check does depend on the property
it certifies (denied → raises → PASS; permitted → resolves → FAIL). Recorded
0 real of 1.

So the model that answered "no defects found" as a baseline on 2026-09-02
(the ideal result on this fixture) and gave two adjudicated re-treads as a
candidate yesterday produced one invention today, from the route that
produced nothing yesterday. Three runs, three different outputs, same bytes.

## Evidence

```
oxbox send --venue openrouter --model deepseek/deepseek-v4-flash --mode review \
  --stdin --files jailtest.py --max-tokens 100000 --temperature 0.2 --effort high \
  --provider '{"only": ["streamlake/fp8"], "allow_fallbacks": false}' \
  --log-dir /Users/curtisg/src/oxbox/logs < corpora/prompts/oxbox-clean-control.txt
oxbox-send: log -> /Users/curtisg/src/oxbox/logs/2026-09-07T21-39-41Z
oxbox-send: venue=openrouter model=deepseek/deepseek-v4-flash mode=review effort=high context=6096B files=1
oxbox-send: finish=stop prompt_tokens=1837 completion_tokens=7682 reasoning_chars=28948 route=StreamLake
```

`meta.json` records `"provider": {"only": ["streamlake/fp8"], "allow_fallbacks":
false}` and `ox_version` 1.1.0; `status.json` records `route: StreamLake`,
`venue_cost` 0.001524, `truncated` false. The endpoint slug is the `tag` from
`GET /api/v1/models/deepseek/deepseek-v4-flash/endpoints`, which at 21:43Z
listed StreamLake at $0.0886 in / $0.177 out per million, fp8, 384,000 output
cap, `uptime_last_30m` 98.3.

The answer, in full (629 bytes):

> **Finding 1: Missing timeout in `dns_lookup` (line 84)**
> The call to `socket.getaddrinfo("example.com", 443)` does not set a timeout,
> so if the jail blocks DNS by silently dropping packets, the resolver may hang
> indefinitely instead of raising an exception, causing the test to never
> complete.
>
> **Failure scenario:** The jail drops all outbound DNS queries. `dns_lookup`
> calls `socket.getaddrinfo`, which sends a DNS query and blocks waiting for a
> response. With no timeout, the system resolver may wait for a long default
> timeout (e.g., 30+ seconds) or hang forever, preventing the test from
> finishing and reporting results.

The reproduction, inside `oxbox jail` (seatbelt, `network=DENIED`):

```
example.com gaierror [Errno 8] nodename nor servname provided, or not known 0.006s
openrouter.ai gaierror [Errno 8] nodename nor servname provided, or not known 0.000s
```

| id | as stated | reproduction | recorded |
|---|---|---|---|
| F1 | no timeout on `getaddrinfo`; a silent DNS drop hangs the suite | both backends deny the call and it raises in 6 ms; no drop state exists at the pin | invention, by the L2/P4 verdicts and the C3 rule |

## So what

Two things, and the second matters more than the first.

The pin works as the survey needs it to: the route named in the request is
the route that answered, `meta.json` says what was asked for and
`status.json` says what came back, and for the first time a row on this
venue measures a provider rather than a lottery. Eight runs of this model on
OpenRouter have now gone to StreamLake four times, DigitalOcean three and
Novita once, and this is the only one where that was chosen.

The second: yesterday's conclusion that "the blowout was the route" gets
its first same-route control, and it is not clean. StreamLake, pinned,
answered the identical payload in 151 seconds today after producing nothing
in 33 minutes yesterday. So the 2026-09-06 failure was StreamLake *that
hour*, not StreamLake as such — the route explains the difference between
two runs on one day, and does not predict the next one. What a pin buys is
attribution, not stability. The manifest entry for this model, if it ever
carries a pin, should carry it for the price guard (`max_price` at list)
and for reproducibility of the measurement, not because one route is the
good one.

## Cost

### Under test

| run | model | mode | context | prompt | completion | reasoning | usd |
|---|---|---|---|---|---|---|---|
| `2026-09-07T21-39-41Z` | `deepseek/deepseek-v4-flash` | review | 6,096 B | 1,837 | 7,682 | 7,533 | $0.0015 billed |

usd is the `venue_cost` OpenRouter returned for the StreamLake route; the
archived catalog price (2026-09-01.json) computes $0.0012, so this route
bills about 1.3x the list row. Reasoning tokens are inside completion and
priced as output. The completion is 61% larger than yesterday's Novita run
on the same payload (7,682 vs 4,774), almost all of it reasoning.

### Harness

| model | lane | turns | input | output | thinking | cache read | cache write |
|---|---|---|---|---|---|---|---|
| `claude-fable-5-1` | main | 15 | 392 | 14,832 | 7,034 | 3,214,201 | 46,985 |

Window: 2026-09-07T21:39:00 .. 2026-09-07T21:45:00 (given). Upper bound: the
window also holds the launch of the two DigitalOcean-pinned attempts that
were refused (see the availability observation of the same date), which
cost no model tokens and a few hundred harness tokens. The verification was
one reproduction and one comparison against the verdict key, so the ratio is
the lowest this fixture has recorded: harness input+output 1.6x the model's
prompt+completion, 339x with cache reads.
