<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-01
venue: openrouter
model: "-"
kind: access
source: probe
agent: claude-fable-5-1
---

# Eight of OpenRouter's 21 free rows return the data-policy 404 on this account, which is a gate and not a missing route

**What happened** — the 2026-09-01 tripwire (`oxsurvey --probe --tripwire`, one
request per free model, this survey's account) got `404` from eight of the 21
free rows with the same body every time:

```
{"error":{"message":"No endpoints available matching your guardrail restrictions
and data policy. Configure: https://openrouter.ai/settings/privacy","code":404}}
```

The eight: `liquid/lfm-2.5-2.6b:free`, `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free`,
`nvidia/nemotron-3-super-120b-a12b:free`, `nvidia/nemotron-3-ultra-550b-a55b:free`,
`nvidia/nemotron-3.5-content-safety:free`, `nvidia/nemotron-3.5-lightning:free`,
`poolside/laguna-s-2.1:free`, `poolside/laguna-xs-2.1:free`. Six rows answered and
scored `correct`; three were rate-limited upstream; two audio previews rejected a
text request with 400; the two Thinking Machines rows are a separate story
([[2026-09-01-inkling-free-is-only-served-to-agentic-harnesses]]). Full record:
`snapshots/openrouter/2026-09-01-access.json`.

## Evidence

The body is the message issue 0.1 documented for cloaked models before prompt
logging was enabled, and it names the account's privacy page. It does not say the
model has no endpoints; it says none matches *this account's* restrictions. The
same two Nemotron models answer on Requesty (`nemotron-3-super-120b-a12b` scored
`correct` there in the same minute; `-ultra` returned a 503 overload).

## So what

**This corrects a reading in `docs/decisions.md`.** The 2026-08-30 tripwire note
counted "10 `not_found`" and called the Nemotron 404-on-OpenRouter, answers-on-
Requesty pair a card contradiction: "the catalog lists models the endpoint does
not serve". The body of the 404 says otherwise. It is a policy gate on this
account, most likely the setting that governs providers who may train on or
retain inputs, and whether these eight rows answer under looser settings is
untested. The catalog is not impeached by it; the account configuration is
documented by it.

Two follow-ups, neither done here:

- `oxsurvey`'s `classify()` should split this body out of `not_found` into its
  own verdict (`policy_blocked` or similar), because a 404 that names the
  account's settings and a 404 that means the route is gone argue for opposite
  actions.
- Someone with the account should record which privacy toggles are set, so the
  eight can be re-probed under a known configuration. Until then, "8 of 21
  unreachable" is a fact about one account on one day.
