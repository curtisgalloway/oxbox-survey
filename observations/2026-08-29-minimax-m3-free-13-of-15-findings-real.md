<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-08-29
venue: openrouter
model: minimax/minimax-m3:free
kind: findings
source: oxbox-run
agent: claude-opus-5
---

# MiniMax M3 free: 13 of 15 findings real across two review batches, and two of them were fixed within the hour

**What happened** — two `--mode review` batches over four Python files in
oxbox (645 and ~700 lines), run through the 2026-08-27 survey manifest. Fifteen
findings; thirteen hold up against the source as it was sent. Two of the real
ones were serious enough to be fixed in oxbox 16 minutes after the run.

## The runs

| Log dir | Files | Prompt | Completion | Finish |
|---|---|---|---|---|
| `2026-08-30T01-11-26Z` | `.claude/skills/ox-review/scripts/oxreview.py`, `jailtest.py` | 5,668 | 33,914 | stop |
| `2026-08-30T01-14-28Z` | `.claude/skills/ox-review/scripts/exposure.py`, `.claude/skills/ox-review/scripts/preflight.py` | 7,037 | 18,312 | stop |

Both used `--manifest manifests/oxbox-manifest-2026-08-27.json`
(sha256 `92cfb2ba…`), entry position 2, `ox_version` 0.2.0, `truncated: false`.

## Batch B — oxreview.py, jailtest.py

| # | Finding | Verdict |
|---|---|---|
| 1 | Stale-lock break spins forever when debris blocks `rmdir`; `wait_timeout` is never consulted on that path | **real**, fixed in oxbox `626db7a` |
| 2 | `status.json` from a previous attempt can be read as the current attempt's status, so the retry decision uses the wrong error | **real**, still open |
| 3 | `tcp_connect` / `udp_send` skip `sock.close()` on the raising path | **real**, trivial; the model said so itself |
| 4 | The `OSError` branch breaks before appending to `record["attempts"]`, leaving `"attempts": []` | **real**, fixed in oxbox `626db7a` |
| 5 | `record.get("expires_at", 0)` returns `None` for an explicit JSON null, and `_expired`'s `except` does not catch `TypeError` | **real**, self-labeled UNCERTAIN |

Five for five. It also wrote a "Not bugs (noted for completeness)" section whose
four entries all check out, including the dead `REPO_ROOT` and `write_probe` in
`jailtest.py`.

Finding 1 is the headline. The code as sent unlinked `holder.json`, called
`self.path.rmdir()`, swallowed both errors, and `continue`d — bypassing the sleep
and the `wait_timeout` check, so a leftover `holder.<pid>.tmp` from a killed run
wedges every later batch at full CPU. The commit that landed 16 minutes later is
titled "oxreview: a stale lock with debris in it spun the queue forever" and its
comment records the reproduction: 82MB of log in 20 seconds against a 5-second
`--wait-timeout`.

## Batch A — exposure.py, preflight.py

| # | Finding | Verdict |
|---|---|---|
| 1 | Bare `except Exception` in `fetch()` reports `MemoryError` and friends as "probe failed" | **real**, minor |
| 2 | `probe_anonymous_clone` does not URL-encode `owner`/`name`; `probe_provider_api` does | inconsistency **real**; the stated mechanism is **wrong** — an `@` in the path cannot move the host |
| 3 | Conditional-expression-in-tuple in the `HTTPError` return | **not a defect**, and the model says so: "Confirmed correctness today; flagged because the current form is a tripwire" |
| 4 | `subprocess.run(ox --version)` has no `timeout=` and no `try` | **real** |
| 5 | An empty remote URL yields a confident `not-public` verdict and the note "nothing here is published" | **real** |
| 6 | `ahead != "0"` string compare instead of `int(ahead) > 0` | **false positive** — the scenario invents a git that pads counts |
| 7 | `parse_remote` drops the port, so the clone probe hits 443 on a `:8443` host | **real** |
| 8 | `ox --version` return code ignored, stderr folded into stdout and reported as the version | **real** |
| 9 | An explicit `--ox` that does not exist is silently overridden by `$OX`/`$PATH` | **real**, self-labeled UNCERTAIN |
| 10 | TOCTOU between `read_bytes()` and `stat()` in `describe_manifest` | true, negligible; the `except` returns, so nothing crashes |

Eight real, one correctly labeled as not-a-defect, one false positive, one true
but not worth fixing.

## Verify against the code that was sent, not the working tree

Both fixed findings first read as false positives, because the current file
contains the fix *and a comment describing the bug that was fixed*. The payload
in `logs/<run>/request.json` is the only correct reference. Two verdicts in this
file were reversed by checking it.

## So what

This is the first `source: oxbox-run` evidence for any model in the free tier,
and it is a better result than the survey's previous best: Ox Alpha's 63
findings at 72% in issue 0.2, against 13 of 15 here. It is also a much smaller
sample — two prompts, four files, one repo, all Python — and the two batches
were not a matched comparison against anything.
