<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-08-23
venue: openrouter
model: stealth/ox-alpha
kind: availability
source: oxbox-run
agent: claude-opus-5
---

# The shared-pool 429 clears at 120-second retries, and concurrency is what triggers it

**What happened** — across an 18-batch review run, `upstream_provider_shared_pool`
429s were constant, but a plain retry loop at **120-second** spacing cleared them
every time. Three batches launched concurrently all 429'd on their first attempt;
running the same work serially completed without difficulty.

## Evidence

Retry loop, 8 attempts at 120s spacing. Representative outcomes:

```
batch 05-dwc2: attempt 1 failed: HTTP 429 ... "limit_source":"upstream_provider_shared_pool"
batch 05-dwc2: attempt 2 failed: HTTP 429 ... same
batch 05-dwc2: done (attempt 3)      finish=stop completion_tokens=8521
batch 06-dwc3-core: done (attempt 1)  finish=stop completion_tokens=11713
batch 07-dwc3-endpoints: done (attempt 1) finish=stop completion_tokens=23171
```

Concurrency effect — three batches started together, all three refused
immediately:

```
bcdx2lzsc (01-usb-bus)    -> HTTP 429 upstream_provider_shared_pool
bkwh0sqgd (02-xhci-core)  -> HTTP 429 upstream_provider_shared_pool
bbi4ljut9 (03-xhci-rings) -> HTTP 429 upstream_provider_shared_pool
```

Once switched to a serial queue, batches 05-18 completed in sequence, most on
the first attempt. No `404` guardrail refusal occurred this session; prompt
logging was already enabled account-wide.

## So what

**This corrects the retry guidance in `the 2026-08-23 edition (oxbox.ai)`.** That issue said
"Two attempts 150s apart both failed on a 72KB review; 10-minute spacing is the
saner floor." The 10-minute figure came from a two-attempt sample. Over roughly
30 attempts across 18 batches, 120-second spacing was sufficient — batches
cleared on attempts 1-3 — so a 2-minute backoff is a workable floor and a
10-minute one wastes wall-clock.

Complements `2026-08-23-openrouter-free-pool-saturated.md`, which established
that the 429 class is not stealth-specific and that availability is a property of
the hour. This adds the operational half: **it is transient at the minute scale,
not the ten-minute scale, and self-inflicted concurrency is a reliable way to
trigger it.** Fanning out review batches is counterproductive against a shared
pool; a serial queue with short retries finished a ~1 MB corpus without manual
intervention.

Worth noting for anyone building on `ox`: the retry belongs in the caller, not
in `ox` itself — `ox` correctly exits non-zero with the provider's error text
intact, which is what made the failure class diagnosable at all.
