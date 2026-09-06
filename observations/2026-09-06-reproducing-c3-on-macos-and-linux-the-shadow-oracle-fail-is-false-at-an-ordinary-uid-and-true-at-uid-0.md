<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

---
date: 2026-09-06
venue: local
model: "-"
kind: findings
source: manual
agent: claude-fable-5-1
corpus: oxbox-clean-control
reproduces: C3 of run 2026-09-06T21-30-07Z
---

# Reproducing C3 on macOS and Linux: the stat oracle's FAIL on /etc/shadow is false at an ordinary uid and true at uid 0, and uid 0 is not what makes the stat succeed

**What happened** — Two checkers split on finding C3 of the GLM-5.3 Flash
clean-control candidate run (Fable 5.1 CONFIRMED, Opus 5 REFUTED), so at the
editor's direction the finding was run instead of read. `jailtest.py` and the
`oxbox` launcher at `6302b12`, with `profiles/jail.sb`, were executed as
shipped on two hosts: argenta (macOS 25.6, seatbelt backend) and dev (Debian
13, kernel 6.12, bubblewrap 0.11 at `/usr/bin/bwrap`, Python 3.13.5). On dev
the scenario the finding describes was forced by pointing `HOME` at an empty
directory, so that `sensitive_paths()` finds nothing home-relative and
`OXBOX_EXISTING_PATHS` is exactly `/etc/shadow`; then the same run as root
via `sudo`; then, inside the same jail, a direct `stat` and `open` of
`/etc/shadow` at each uid.

| Host, uid, `EXISTING[0]` | fs read `/etc/shadow` | stat oracle | `open("/etc/shadow")` inside the jail | verdict of the oracle's FAIL |
|---|---|---|---|---|
| macOS, ordinary user, `~/.ssh` | not in the list on darwin | PASS (`PermissionError`) | n/a, no such file on macOS | no FAIL to judge |
| Linux, ordinary user, `~/.ssh` (real home) | PASS (`PermissionError`) | PASS (`FileNotFoundError`, home not bound in) | `PermissionError` | no FAIL to judge |
| Linux, ordinary user, `/etc/shadow` (forced) | PASS (`PermissionError`) | **FAIL** (`succeeded`), exit 1 | `PermissionError` | **false**: the file is unreadable, the jail holds |
| Linux, uid 0, `/etc/shadow` (forced) | skipped by the uid-0 rule | **FAIL** (`succeeded`), exit 1 | **readable**: 923 bytes, 34 lines, first field `root` | **true**: jailed code as root reads the host's shadow file |

`stat("/etc/shadow")` succeeded at both uids inside the jail, 923 bytes, so
uid 0 is not what makes the stat succeed; the read-only bind of `/etc` is.

## Evidence

Payload hashes on dev: `oxbox` `1578245294a5551d…`, `jailtest.py`
`68bc6a61b438bd6a…` (sha256, first 16 hex). Linux, forced, ordinary user
(`uid 1228600005`):

```
[PASS] fs read: /etc/shadow                    (PermissionError)
[FAIL] fs metadata: stat /etc/shadow (oracle)  (succeeded)
...
JAIL LEAKS: 1 of 8 probes failed
exit 1
```

Linux, forced, root:

```
[FAIL] fs metadata: stat /etc/shadow (oracle)  (succeeded)
[PASS] env: parent environment not inherited   (succeeded)
[FAIL] fs write: inside work dir               (PermissionError)
[PASS] fs read: inside work dir                (succeeded)
[SKIP] fs read: /etc/shadow (uid 0 bypasses the file permissions this probe tests; rerun as an ordinary user)
JAIL LEAKS: 2 of 7 probes failed
exit 1
```

and, inside the same jail as root:

```
uid 0
stat ok: 923 bytes
open: READABLE, 923 bytes, 34 lines; first field of line 1: root
```

macOS baseline (argenta), 12 of 12 probes pass; the oracle targets `~/.ssh`
and seatbelt denies the stat (`PermissionError`). `/etc/shadow` is excluded
from the list on darwin at `oxbox:105–106` and does not exist on the host.

## So what

**The facts each checker asserted are both true, and the finding's stated
cause is false.** Fable's mechanism holds at an ordinary uid: `/etc/shadow`
first in the list produces a FAIL on a jail that is holding, the false FAIL
that Gemini's G1 recorded on 2026-09-02. Opus's factual claim holds at uid 0:
the oracle's FAIL there reports a genuine exposure, because jailed code
running as root reads the host's `/etc/shadow` through the read-only bind of
`/etc`. And C3's own account, that uid 0 is what makes the stat succeed and
turns the oracle's FAIL false, is wrong on both counts: the stat succeeds at
any uid, and at uid 0 the FAIL is not false. Whether a finding whose stated
cause is wrong earns credit for pointing at a real inconsistency is the
editor's ruling, not this observation's; the observation is what the ruling
rests on.

**Two things this run exposed that were not the question.** Running oxbox as
root under `sudo` on dev, `fs write: inside work dir` FAILed with
`PermissionError` inside the bubblewrap jail, on a work directory owned by
the invoking user; the cause was not investigated and this row is not a
verdict on it. And the network probes on Linux raise `OSError` rather than
`ConnectionRefusedError` or a timeout, the `ENETUNREACH` of a fresh network
namespace, which is the collision L1 describes; the jail is holding, and the
probe cannot tell that from an offline host.

**Reproduce first.** Two capable checkers read the same lines and reached
opposite verdicts; four commands on the right host settled every factual
point in under a minute. The editor's direction on 2026-09-06 is that
reproduction is the default baseline for verifying a finding wherever the
failure scenario can be executed against the pin in a jail, and that reading
the source is the fallback, not the method. `observations/README.md` and the
generator skill now say so.

**Nobody told the models about the two platforms.** Neither the review prompt
nor the verification contract mentions macOS or Linux; the checkers learned
about seatbelt and bubblewrap only from the payload. C3's confusion is
partly a platform confusion, and a prompt that named both backends and asked
"on which platform?" would have cost a sentence.
