<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-11
venue: opencode
model: big-pickle
kind: efficiency
source: probe
agent: claude-opus-5
---

# The OpenCode client spends 12k-27k input tokens before the payload

**What happened** — a six-word prompt through `opencode run` bills 26,925 input
tokens on the default agent. A custom agent with every tool switched off brings
that to 12,509 plus 9,728 read from cache. The remainder is the client's own
system prompt, and it rides on every request whatever the task is.

## Evidence

Same prompt, same model, same empty working directory; only the agent changed.

```
$ opencode run --dir <empty> -m opencode/big-pickle --format json "Reply with exactly the word: pong"
  tokens: {total 28721, input 26925, output 4, reasoning 0, cache{write 0, read 1792}}

$ opencode run --dir <empty> --agent toolless -m opencode/big-pickle --format json "say pong"
  tokens: {total 22275, input 12509, output 38, reasoning 0, cache{write 0, read 9728}}
```

The `toolless` agent is `.opencode/agent/toolless.md`, frontmatter `mode:
primary` and `tools:` with `bash`, `edit`, `write`, `read`, `glob`, `grep`,
`list`, `patch`, `todowrite`, `todoread`, `webfetch` and `task` each `false`.

Two other facts from the same session, both about the default agent rather than
the models:

- `opencode agent list` shows the default `build` agent carrying
  `{"permission": "*", "action": "allow", "pattern": "*"}`. Tools are
  auto-approved. Omitting `--auto` does not change this, which is the opposite
  of the `agy` arm in `verifiercheck.py`, where headless mode auto-*denies* the
  `command` permission and that is what makes the arm toolless.
- `--format json` emits a `step_finish` event carrying `tokens` -- input,
  output, reasoning, and cache read and write -- plus `cost`. So unlike the
  `claude` and `agy` arms, a client arm here can be priced.

## So what

This is the number that decides whether OpenCode can be an arm at all, and it
cuts both ways.

In its favor: the token accounting exists. `verifiercheck.py` states the flaw in
its two CLI arms plainly -- "a subscription CLI reports no tokens -- agy
publishes none at all -- so the arms below it can be compared for accuracy and
not for cost, which is the wrong way round for a question that is entirely about
cost." A client arm here does not have that flaw.

Against it: the payload is not the whole world, and the survey's toolless arms
are built on the premise that it is. Twelve thousand tokens of someone else's
system prompt sit between the fixture and the model, they are not in the
archived request, and they are not what an `oxbox send` run of the same fixture
sends. On a free listing this costs no money, but it spends context window and
it makes any finding attributable to the client as much as to the model. That
is the rule `verifiercheck.py` already names -- an arm is a model and a harness,
and the pair is what gets measured -- arriving here with a number on it.

The permission default is the other half. An empty working directory is not
containment when the agent has `bash` and approves its own use of it; the empty
directory works for `agy` only because that harness denies first.

## Cost

Zero on the model side: free-tier calls, `cost: 0` on each. The measurement is
the client's own reported token counts, quoted above.
