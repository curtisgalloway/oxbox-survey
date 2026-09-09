#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Curtis Galloway
# SPDX-License-Identifier: Apache-2.0
"""Generate an issue in two passes, from archived inputs, under a named model.

The generator is a skill, so until now "which model wrote the issue" meant
"which model the editor happened to be running". That cannot be compared, and a
prose change cannot be attributed. This runs the same generation twice or three
times over the same archived snapshot and observations, one arm per model and
effort level, and records what each one produced.

Two passes, because one pass writing prose while holding every source in
context is what produces the density this is trying to fix:

  content   Runs in the repository. Reads the snapshot for a date, the
            observations newer than the previous issue, and `ratings.py
            --json`. Emits a structured intermediate: facts, never sentences.
  prose     Runs in an EMPTY working directory with the file tools withheld,
            and is handed nothing but the intermediate and the writing rules.
            It cannot add a detail back in because it cannot see one. Without
            that boundary a second pass re-densifies instead of clarifying.

The empty working directory is the same enforcement verifiercheck.py uses to
keep a toolless arm toolless. It is the mechanism, not a convention.

Every call records `modelUsage` from the CLI's JSON output. That names the
model that actually answered, which matters because Fable routes queries its
safeguard classifiers flag to Opus, and --fallback-model does the same on a
flagged request. Either can mix two models inside one run and surface as
inconsistent voice. More than one key in `modelUsage` means the run was not
uniform, and the arm is reported as MIXED rather than quietly averaged.

    python3 scripts/generate_issue.py --list
    python3 scripts/generate_issue.py --arm fable-high --date 2026-09-01 --dry-run
    python3 scripts/generate_issue.py --arm fable-high --date 2026-09-01
    python3 scripts/generate_issue.py --arm all --date 2026-09-01 --out work/ab

Nothing here writes into the editions repository. Output lands under --out for
comparison with `scripts/prose_metrics.py`; publishing stays a human step.
"""

import argparse
import contextlib
import io
import json
import os
import re
import subprocess
import sys
import time
from concurrent import futures
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
SKILL = HERE / ".claude" / "skills" / "oxbox-survey" / "SKILL.md"
SHAPE = HERE / "docs" / "issue-shape.md"

# The second-level headings of an issue, verbatim and in order. They mirror the
# "### " entries under "The sections, in order" in docs/issue-shape.md, minus the
# three that are not headings (title and byline, the two-sentence block, the
# opening paragraph). surveytest.py checks the two lists against each other.
#
# Listed here as well as in the spec because the 2.6.0 run, handed only a
# pointer to the spec, paraphrased every name it could not see: "New this week"
# for "What's new this week", "Caveats" for "How far to trust this", and put
# the models before the lessons. A writer that cannot open the file has to be
# given the words.
SECTIONS = [
    "Editor's notes",
    "What's new this week",
    "Top things we learned",
    "Top models to try",
    "What a review cost",
    "The models",
    "The stealth models",
    "What models changed since the last issue",
    "How far to trust this",
    "Sources",
]

# One entry per model-and-effort combination to compare. `effort` is the CLI's
# --effort flag. Fable's thinking is always on and cannot be switched off, so
# effort is the only lever on that model; Opus is here as the other model
# rather than as another effort level.
ARMS = {
    "fable-high": {
        "model": "claude-fable-5-1",
        "effort": "high",
        "note": "the current baseline: what has written every issue so far",
    },
    "fable-low": {
        "model": "claude-fable-5-1",
        "effort": "low",
        "note": "same model, reduced effort. Adaptive thinking stays on either "
                "way -- it cannot be turned off, so this is the only lever Fable "
                "has",
    },
    "opus-5": {
        "model": "claude-opus-5",
        "effort": "high",
        "note": "the other model, at the same effort as the baseline",
    },
    # Not a comparison arm. It exists so the harness itself -- the flags, the
    # JSON envelope, the empty-cwd boundary -- can be exercised for cents
    # before an arm that costs dollars is launched.
    "smoke": {
        "model": "claude-haiku-4-5",
        "effort": "low",
        "note": "harness self-test only; never compare prose from this arm",
    },
    # PROSE ONLY, through the Codex CLI. `claude -p` runs Claude models, so a
    # cross-vendor arm needs a different driver; `codex exec` is headless, and
    # the editor's subscription covers it.
    #
    # Prose-only is a choice about scope, not a limitation of Codex -- it could
    # run the content pass perfectly well. Holding it to the prose pass keeps
    # the comparison clean: with --intermediate every arm writes from the same
    # facts, so the writer is the only variable. Gathering the facts is not
    # what this experiment is measuring.
    #
    # Worth having because the other three arms are two Claude models, which
    # cannot tell a portable writing rule from a Claude-shaped one.
    "astra": {
        "model": "gpt-6-astra",
        "effort": "high",
        "via": "codex",
        "prose_only": True,
        "cost_basis": "subscription",
        "note": "cross-vendor prose arm through the Codex CLI, covered by the "
                "editor's subscription; needs --intermediate",
    },
}

# Withheld from the prose pass. The empty working directory already leaves it
# nothing to read; naming the tools as well means a slip shows up as a refusal
# rather than as a quietly better-informed paragraph.
PROSE_DENIED = ["Read", "Glob", "Grep", "Bash", "WebFetch", "WebSearch",
                "Edit", "Write", "Task", "NotebookEdit"]

CONTENT_PROMPT = """\
You are the content pass of the Oxbox Survey generator. You are NOT writing the
issue. Another pass writes it, and that pass will see nothing but the file you
produce, so anything you leave out is gone.

Read, in this order:

1. `.claude/skills/oxbox-survey/SKILL.md` -- the generator's rules. Follow the
   evidence-tier rules and the honesty rules exactly. Ignore the "How to write
   it" section; that governs the prose pass, not you.
2. The newest snapshot at or before {date} under `snapshots/`, and the one
   before it, so churn is a diff and not a memory.
3. Every file in `observations/` dated after the previous issue.
4. `providers/*.md` for standing venue facts.
5. The output of `python3 ratings.py --json` and `python3 ratings.py --costs`.

Emit ONE JSON object and nothing else. No prose, no markdown fence, no
commentary before or after.

Rules for what goes in it:

- Every leaf is a FACT, not a sentence. "20 of 27 findings verified real" is a
  fact. "MiniMax M3 performed impressively" is a sentence, and a judgment, and
  does not belong here.
- Every fact carries its evidence tier ("measured", "observed", "reported") and,
  where one exists, the observation filename or snapshot date behind it.
- Numbers stay numbers. Do not round, do not convert to prose, do not
  editorialize a comparison into a leaf.
- If a value is missing it is null and a sibling `note` says why. Never
  interpolate.

SELECT. Do not gather everything you can find. Read the section "What the report
is for, and what earns a place in it" in SKILL.md and apply it here, because
selection happens in this pass and cannot be undone later -- the prose pass sees
only what you emit, so anything you include WILL be printed.

Apply the test to every candidate fact: what does a reader do differently
because this is here? The reader is deciding whether to point a cheap model at
their code this week. They are not auditing how the survey reached its numbers.

- Prefer the five operational axes: access, usable output, verification burden,
  what changed, and one inspectable incident told properly.
- Leave out the survey's own adjudication, its methodology defenses, its process
  and tooling notes, and anything unchanged since the last issue.
- A highlight earns its place by changing a decision, not by having happened.
- One incident with its reproduction and its consequence beats twenty tallied.

Include the standing regulatory caveat, the churn list and the sources, which
are required every issue. The generator review is required too and goes to
`docs/generator-reviews/`, never into the issue.

The keys below are the sections of `docs/issue-shape.md`, in the order the
issue prints them, and the caps are that file's caps: at most five
highlights, five lessons, four top models. Selection is yours. The prose pass
prints what it is given and cannot trim, so a sixth highlight here is a sixth
highlight in the issue.

- `lead` is the ONE fact that most changes what a reader does this week, with
  its number. It becomes the opening paragraph. Pick it; do not leave it to
  the writer, who cannot see what it was chosen over.
- `highlights` is what changed in the world ("What's new this week").
- `lessons` is what a reader has to do about it ("Top things we learned"):
  what broke, the workaround that was necessary, the flag that had to be set.
  This is the operational half of the survey and the section nobody else
  writes. Every lesson names the observation file it came from.

Shape (extend where the week needs it; never drop a key):

{{
  "issue_date": "{date}",
  "generator_version": "<from SKILL.md frontmatter>",
  "lead":         {{"fact": ..., "number": ..., "tier": ..., "source": ...}},
  "highlights":   [{{"claim": ..., "why_it_matters": ..., "facts": [...],
                     "tier": ..., "links": [...]}}],
  "lessons":      [{{"lesson": ..., "what_broke": ..., "what_to_do": ...,
                     "facts": [...], "tier": ..., "observation_file": ...}}],
  "top_models":   [{{"id": ..., "venue": ..., "price": ..., "stats": [...],
                     "facts": [...], "rating": ..., "links": [...]}}],
  "costs":        {{"numbers": [...], "checking_model": ..., "reading": [...],
                     "workbook_link": ...}}],
  "catalog":      {{"venues": [...], "rows": [...]}},
  "stealth":      [...],
  "churn":        {{"added": [...], "delisted": [...], "repriced": [...],
                     "revealed": [...]}},
  "caveats":      [...],
  "sources":      [{{"title": ..., "url": ..., "used_for": ...}}],
  "tried":        [{{"model": ..., "counts": {{...}}, "observation_file": ...}}],
  "generator_review": {{"triggers_fired": [...], "proposed_edits": [...]}}
}}

`tried` is the record behind `top_models` and `lessons`, kept so a number can
be traced; it is not a section of its own.
"""

PROSE_PROMPT = """\
You are the prose pass of the Oxbox Survey generator. Write one issue in
Markdown from the facts below, and do nothing else.

You cannot see the snapshot, the observations, the run logs or the repository.
That is deliberate. Everything you are allowed to state is in the JSON below.
Do not add a fact, a number, a comparison, a hedge or an example that is not
there. If something reads as though it needs one more detail, it does not get
one -- write around it, or say plainly that the record does not say.

Do not drop anything either. Every fact in the JSON appears in the issue.

=== THE WRITING RULES (follow these exactly) ===

{rules}

=== THE SHAPE OF THE ISSUE (authoritative; this is the format) ===

{shape}

=== THE HEADINGS ===

The second-level headings are exactly these, in exactly this order, with
exactly these words:

{headings}

Add none. Rename none. Do not promote "What this is" or the opening paragraph
to a heading; the shape above says where they go. Leave "Editor's notes" in
place with nothing under it. Omit a heading only where the shape says the
section folds into another or reduces to one line, and say so in that line.

=== STANDING RULES FOR PARTICULAR SECTIONS ===

{format_block}

=== THE FACTS ===

{intermediate}

Write the issue now. Output only the Markdown.
"""


def extract_section(text, heading):
    """Pull one '## heading' section out of SKILL.md."""
    pat = re.compile(r"^## %s\s*$" % re.escape(heading), re.M)
    m = pat.search(text)
    if not m:
        raise SystemExit("generate_issue: no '## %s' section in SKILL.md" % heading)
    rest = text[m.end():]
    nxt = re.search(r"^## ", rest, re.M)
    return rest[:nxt.start()].strip() if nxt else rest.strip()


def run_cli(arm, prompt, cwd, deny_tools, timeout, dry_run, mode="manual"):
    """One non-interactive CLI call.

    The two passes need opposite permission postures. The content pass has to
    read the snapshot, the observations and ratings.py output, so it runs in
    `auto`. The prose pass must read nothing at all, so it runs in `manual`
    with prompts answered by nobody, every file and network tool named in
    --disallowed-tools, and an empty working directory underneath. Three
    independent barriers, because the isolation is the point of the split and
    one flag is one point of failure."""
    cmd = [
        "claude", "-p",
        "--model", arm["model"],
        "--effort", arm["effort"],
        "--output-format", "json",
        "--permission-mode", mode,
    ]
    if mode == "manual":
        cmd += ["--permission-prompts", "none"]
    if deny_tools:
        cmd += ["--disallowed-tools"] + deny_tools
    if dry_run:
        print("  cwd: %s" % cwd)
        print("  cmd: %s" % " ".join(cmd))
        print("  prompt: %d bytes" % len(prompt))
        return None
    started = time.time()
    proc = subprocess.run(cmd, input=prompt, cwd=str(cwd), capture_output=True,
                          text=True, timeout=timeout, check=False)
    elapsed = round(time.time() - started, 1)
    if proc.returncode != 0:
        sys.stderr.write("generate_issue: exit=%d\n%s\n"
                         % (proc.returncode, proc.stderr[-2000:]))
        return None
    try:
        envelope = json.loads(proc.stdout)
    except ValueError:
        sys.stderr.write("generate_issue: CLI did not return JSON\n")
        return None
    envelope["_elapsed_s"] = elapsed
    return envelope


CODEX_SESSIONS = Path.home() / ".codex" / "sessions"


def codex_model_from_rollout(thread_id):
    """The model that actually answered, read back from the session rollout.

    `codex exec --json` does not name the model anywhere in its event stream --
    turn.completed carries token counts and nothing else -- so the requested
    model and the responding model cannot be compared from stdout alone. The
    rollout file records it, and its filename carries the thread id, which is
    why these runs are not --ephemeral. Returns None rather than guessing; an
    unverified model is reported as unverified, not assumed to be the one asked
    for."""
    if not thread_id:
        return None
    for path in CODEX_SESSIONS.rglob("rollout-*%s.jsonl" % thread_id):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        found = re.findall(r'"model"\s*:\s*"([^"]+)"', text)
        if found:
            return sorted(set(found))
    return None


def _rollout_paths(thread_id):
    if not thread_id:
        return []
    return sorted(CODEX_SESSIONS.rglob("rollout-*%s.jsonl" % thread_id))


def codex_last_message_from_rollout(thread_id):
    """The reply text, from the rollout's task_complete event."""
    for path in _rollout_paths(thread_id):
        found = None
        try:
            handle = path.open(encoding="utf-8", errors="replace")
        except OSError:
            continue
        with handle:
            for line in handle:
                try:
                    d = json.loads(line)
                except ValueError:
                    continue
                q = d.get("payload", d)
                if (q.get("type") or d.get("type")) == "task_complete":
                    found = q.get("last_agent_message") or found
        if found:
            return found
    return None


def run_codex(arm, prompt, stem, timeout, dry_run):
    """One headless Codex call, for a cross-vendor prose arm.

    Isolation matches the Claude prose pass: the working root is an empty
    directory and the sandbox is read-only, so there is nothing to read even if
    the model reaches for a tool.

    Cost is deliberately None. The run is covered by a subscription, which
    means unmetered rather than free, and writing 0 into the cost column would
    state a price nobody was charged. `astra-metered` exists to answer the
    price question with a bill."""
    out_dir = Path(stem).parent
    empty = out_dir / "empty-cwd"
    empty.mkdir(parents=True, exist_ok=True)
    last = str(stem) + ".last.txt"
    cmd = [
        "codex", "exec", "--json",
        "--model", arm["model"],
        "--skip-git-repo-check",
        "--sandbox", "read-only",
        "--cd", str(empty.resolve()),
        "--output-last-message", last,
        "-",
    ]
    if dry_run:
        print("  cwd: %s" % empty)
        print("  cmd: %s" % " ".join(cmd))
        print("  prompt: %d bytes" % len(prompt))
        return None
    started = time.time()
    proc = subprocess.run(cmd, input=prompt, cwd=str(empty), capture_output=True,
                          text=True, timeout=timeout, check=False)
    elapsed = round(time.time() - started, 1)
    if proc.returncode != 0:
        Path(str(stem) + ".stderr.txt").write_text(proc.stderr, encoding="utf-8")
        sys.stderr.write("generate_issue: codex exit=%d, stderr kept\n"
                         % proc.returncode)
        return None
    thread_id, usage = None, {}
    for line in proc.stdout.splitlines():
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        if ev.get("type") == "thread.started":
            thread_id = ev.get("thread_id")
        elif ev.get("type") == "turn.completed":
            usage = ev.get("usage") or {}
    models = codex_model_from_rollout(thread_id)
    answer = Path(last).read_text(encoding="utf-8") if os.path.exists(last) else ""
    if not answer.strip():
        # --output-last-message wrote nothing even though the turn completed and
        # billed 22K output tokens (observed 2026-09-08, codex-cli 0.153.4). The
        # rollout has the reply on the task_complete event, so read it back
        # rather than lose an eleven minute run to a missing file.
        answer = codex_last_message_from_rollout(thread_id) or ""
        if answer:
            sys.stderr.write("generate_issue: --output-last-message was empty; "
                             "recovered the reply from the session rollout\n")
    return {
        "result": answer,
        "modelUsage": {m: {} for m in (models or [])},
        "total_cost_usd": None,
        "_elapsed_s": elapsed,
        "_usage": usage,
        "_thread_id": thread_id,
        "_model_verified": bool(models),
    }


def responding_models(envelope):
    """Which model actually answered. More than one means the run mixed two,
    which is what a safeguard reroute or a --fallback-model hit looks like."""
    usage = envelope.get("modelUsage") or {}
    return sorted(usage.keys())


def strip_fence(text):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n", "", text)
        text = re.sub(r"\n```\s*$", "", text)
    return text.strip()


def extract_json(text):
    """The outermost JSON object in a reply, or None.

    The content pass is told to emit one object and nothing else, and a capable
    model still opens with a sentence ("I have all the inputs. Emitting the
    intermediate.") and wraps the object in a fence. Both are cosmetic and
    neither is worth re-running a twenty-eight minute pass over, so find the
    object rather than insisting the whole reply parse. Brace matching, string
    aware, so a brace inside a quoted value does not close the object early."""
    fenced = re.search(r"```(?:json)?\s*\n(.*?)\n```", text, re.S)
    candidates = [fenced.group(1)] if fenced else []
    candidates.append(text)
    for blob in candidates:
        start = blob.find("{")
        if start < 0:
            continue
        depth, in_str, esc = 0, False, False
        for i in range(start, len(blob)):
            ch = blob[i]
            if in_str:
                if esc:
                    esc = False
                elif ch == "\\":
                    esc = True
                elif ch == '"':
                    in_str = False
                continue
            if ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(blob[start:i + 1])
                    except ValueError:
                        break
    return None


def generate(arm_name, arm, date, out_dir, timeout, dry_run, only=None,
             shared=None):
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = out_dir / ("%s-%s" % (date, arm_name))
    skill_text = SKILL.read_text(encoding="utf-8")
    record = {"arm": arm_name, "model_requested": arm["model"],
              "effort": arm["effort"], "date": date, "passes": {}}
    # The two passes are commonly run in separate invocations -- a content pass
    # today and a prose pass when a model's credits reset -- so carry forward
    # whatever an earlier run recorded instead of overwriting it with a file
    # that describes only the pass that just happened.
    prior = Path(str(stem) + ".meta.json")
    if prior.exists():
        try:
            record["passes"] = json.loads(
                prior.read_text(encoding="utf-8")).get("passes", {})
        except ValueError:
            pass

    if arm.get("prose_only") and only != "prose":
        only = "prose"
        if not shared:
            sys.stderr.write(
                "generate_issue: arm=%s is prose-only and needs --intermediate; "
                "ox gives a model no tools, so it cannot run the content pass\n"
                % arm_name)
            return None

    # An arm that ran its own content pass is comparable to the published
    # issue but NOT to another arm: two intermediates differ, so a prose
    # difference is confounded with a content difference. --intermediate holds
    # the facts fixed and leaves the writer as the only variable.
    inter_path = Path(shared) if shared else Path(str(stem) + ".intermediate.json")
    record["intermediate"] = str(inter_path)
    record["intermediate_shared"] = bool(shared)
    if shared and only in (None, "content"):
        only = "prose"
    if only in (None, "content"):
        print("[%s] content pass" % arm_name)
        env = run_cli(arm, CONTENT_PROMPT.format(date=date), HERE, None,
                      timeout, dry_run, mode="auto")
        if dry_run:
            pass
        elif env is None:
            return None
        else:
            body = strip_fence(env.get("result", ""))
            obj = extract_json(body)
            # Always keep the raw reply, not only on failure: it is the record
            # of what the pass actually said, and a preamble the extractor
            # discarded may be the explanation for a thin intermediate.
            Path(str(stem) + ".content.raw.txt").write_text(body,
                                                            encoding="utf-8")
            if obj is None:
                sys.stderr.write("generate_issue: content pass produced no JSON; "
                                 "raw kept at %s.content.raw.txt\n" % stem)
                return None
            body = json.dumps(obj, indent=1) + "\n"
            inter_path.write_text(body, encoding="utf-8")
            record["passes"]["content"] = {
                "responding_models": responding_models(env),
                "cost_usd": env.get("total_cost_usd"),
                "elapsed_s": env.get("_elapsed_s"),
                "bytes": len(body),
            }

    if only in (None, "prose"):
        print("[%s] prose pass" % arm_name)
        empty = out_dir / "empty-cwd"
        empty.mkdir(exist_ok=True)
        intermediate = (inter_path.read_text(encoding="utf-8")
                        if inter_path.exists() else "{}")
        # The shape is handed over whole. The skill's format block is a
        # pointer to docs/issue-shape.md, and the prose pass, by design, has
        # no file to follow a pointer to; the 2.6.0 run showed what a writer
        # does with a pointer it cannot open.
        prompt = PROSE_PROMPT.format(
            rules=extract_section(skill_text, "How to write it"),
            shape=SHAPE.read_text(encoding="utf-8"),
            headings="\n".join("%d. ## %s" % (i + 1, h)
                               for i, h in enumerate(SECTIONS)),
            format_block=extract_section(skill_text, "Report format"),
            intermediate=intermediate,
        )
        if arm.get("via") == "codex":
            env = run_codex(arm, prompt, str(stem), timeout, dry_run)
        else:
            env = run_cli(arm, prompt, empty, PROSE_DENIED, timeout, dry_run,
                          mode="manual")
        if dry_run:
            return None
        if env is None:
            return None
        issue = strip_fence(env.get("result", ""))
        Path(str(stem) + ".issue.md").write_text(issue, encoding="utf-8")
        record["passes"]["prose"] = {
            "responding_models": responding_models(env),
            "cost_usd": env.get("total_cost_usd"),
            "cost_basis": arm.get("cost_basis", "metered"),
            "model_verified": env.get("_model_verified", True),
            "tokens": env.get("_usage"),
            "elapsed_s": env.get("_elapsed_s"),
            "bytes": len(issue),
        }

    seen = set()
    for p in record["passes"].values():
        seen.update(p["responding_models"])
    record["responding_models_all"] = sorted(seen)
    record["uniform"] = len(seen) <= 1
    # Recorded because the CLI hands it over, not because it is the question.
    # None where the run was covered by a subscription; never 0, which would
    # state a price nobody was charged.
    priced = [p.get("cost_usd") for p in record["passes"].values()]
    record["cost_usd_total"] = (None if any(c is None for c in priced)
                                else round(sum(priced), 4))
    Path(str(stem) + ".meta.json").write_text(
        json.dumps(record, indent=1) + "\n", encoding="utf-8")
    if not record["uniform"]:
        sys.stderr.write(
            "generate_issue: arm=%s MIXED -- more than one model answered: %s\n"
            % (arm_name, ", ".join(record["responding_models_all"])))
    return record


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--arm", default="fable-high",
                   help="one of %s, or 'all'" % ", ".join(ARMS))
    p.add_argument("--date", help="issue date, e.g. 2026-09-01")
    p.add_argument("--out", default="work/generated", help="output directory")
    p.add_argument("--pass", dest="only", choices=["content", "prose"],
                   help="run only one pass (default: both)")
    p.add_argument("--intermediate",
                   help="reuse this intermediate instead of running the content "
                        "pass. Holds the facts fixed so the writer is the only "
                        "variable, which is what makes two arms' prose "
                        "comparable. Required by a prose-only arm.")
    p.add_argument("--timeout", type=int, default=3600, help="seconds per pass")
    p.add_argument("--jobs", type=int,
                   help="arms to run at once (default: all of them). Use 1 to "
                        "serialize, or 2 when two arms share one model's rate "
                        "limit and would throttle each other.")
    p.add_argument("--dry-run", action="store_true",
                   help="print the commands and prompt sizes, call nothing")
    p.add_argument("--list", action="store_true", help="show the arms")
    args = p.parse_args(argv)

    if args.list:
        for name, arm in ARMS.items():
            print("%-12s %-20s effort=%-5s %s"
                  % (name, arm["model"], arm["effort"], arm["note"]))
        return 0
    if not args.date:
        p.error("--date is required")

    names = list(ARMS) if args.arm == "all" else [args.arm]
    for name in names:
        if name not in ARMS:
            p.error("unknown arm %r; --list shows them" % name)

    out_dir = Path(args.out)
    results = []

    # Arms are independent: each reads the same intermediate read-only and
    # writes its own stem, so nothing serializes them but the loop. Running
    # them together turns four arms from four wall clocks into one. A dry run
    # stays serial so its printed commands do not interleave.
    jobs = 1 if (args.dry_run or len(names) == 1) else (args.jobs or len(names))
    if jobs > 1:
        print("running %d arms in parallel" % len(names))
        buffers = {}

        def work(name):
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                r = generate(name, ARMS[name], args.date, out_dir, args.timeout,
                             args.dry_run, args.only, args.intermediate)
            buffers[name] = buf.getvalue()
            return r

        with futures.ThreadPoolExecutor(max_workers=jobs) as pool:
            for name, r in zip(names, pool.map(work, names)):
                sys.stdout.write(buffers.get(name, ""))
                if r:
                    results.append(r)
    else:
        for name in names:
            r = generate(name, ARMS[name], args.date, out_dir, args.timeout,
                         args.dry_run, args.only, args.intermediate)
            if r:
                results.append(r)

    if results:
        print("\n| arm | responding model | uniform | cost USD | seconds |")
        print("|---|---|---|---|---|")
        for r in results:
            secs = sum(p.get("elapsed_s") or 0 for p in r["passes"].values())
            cost = ("unmetered" if r["cost_usd_total"] is None
                    else "%.4f" % r["cost_usd_total"])
            models = ", ".join(r["responding_models_all"]) or "unverified"
            print("| %s | %s | %s | %s | %.0f |"
                  % (r["arm"], models,
                     "yes" if r["uniform"] else "NO -- MIXED", cost, secs))
    return 0


if __name__ == "__main__":
    sys.exit(main())
