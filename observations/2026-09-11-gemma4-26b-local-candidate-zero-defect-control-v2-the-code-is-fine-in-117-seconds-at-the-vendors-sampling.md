<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-11
venue: ollama
model: gemma4:26b
kind: findings
source: oxbox-run
agent: claude-fable-5-1
corpus: oxbox-clean-control-v2
role: candidate
run: 2026-09-11T02-13-25Z
wall_s: 117
findings: 0
real: 0
usd_model: 0
usd_total: 0
---

# Gemma 4 26B, local, on the zero-defect control at the v2 parameters: "The code is fine." in 117 seconds

**What happened** — `oxbox-clean-control-v2` (`jailtest.py` at `6302b12`,
6,096 B, review mode, **effort medium, 16,000 tokens, temperature 1.0**) put
to `gemma4:26b` through its `gemma4:26b-64k` tag (`num_ctx` 65,536, same
blobs) served by ollama 0.34.0 on argenta (Mac Studio M3 Ultra, 60-core GPU,
96 GB), through the local setup described in
`2026-09-10-qwen3.8-27b-local-candidate-zero-defect-control-nothing-in-900-seconds-on-argenta.md`.
The whole answer: "The code is fine." 10,683 completion tokens, 37,154
characters of reasoning, `finish_reason` stop, 117 seconds. The same model on
the same file at the v1 parameters
(`2026-09-10-gemma4-26b-local-candidate-zero-defect-control-spent-its-whole-cap-looping-and-returned-nothing-in-21-minutes.md`)
spent 100,000 tokens reasoning in a loop and returned nothing in 1,279
seconds. The three numbers the key asks for: **emitted 0, real 0, inventions
0**, the answer the key calls the best possible result, and the first time a
local model has given it.

**Server settings** — `num_ctx` 65,536 from the tag's Modelfile, over the
server's default of the model's full 262,144. Read timeout 3,600 seconds.
The request carried `reasoning: {effort: "medium"}`; whether ollama forwards
effort to this family is an open upstream question (ollama #18121), and the
reasoning volume, 37k characters against 352k at the cap, says something
changed, but three settings changed at once and this run does not say which.

## Evidence

Log `logs/2026-09-11T02-13-25Z`, `context_bytes` 6096, `finish_reason` stop,
prompt 1,969, completion 10,683, `message.content` "The code is fine." The
reasoning (37,154 characters, read in full) opens by tabulating the file:
purpose, the environment variables, the `probe()` truth table. It then
circles the places the record's inventions live, `isdir` in `read_probe` (33
mentions), `EXISTING[0]` and the stat oracle (72 mentions of `stat`), the
socket timeouts (12), `write_probe` (4), and near the end twice says "Wait! I
found one very small thing" and dismisses it in the next line ("it's a test
script, not a production kernel"; "This is correct."). It ends "I'm
confident." It never names either real defect the file carries at this pin
(the record's G1 and L1) as a defect, though it looked at both places, so
this is the ideal answer on the invention axis and a miss on both known
defects, the same shape as DeepSeek V4 Flash's 2026-09-02 baseline and
Nemotron 3.5 Lightning's 2026-09-08 run.

## So what

Same model, same file, same hardware, and the only difference is the
parameters the prior-art review said to change: temperature 1.0 as the
vendor's card sets it, effort medium, and a 16,000-token cap. Twenty-one
minutes and nothing became two minutes and the right answer. A single run
does not settle which of the three did it, and the review says the cap
alone would have ended the loop without producing an answer, so the
sampling is the likeliest cause. What it does settle is that the v1
exhaustions were a property of the settings as much as of the model, which
is what the record now has to say beside every v1 row.

## Cost

Nothing billed. On a fixture that expects nothing, an answered run with no
findings has no cost denominator and scores as a dash; that is by the round
11 ruling, and it is the point.
