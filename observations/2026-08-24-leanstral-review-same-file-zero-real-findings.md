<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-08-24
venue: requesty
model: mistral/leanstral-1-5
kind: findings
source: oxbox-run
agent: claude-opus-5
---

# leanstral on the same file: 6 findings, 0 real defects, 1 factually wrong

**What happened** — identical file, identical prompt, identical mode as
[[2026-08-24-ox-alpha-found-a-real-credential-leak]]. A controlled comparison,
which is the thing the earlier attribution note failed to be.

## Scorecard

Six numbered findings. **Four are titled `BUG:` in the heading and then
concluded to be non-defects in the body** — "Verdict: Not a defect", "No actual
defect here", "No defect". Anyone skimming headings sees five bugs.

| # | Claim | Verdict |
|---|---|---|
| 1 | `--base-url` lacks URL validation | raised, then self-resolved as "intentional design" |
| 2 | `--api-key-env` can pair any variable with any URL — "the primary defect" | not a code defect; it is the documented escape hatch. See below. |
| 3 | env var not checked before URL selection | self-resolved: "error is caught before request is sent" |
| 4 | `--api-key-env ""` bypasses the guard | **factually wrong** |
| 5 | `KeyError` on `VENUES["custom"]` | self-resolved: "This is correct" |
| 6 | no URL allowlist | restatement of #2 with a third verdict |

**#4 is wrong on Python semantics.** It claims `if not args.api_key_env` is
falsy for `""` and the empty string passes the check. `not ""` is `True`, so the
guard fires. Verified:

```
$ ox --base-url https://evil.example/v1 --api-key-env "" --model m --dry-run t
ox: --base-url requires --api-key-env, so a key is never sent to an unlisted host by accident
```

**#1, #2 and #6 are one observation with three different verdicts** — "not a
defect", "the primary defect", and "design limitation, not a concrete code
defect". It never reconciles them.

It found **none** of the four real defects on the same file: the redirect
credential leak, the missing URL validation, the empty-choices `IndexError`, or
the log-stamp collision.

Cost: 3708 prompt tokens, 1627 completion, **0 reasoning**, about one minute.

## So what

The one thing worth keeping from it: #2 pushes on whether the invariant is
*enforced* or merely *documented* for the escape-hatch path, and it is right
that the code relies on the operator there. That is a real observation about the
strength of a claim, arrived at three times with three verdicts, so it is hard to
credit as a finding.

**Ten times cheaper and fifteen times faster than Ox Alpha, and it produced
nothing actionable on the same input.** Token efficiency (axis 5) is worth
points only when the output is worth reading; here the cheap answer had a
negative value, because acting on #4 would mean "fixing" a guard that already
works. The efficiency profile that made leanstral attractive in
[[2026-08-23-requesty-chat-completions-no-deposit]] does not transfer to review
quality, and nothing in the catalog could have predicted that.
