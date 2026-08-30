<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

# What the survey reads from ox's run logs

The contract between `oxbox` (which writes `logs/<stamp>/`) and this repo (which
reads them). It exists so oxbox's own docs can link here instead of restating a
consumer's internals — a field documented in two places drifts.

**Direction of the promise.** ox may add fields freely. Removing or renaming one
of the fields below, or changing its meaning, breaks a named survey tool.
Anything ox writes that is not listed here, the survey does not depend on.

## Run directories

`logs/<stamp>/`, where `<stamp>` is `strftime("%Y-%m-%dT%H-%M-%SZ")` — UTC, with
**dashes in the time, not colons**. The directory name is the run's identity and
the survey compares it as a plain string. See the watermark section; the shape
matters there.

| File | Read by | For |
|---|---|---|
| `status.json` | `usagereport.py` | which entry served the work, and what failed |
| `response.json` | `costcheck.py` | the model's own token accounting |
| `meta.json` | `costcheck.py` | model / venue / mode / context size |
| `request.json` | corpus verification, by hand | the exact payload that was sent |
| `reasoning.txt` | — | evidence in a failure; never parsed |

## status.json

- **`dry_run`** (bool) — the most load-bearing field here. A dry run writes a full
  directory and calls nobody; counting it inflates usage and reports a model as
  reachable on a request that never left. The survey counts only `dry_run: false`.
- **`ok`** (bool) and **`error`** (string or null) — a failure and its message,
  quoted in the weekly report.
- **`truncated`** (bool or null) — counted. Null means unknown and is fine.
- **`model`** (string) — the entry that actually answered.
- **`prompt_tokens`, `completion_tokens`, `reasoning_tokens`** (int) — summed per
  model; absent reads as zero.
- **`manifest`** — `path` and `sha256`. The survey reads the manifest back from
  `path` to list entries that were never reached, so it must be the file actually
  used.
- **`attempts`** (list) — the walk ox made through the manifest, in order. Each
  carries `venue` and `model`; a skipped one also carries **`skipped`**, a
  human-readable reason. The survey matches on the *presence* of `skipped`, never
  its wording, so the text may change freely. This list is what separates "never
  reached because it was skipped on cost" from "never reached because the rank
  above always worked" — two facts that argue in opposite directions.

## response.json

Under `usage`: `prompt_tokens`, `completion_tokens`,
`completion_tokens_details.reasoning_tokens`,
`prompt_tokens_details.cached_tokens`, `cost`.

A run with no `response.json` is read as a dry run when `status.dry_run` is set,
and as an incomplete run otherwise — so a genuine failure and a dry run are never
conflated.

## The watermark: logs/.oxsurvey-scraped.json

`usagereport.py --mark` writes this into each logs directory it has read.

```json
{
  "scraped_through": "2026-08-30T16-05-13Z",
  "scraped_through_iso": "2026-08-30T16:05:13",
  "scraped_from": "2026-08-24T00:00:00",
  "runs": 6,
  "contract": "..."
}
```

**`scraped_through` is a run directory name, not an ISO timestamp** — written in
the exact `%Y-%m-%dT%H-%M-%SZ` shape ox uses. This is load-bearing. A pruner
compares a directory name against it as a plain string (`dirname >
scraped_through`), and that is correct only when both sides share the shape. An
ISO watermark breaks it in the direction that destroys evidence: `-` is `0x2D`,
`:` is `0x3A`, so within the same hour every directory name sorts *below* an ISO
watermark and reads as already-scraped. `scraped_through_iso` is for humans; do
not compare against it.

The rule for any pruner, in three cases:

- **Absent** — no survey has read this directory; age alone governs.
- **Present and valid** — delete no run whose directory name sorts *above*
  `scraped_through`, whatever its age.
- **Present but unparseable** — prune nothing. An unreadable watermark says the
  survey's position is *unknown*, which is not zero. `--mark` writes atomically,
  so a reader sees the old file or the new one; that guards against a torn write
  by this writer, not against a hand-edit or a full disk, which is why a pruner
  must still fail closed.

## Retention

Keep runs **at least 14 days** — two survey cycles, so one missed cycle cannot
destroy the next one's input. The stronger reason is that a *failed* run's logs
are evidence existing nowhere else (an empty-content abort strands the whole
answer in `reasoning.txt`), where a successful run can be reproduced by running
again. `OXBOX_LOG_RETENTION_DAYS` is the reserved name for that knob (days, `0`
meaning keep everything); nothing prunes automatically today.
