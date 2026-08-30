<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

# corpora/

The targets side of the survey. `manifests/` says which model to call; this says
what to send it.

`corpus-manifest.json` pins a repository at a commit, an exact file list, and the
exact prompt text. Two models given the same task id get a byte-identical payload,
so the difference in what comes back is theirs and not the corpus's. That is the
whole point: the strongest observation in this repo so far —
[leanstral vs Ox Alpha](../observations/2026-08-24-leanstral-review-same-file-zero-real-findings.md)
— worked because it happened to be the same file, same prompt, same mode. This
directory makes that the default instead of a lucky accident, and retires the
generator's standing caveat that the Observed tier has "no fixed corpus".

**It is a fixture set, not a benchmark.** There is deliberately no expected-findings
key. A run against a task id still produces an observation a human wrote after
reading every finding against the source; nothing here scores a model on its own.

## Shape

```jsonc
{
  "corpus_version": 0,              // int, bump only on a breaking shape change
  "defaults": { ... },              // params a task inherits unless it overrides
  "projects": [{
    "id": "oxbox",
    "url": "...", "license": "...", "visibility": "public",
    "visibility": "public",         // the hard rule; verified, never assumed
    "visibility_verified": "2026-08-30",
    "commit": "<40 hex>",           // what a task's files are read from
    "commit_verified": "2026-08-30",// the day someone checked the SHA resolves; null if not
    "why": "...",                   // why this project is in the set at all
    "tasks": [{
      "id": "oxbox-review-queue",   // stable, globally unique, quoted in observations
      "mode": "review",             // review | diff | ask — ox's three modes
      "files": [...],               // repo-relative, in the order ox receives them
      "bytes": 22910,               // sum at the pin; must equal ox's meta.json context_bytes
      "commit": "<40 hex>",         // optional: overrides the project pin for this task
      "prompt": "corpora/prompts/oxbox-review-queue.txt",
      "answer_key": null,           // corpora/answers/<id>.md; required unless human-scored
      "params": {...},
      "status": "active",           // active | proposed | blocked | retired
      "verification": "human",      // human | git-apply | json-parse | answer-key
      "evidence": [...]             // observations produced from this fixture
    }]
  }]
}
```

`verification` is the field worth reading twice. `human` means someone reads every
finding against the source — the only judgement the survey trusts for review
quality, and the reason there are so few runs. The other three are mechanical, and
the tasks that carry them are the cheap ones to add: `oxbox-secret-scanner-fix` is
scored by `git apply --check` plus eight measured pattern verdicts, with nobody
reading the patch.

Anything not scored by a human needs an **answer key** in `corpora/answers/<task
id>.md`, written before the run. It states the acceptance criteria, how they were
measured, and what a near-miss looks like. Writing one afterwards, having seen the
output, turns a fixture into a post-hoc opinion; the test requires the file to
exist for any task scored `git-apply`, `json-parse` or `answer-key`.

A task may override its project's `commit`. `oxbox-clean-control` does: it sits one
commit *later* than the batch that found its only defect, because the point of that
fixture is a file with nothing left to find.

## Running a task

Check the project out at its pin, then feed the prompt file on stdin:

```bash
git -C /path/to/oxbox checkout 6072d56
ox --mode review --stdin \
   --files .claude/skills/ox-review/scripts/oxreview.py,jailtest.py \
   --max-tokens 100000 --temperature 0.2 --effort high \
   --manifest /path/to/oxbox-survey/manifests/oxbox-manifest-2026-08-29.json \
   < /path/to/oxbox-survey/corpora/prompts/oxbox-review-queue.txt
```

Then check `meta.json` in the run's log dir: `context_bytes` must equal the task's
`bytes`. If it does not, the payload is not the fixture and the run is not
comparable to anything.

Record the result in `observations/` as usual, with one added frontmatter field:

```yaml
corpus: oxbox-review-queue
```

The field is optional — an observation about a venue or a one-off is not a corpus
run — but when present it must name a task id that exists here. `surveytest.py`
enforces that.

Then measure what it cost, both halves, and paste the table into the observation:

```bash
python3 costcheck.py --run /path/to/oxbox/logs/<run> \
    --session <session uuid> --from <window start> --to <window end>
```

The model's tokens are the cheap half. The expensive half is reading every finding
against the pin, and a fixture only tells you whether a free model is worth using
once both are on the page.

## Rules

- **Prompt files are payload, not documents.** No SPDX header, no editorial
  comment, no trailing note — every byte is sent to the model. The first two
  prompts were extracted verbatim from `request.json` in the run they reproduce,
  not written afterwards from memory.
- **A prompt must not trip ox's own secret scanner.** `build_context` scans the
  task text exactly as it scans file bodies, and exits 2 on a hit, so a fixture
  that spells out a credential-shaped string is unrunnable — or worse, runnable
  under one ox version and refused by another. `oxbox-secret-scanner-fix` writes
  its samples as `client_secret=<20 chars, unquoted>` for this reason.
- **Dry-run a fixture before committing it.** `ox --dry-run` builds the payload,
  runs the scanner, and sends nothing. It prints `context=NB`, which must equal
  the task's `bytes`. All five active fixtures were checked this way.
- **A task with `evidence` is frozen.** Changing its files, prompt or pin silently
  breaks the comparison to every run already recorded against it. Add a new task
  id instead and mark the old one `retired`.
- **Public code only**, the same rule as the rest of the pipeline. `visibility`
  is a field so the check is a lookup rather than a recollection, and a project
  that is not public does not belong here at all.
- **Read a target's source at a committed ref, never from a working tree you do
  not control.** `git show <sha>:<path>`, not `cat /path/in/their/checkout`. A
  checkout is somebody's workbench and is allowed to be broken at any instant:
  on 2026-08-30 the oxbox tree briefly held deliberately-broken copies of `ox`
  so a new regression test could be proved to fail, and a check run against it
  in that window was measuring bytes that were about to be restored. See
  `observations/2026-08-30-never-reached-had-a-mechanical-cause.md`.
- **Verify against the pin, never the working tree.** The 2026-08-29 minimax run
  is the standing example: two of its real findings were fixed within the hour,
  and the fixed files carry comments describing the bug that was fixed, so a
  verifier reading HEAD scores both as false positives. Two verdicts in that
  observation were reversed by going back to the payload.
- **`bytes` is a checksum, not a description.** It must equal the sum of the file
  sizes at the pin, which is what ox reports as `context_bytes`.
- **Not dated per issue.** Unlike `manifests/`, a corpus changes when a target
  moves, not weekly. Edit this file in place and bump nothing but `updated`.

## Not runnable yet

**OCR and any other image input.** `ox` builds `messages[].content` as a plain
string (`ox:781-783`) — there is no content-parts array, no `image_url`, no
attachment path — so a vision task cannot be sent through the containment at all
today. It would need an ox change, plus a decision about whether an image counts
as "public code only", plus an `input_modalities` column in the snapshot, since
nothing in the catalog currently records which free models even accept an image.
Until then the runnable neighbour is text-shaped: hand a model already-extracted
messy text and ask for a structured table, which measures extraction fidelity with
no ox change at all.
