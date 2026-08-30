<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-08-24
venue: opencode
model: x-preview-f-free
kind: findings
source: oxbox-run
agent: claude-opus-5
---

# Ox Alpha found a real credential leak in oxbox: 5 findings, 0 false positives

**What happened** — `--mode review` over `ox` (13.6KB), asked to check the
venue-selection and credential-resolution code against the invariant "a
credential must never be sent to a host it does not belong to". It found a
genuine, exploitable vulnerability that had been in oxbox since before the venue
work, plus four other real defects, and invented nothing.

## The headline finding, verified by experiment

`urllib` follows 3xx automatically and its `HTTPRedirectHandler` rebuilds the
follow-up request keeping every original header — including `Authorization`.
curl and requests strip it cross-host; urllib does not.

Reproduced against a local server pair, one redirecting to the other:

```
HTTP 302 -> followed cross-host, Authorization forwarded=True,
            ox printed the attacker's content as the model's answer
HTTP 307 -> not followed, no leak
```

Both halves matter. The key leaks, and then `ox` presents the receiving host's
JSON to the operator as the model's answer — in a tool whose premise is that
model output is untrusted but the channel is not. Fixed in
curtisgalloway/oxbox#3 with a `NoRedirects` handler.

## Scorecard

| # | Finding | Verdict |
|---|---|---|
| 1 | Bearer token forwarded across a redirect | **real**, reproduced |
| 2 | `--base-url` unvalidated: `http://` cleartext, scheme-less → traceback | **real**, traceback reproduced |
| 3 | non-JSON 200 → uncaught decode error, no `error.txt` | plausible by inspection, **not tested** |
| 4 | `{"choices": []}` → `IndexError` | **real**, confirmed |
| 5 | 1-second log stamp + `exist_ok=True` → parallel runs overwrite audit records | **real**, confirmed by inspection |

**Five findings, four confirmed, one untested, zero false positives.** It also
wrote an accurate "what is correct in the reviewed area" section — the pairing
logic, the `venue != "custom"` guard, and that only the env-var *name* reaches
the logs — all of which check out. And it correctly separated in-scope findings
from three it flagged as "noticed in passing".

Cost: 3611 prompt tokens, 16704 completion (4935 reasoning), roughly 15 minutes.

## So what

This is the first `source: oxbox-run` finding evidence in the repo and the
first that could justify a `USE`. It is one file and one prompt — not a
benchmark — but it is a better result on a review task than anything in the
named tier has demonstrated, and it is the kind of defect the vendor
patch-generation scores say nothing about.

It also cost me a claim. I wrote in oxbox#2 that binding each venue to its own
key variable made a misdirected credential "impossible by construction". That
holds at the CLI layer and says nothing about the runtime redirect path. The
model was reviewing the invariant I asserted, and the invariant was false.
