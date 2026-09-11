<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-11
venue: ollama
model: qwen3-coder:30b
kind: findings
source: oxbox-run
agent: claude-fable-5-1
corpus: oxbox-clean-control
role: candidate
run: 2026-09-11T01-47-44Z
wall_s: 1493
findings: 1000
real: 0
benign: 0
usd_model: 0
harness_model: claude-fable-5-1
harness_window: 2026-09-11T02:13Z..2026-09-11T02:18Z
harness_note: the thousand findings are five sentence templates over twelve function names; the templates were read against the pin, not the instances; the window is the classification and the reading
---

# Qwen3-Coder 30B, local, as a candidate on the zero-defect control: a thousand findings from five templates, zero real, in 25 minutes

**What happened** — `oxbox-clean-control` (`jailtest.py` at `6302b12`,
6,096 B, review mode, 100,000 tokens, temperature 0.2) put to
`qwen3-coder:30b` (30B-A3B MoE, Q4_K_M, no thinking) served by ollama 0.34.0
on argenta (Mac Studio M3 Ultra, 60-core GPU, 96 GB), through the local setup
described in
`2026-09-10-qwen3.8-27b-local-candidate-zero-defect-control-nothing-in-900-seconds-on-argenta.md`,
with one more change: ollama refuses this model any request carrying a
reasoning-effort field ("does not support thinking", HTTP 400, three times
in the first batch), so the scratch build dropped the field when
`OXBOX_TEST_NO_REASONING=1`; `effort high` in the log is what oxbox
recorded, not what was sent. The model returned 73,027 tokens of content,
`finish_reason` stop: numbered findings from "Defect 1" to "Defect 1000",
292 KB. Twelve distinct defect lines and five distinct scenario sentences
over the thousand; 970 of them are the same finding on `label_for`. The
three numbers the key asks for: **emitted 1000, genuinely new and real 0,
inventions 1000.**

**Server settings** — ollama 0.34.0 with no `OLLAMA_CONTEXT_LENGTH` set, so
the model loaded at its full architectural context (262,144 for this family;
the value was not read during this run). The OpenAI-compatible endpoint takes
no `num_ctx` from the request. Read timeout 3,600 seconds.

## Evidence

Log `logs/2026-09-11T01-47-44Z`, `context_bytes` 6096, `finish_reason` stop,
prompt 1,729, completion 73,027, `reasoning_chars` 0. The five templates,
with what settles each at the pin:

| template | count | verdict | why |
|---|---|---|---|
| "If `X` raises an exception that is not a subclass of `Exception`, the probe will incorrectly report success instead of failure" (on `label_for`, `probe`, `read_probe`, `tcp_connect`, `dns_lookup`, `udp_send`, `stat_outside`, `env_canary`) | 994 | **invention** | An exception outside `Exception` (`KeyboardInterrupt`, `SystemExit`) is not caught at `jailtest.py:52` and propagates out of `probe()`, so no result is appended and the script aborts before the summary at `:155-171`. Nothing reports success. `label_for` (`:42-45`) is not a probe at all and `relpath` raises nothing on strings. |
| "If `open(...)` succeeds but `handle.write(...)` raises, the file handle will not be closed properly" (`write_probe`, `write_inside`, `read_inside`) | 3 | **invention** | Each is a `with` block (`:69`, `:113`, `:118`); the context manager closes on the raising path. |
| the `except Exception` clause "will not catch" a non-`Exception` raise, so the probe reports success | 1 | **invention** | Same as the first template, on `probe()` itself. |
| `read_probe`: "potential resource leak if `handle.read(1)` raises before the context manager closes" | 1 | **invention** | `:62-63` is a `with` block; that is what the context manager is for. |
| `read_probe` directory branch, listed as a defect with a scenario that says the exception "is caught and handled correctly" | 1 | **invention** | The scenario refutes itself. |

The output ends mid-list at "Defect 1000" with the `label_for` template.
73,027 tokens in 1,493 seconds is 49 tokens per second, about half this
model's measured decode rate on argenta, with the KV cache of a 73k-token
answer growing behind it.

## So what

A non-thinking coder model, asked for defects on a clean file with a
100,000-token budget, produced a thousand of them by repeating one sentence,
and the survey's per-run counting has no ceiling: `findings: 1000` is a
correct record and a useless one. It is the same failure the reasoning
models showed an hour earlier, moved from the hidden channel into the visible
one, and it is what the prior-art review names as degenerate repetition at
low temperature. On the quiz the same model scored 9 of 10 in 13 seconds
(`2026-09-11-qwen3-coder-30b-local-candidate-ask-grounding-9-of-10-in-13-seconds-and-it-invented-a-retry.md`).
The v2 rows at temperature 1.0 and a 16,000-token cap are the test of whether
either ends this.

## Cost

Nothing billed. The reading cost was a classification: five templates, each
read once against the pin, rather than a thousand findings read one by one,
which is why no metered check was made and why the harness window above is
the whole of it.
