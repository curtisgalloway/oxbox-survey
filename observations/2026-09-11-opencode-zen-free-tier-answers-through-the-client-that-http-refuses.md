<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-11
venue: opencode
model: "-"
kind: access
source: probe
agent: claude-opus-5
---

# OpenCode Zen's free tier is reachable, through the OpenCode client only

**What happened** — the three free listings that refuse `chat/completions` with
`400 MissingSessionID` ("OpenCode's free tier can only be used in OpenCode")
all answer through `opencode run`, on the same account, in the same minute. The
restriction is on the client, not on the credential or the listing. A second
question asked at the same time -- whether the client sees a different roster
than the HTTP catalog -- is answered no.

## Evidence

The account was connected to the local client by the account holder on
2026-09-11. `opencode providers list` reports one credential, `OpenCode Zen`.

Today's HTTP catalog is unchanged from the one the 2026-09-10 access probe ran
against, so the two surfaces below are same-day comparable:

```
$ ./oxsurvey --venue opencode --dry-run
== opencode
  70 in roster, free status UNKNOWN (no pricing in catalog)
diff against opencode/2026-09-10.json
  no changes
```

**Roster: no divergence.** `opencode models` authenticated lists 69 ids against
the catalog's 70. The only difference is `deepseek-v4-flash-free`, in the HTTP
catalog and not the client; the client's `deepseek-v4-flash` is in the HTTP
catalog too. Nothing is client-only.

```
http 70 client 69
HTTP only (1):  deepseek-v4-flash-free
client only (0):
```

This kills a lead worth naming so nobody chases it twice: run **before** the
account was connected, `opencode models` printed five ids
(`big-pickle`, `deepseek-v4-flash-free`, `minimax-m2.5-free`,
`nemotron-3-super-free`, `ring-2.6-1t-free`), three of which are in no catalog
we hold. That is an unauthenticated stub, not an entitlement list, and it is
not evidence of anything.

**Reachability: all three gated models answer.** Each run in an empty working
directory, one prompt, `--format json`:

```
$ opencode run --dir <empty> -m opencode/<id> --format json "Reply with exactly the word: pong"

big-pickle               -> "pong"   tokens in 26,925 out 4    cost 0
ling-3.0-flash-fin-free  -> "pong"   tokens in 27,415 out 3    cost 0
mimo-v2.5-free           -> "pong"   tokens in 28,491 out 16   cost 0
```

Compare the 2026-09-10 roster-wide probe on the same three ids over
`chat/completions`, recorded in `snapshots/opencode/2026-09-10-access.json`:
`400 MissingSessionID` for all three, and `big-pickle` a `503` before that.

## So what

`big-pickle` is the cloaked listing that motivated adding this venue and has
been unreachable in the record since 2026-08-23. It is reachable now, by a
route the survey does not currently use. The same goes for the rest of the free
tier, which is the part of this venue a reader most wants and the part the HTTP
path cannot serve at all.

It also settles what the refusal means. `MissingSessionID` is a client check,
not a billing gate, not a regional block and not an outage -- the credential is
accepted, the listing exists, the same account is served the moment the request
arrives with a session. A venue page that said "the free tier is not callable"
was right about the API and wrong about the venue.

What it does not establish is anything about review quality: this is a probe,
and the survey's rule is that only a run gets a row. Whether these models can
be *measured* from the client is a separate question, and the harness's token
overhead is the thing standing in the way -- see
[[2026-09-11-the-opencode-client-spends-12-to-27k-input-tokens-before-the-payload]].

## Cost

Zero on the model side: three free-tier calls, `cost: 0` reported by the client
on each. No metered checking -- the assertions here are a string comparison and
a set difference, both reproducible from the commands above.
