#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Curtis Galloway
# SPDX-License-Identifier: Apache-2.0
"""Offline tests for oxsurvey and for the repo's own evidence discipline.

Two jobs:

1. **The fetcher.** Each venue adapter is exercised against a recorded fixture
   of that venue's real catalog shape, so a parser change that silently drops
   the free tier fails here rather than in a committed snapshot. The diff and
   trigger logic run against synthetic pairs.

2. **The discipline.** The rules this repo asserts in prose -- a class B `free`
   is null and never false, an observation carries the frontmatter its README
   defines, `source: probe` never claims a USE -- are checked mechanically.
   A rule that lives only in a README is a hope.

No network and no API key: every fixture is inline. Python 3.9 floor, matching
oxsurvey itself.
"""

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
FAILURES = []
PASSES = 0


def report(ok, label, note=""):
    global PASSES
    if ok:
        PASSES += 1
        print("[PASS] %s" % label)
    else:
        FAILURES.append(label)
        print("[FAIL] %s%s" % (label, ("  (%s)" % note) if note else ""))


def load_oxsurvey():
    source = (HERE / "oxsurvey").read_text(encoding="utf-8")
    source = source.replace('if __name__ == "__main__":', "if False:")
    # oxsurvey resolves SNAPSHOT_DIR from __file__, which exec() does not supply.
    namespace = {"__name__": "oxsurveymod", "__file__": str(HERE / "oxsurvey")}
    exec(compile(source, str(HERE / "oxsurvey"), "exec"), namespace)
    return namespace


# --------------------------------------------------------------------------
# Fixtures: the shape each venue actually returns, trimmed to what matters.
# Recorded from live catalogs on 2026-08-24.
# --------------------------------------------------------------------------

OPENROUTER_FIXTURE = {"data": [
    {"id": "free/model", "canonical_slug": "free/model", "name": "Free",
     "created": 1787000000, "context_length": 1000000,
     "pricing": {"prompt": "0", "completion": "0"},
     "top_provider": {"context_length": 256000, "max_completion_tokens": 8192,
                      "is_moderated": False},
     "architecture": {"input_modalities": ["text"], "output_modalities": ["text"]},
     "supported_parameters": ["tools", "response_format"]},
    {"id": "stealth/codename", "canonical_slug": "stealth/codename", "name": "Codename",
     "created": 1787100000, "context_length": 1048576,
     "pricing": {"prompt": "0", "completion": "0"},
     "top_provider": {"context_length": 1048576}, "architecture": {},
     "expiration_date": "2098-12-31"},
    {"id": "paid/model", "pricing": {"prompt": "0.0000012", "completion": "0.000005"},
     "top_provider": {}, "architecture": {}},
    # Zero per-token but priced per request: NOT free.
    {"id": "request/priced", "pricing": {"prompt": "0", "completion": "0", "request": "0.01"},
     "top_provider": {}, "architecture": {}},
]}

ZENMUX_FIXTURE = {"data": [
    {"id": "vendor/free-one", "display_name": "Free One", "created": 1787200000,
     "context_length": 1000000, "input_modalities": ["text"],
     "output_modalities": ["text"], "publish_time": "2026-08-21",
     "pricings": {"prompt": [{"value": 0, "unit": "perMTokens"}],
                  "completion": [{"value": 0, "unit": "perMTokens"}]}},
    {"id": "vendor/paid", "display_name": "Paid", "context_length": 200000,
     "pricings": {"prompt": [{"value": 1.4, "unit": "perMTokens"}],
                  "completion": [{"value": 4.4, "unit": "perMTokens"}]}},
]}

REQUESTY_FIXTURE = {"data": [
    {"id": "lab/free", "model_canonical_name": "free", "created": 1787300000,
     "context_window": 262144, "max_output_tokens": 8192,
     "input_price": 0, "output_price": 0,
     "pricing": [{"prompt_tokens_threshold": 0, "input_price": 0, "output_price": 0}],
     "supports_tool_calling": True, "supports_reasoning": True,
     "supports_output_json_schema": True,
     "data_used_for_training": False, "data_retention_days": 0},
    # Free below a threshold, priced above it: NOT free.
    {"id": "lab/tiered", "context_window": 100,
     "pricing": [{"prompt_tokens_threshold": 0, "input_price": 0, "output_price": 0},
                 {"prompt_tokens_threshold": 32000, "input_price": 1.5, "output_price": 3.0}]},
    {"id": "lab/paid", "context_window": 100,
     "pricing": [{"prompt_tokens_threshold": 0, "input_price": 2, "output_price": 4}]},
]}

OPENCODE_FIXTURE = {"data": [
    {"id": "big-pickle", "object": "model", "created": 1787400000, "owned_by": "opencode"},
    {"id": "some-model-free", "object": "model", "created": 1787400001, "owned_by": "opencode"},
]}


def test_adapters(ox):
    print("=== venue adapters ===")

    rows = ox["parse_openrouter"](OPENROUTER_FIXTURE)
    free = [r for r in rows if r["free"]]
    report(sorted(r["id"] for r in free) == ["free/model", "stealth/codename"],
           "openrouter: zero-priced models are free",
           sorted(r["id"] for r in free))
    report(not [r for r in rows if r["id"] == "request/priced"][0]["free"],
           "openrouter: a request-priced model is not free even at zero per-token")
    row = [r for r in rows if r["id"] == "free/model"][0]
    report(row["context_length"] == 1000000 and row["endpoint_context_length"] == 256000,
           "openrouter: advertised and endpoint context are kept apart")
    report([r for r in rows if r["id"] == "stealth/codename"][0]["is_stealth"] is True
           and row["is_stealth"] is False,
           "openrouter: the stealth/ prefix marks cloaked listings")

    rows = ox["parse_zenmux"](ZENMUX_FIXTURE)
    free = [r for r in rows if r["free"]]
    report([r["id"] for r in free] == ["vendor/free-one"],
           "zenmux: nested list-shaped pricing is parsed",
           [r["id"] for r in free])
    report(free[0]["expiration_date"] is None,
           "zenmux: publish_time does not masquerade as an expiration date")
    report(all(r["is_stealth"] is None for r in rows),
           "zenmux: is_stealth is null, not false — the venue does not mark them")

    rows = ox["parse_requesty"](REQUESTY_FIXTURE)
    free = [r for r in rows if r["free"]]
    report([r["id"] for r in free] == ["lab/free"],
           "requesty: free only when EVERY pricing tier is zero",
           [r["id"] for r in free])
    report(free[0]["trains_on_input"] is False and free[0]["data_retention_days"] == 0,
           "requesty: data terms are captured as fields")
    report(free[0]["supported_parameters"] == ["reasoning", "response_format", "tools"],
           "requesty: supports_* booleans map into the common vocabulary",
           free[0]["supported_parameters"])

    rows = ox["parse_openai_roster"](OPENCODE_FIXTURE)
    report(all(r["free"] is None for r in rows),
           "class B: free is None — unknown, never false")
    report(all(r["trains_on_input"] is None for r in rows),
           "class B: unsupplied fields are None, not invented")


def test_snapshot_shape(ox):
    print("\n=== snapshot shape ===")
    for name, spec in sorted(ox["VENUES"].items()):
        report(spec["pricing_class"] in ("A", "B"), "%s declares a pricing class" % name)
        report(spec["url"].startswith("https://"), "%s catalog URL is https" % name)
        report((spec["roster_scope"] == "free-only") == (spec["pricing_class"] == "A"),
               "%s roster scope matches its class" % name)


def test_diff_and_triggers(ox):
    print("\n=== diff and triggers ===")

    def snap(models, venue="openrouter", stealth=0):
        return {"venue": venue, "models": models, "stealth_count": stealth,
                "pricing_class": "A", "roster_scope": "free-only"}

    # Carries a stealth entry so T7 (empty stealth tier) stays quiet and the
    # unchanged case is genuinely silent.
    base = [{"id": "a", "free": True, "is_stealth": False, "expiration_date": None},
            {"id": "b", "free": True, "is_stealth": False, "expiration_date": None},
            {"id": "s", "free": True, "is_stealth": True, "expiration_date": None}]

    findings, triggers = ox["diff"](snap(base), snap(base))
    report(not findings and not triggers,
           "an unchanged catalog reports nothing", (findings, triggers))

    # T7 is a signal, not noise: a stealth-free catalog two weeks running is
    # exactly what it exists to flag.
    quiet = [{"id": "a", "free": True, "is_stealth": False, "expiration_date": None}]
    _, triggers = ox["diff"](snap(quiet), snap(quiet))
    report(any(t.startswith("T7") for t in triggers),
           "T7 fires when the stealth tier is empty on a venue that marks them")

    after = [dict(base[0]), dict(base[2]),
             {"id": "stealth/new", "free": True, "is_stealth": True, "expiration_date": None}]
    findings, triggers = ox["diff"](snap(base), snap(after))
    kinds = [f[0] for f in findings]
    report(kinds.count("DELISTED") == 1 and "ADDED" in kinds,
           "added and delisted entries are both reported", kinds)
    report(any(t.startswith("T1") for t in triggers), "T1 fires on a new stealth listing")
    report(not any(t.startswith("T4") for t in triggers),
           "T4 stays quiet on a single delisting")
    two_gone = [dict(base[2])]
    _, triggers2 = ox["diff"](snap(base), snap(two_gone))
    report(any(t.startswith("T4") for t in triggers2), "T4 fires on two delistings")

    repriced = [dict(base[0], free=False)] + base[1:]
    findings, triggers = ox["diff"](snap(base), snap(repriced))
    report(any(t.startswith("T9") for t in triggers), "T9 fires when free status changes")

    expiring = [dict(base[0], expiration_date="2026-10-01")] + base[1:]
    findings, triggers = ox["diff"](snap(base), snap(expiring))
    report(any(t.startswith("T9") for t in triggers),
           "T9 fires when a deprecation date appears")

    # T7 must not claim an empty stealth tier the records contradict, and must
    # stay silent where the venue does not mark cloaked listings at all.
    header_lies = snap([dict(base[0], is_stealth=True)], stealth=0)
    _, triggers = ox["diff"](header_lies, header_lies)
    report(not any(t.startswith("T7") for t in triggers),
           "T7 recomputes from records, ignoring a stale header")

    unmarked = snap([{"id": "x", "free": None, "is_stealth": None, "expiration_date": None}],
                    venue="opencode")
    _, triggers = ox["diff"](unmarked, unmarked)
    report(not any(t.startswith("T7") for t in triggers),
           "T7 stays silent on a venue that does not mark cloaked listings")


def test_cli():
    print("\n=== cli behavior ===")
    survey = str(HERE / "oxsurvey")

    result = subprocess.run([sys.executable, survey, "--list-venues"],
                            capture_output=True, text=True, timeout=60)
    report(result.returncode == 0 and "class A" in result.stdout and "class B" in result.stdout,
           "--list-venues prints both classes")

    tmp = Path(tempfile.mkdtemp(prefix="surveytest-"))
    a = tmp / "a.json"
    b = tmp / "b.json"
    a.write_text(json.dumps({"venue": "openrouter", "models": [], "stealth_count": 0}))
    b.write_text(json.dumps({"venue": "zenmux", "models": [], "stealth_count": 0}))
    result = subprocess.run([sys.executable, survey, "--diff", str(a), str(b)],
                            capture_output=True, text=True, timeout=60)
    report(result.returncode == 2 and "refusing to diff across venues" in result.stderr,
           "--diff refuses to compare different venues", result.stderr[:80])


def test_access_probe(ox):
    print("\n=== access probe ===")
    cases = [
        ((200, "", "OK"), "ok", "a 200 with content is ok"),
        ((200, "", ""), "empty_content",
         "a 200 with empty content is a failure, not an empty answer"),
        ((200, "", None), "empty_content", "a 200 with null content is empty_content"),
        ((402, '{"type":"reject_no_credit"}', None), "no_credit",
         "402 reject_no_credit is recognised"),
        ((403, "your account must have a balance greater than $0", None), "no_credit",
         "a balance message is no_credit even behind another status"),
        ((429, "rate limited upstream", None), "rate_limited", "429 is rate_limited"),
        ((401, "", None), "unauthorized", "401 is unauthorized"),
        ((403, "forbidden", None), "unauthorized", "403 is unauthorized"),
        ((404, "", None), "not_found", "404 is not_found"),
        ((503, "", None), "upstream_error", "503 is upstream_error"),
        ((500, "", None), "upstream_error", "500 is upstream_error"),
        ((418, "", None), "error", "an unmapped status falls through to error"),
    ]
    for (status, body, content), expected, label in cases:
        got = ox["classify"](status, body, content)
        report(got == expected, label, "got %r, want %r" % (got, expected))

    # The tripwire scorer: four verdicts, no human, one request.
    tripwire_cases = [
        ("5", "correct", "the bare defect line is correct"),
        ("5.", "correct", "a trailing period still parses"),
        ("**5**", "correct", "bold markers are stripped"),
        ("```\n5\n```", "correct", "a fenced answer still parses"),
        ("Found it:\n5\n", "correct", "a numbers-only line is found among prose"),
        ("5,5", "correct", "a repeated number is not an overcall"),
        ("5, 6", "overcalled", "naming the trap alongside the defect is an overcall"),
        ("6", "missed", "naming only the trap is a miss"),
        ("1", "missed", "naming an innocent line is a miss"),
        ("Line 5 is the defect", "malformed", "prose alone does not follow the contract"),
        ("", "malformed", "an empty reply is malformed"),
    ]
    for reply, expected, label in tripwire_cases:
        got, _ = ox["score_tripwire"](reply)
        report(got == expected, label, "got %r, want %r" % (got, expected))

    # The fixture has to still plant the defect it claims. Run it: as written it
    # must disagree with its own docstring, and changing ONLY the defect line
    # must make it agree -- which is also the proof that the trap line is not a
    # second defect. Edit the snippet and this fails before the screen ships a
    # wrong answer key.
    source = "\n".join(line[4:] for line in ox["TRIPWIRE_CODE"].splitlines())
    lines = source.splitlines()
    defect = ox["TRIPWIRE_DEFECT_LINE"] - 1
    fixed_source = "\n".join(
        lines[:defect] + [lines[defect].replace("i <= n", "i < n")] + lines[defect + 1:])
    cases = [([1, 2, 3], 2), ([1, 2, 3], 0), ([1, 2, 3], 5), ([], 2), ([9], 1)]

    def disagreements(text, tag):
        """Where this version parts company with its own docstring.

        A raise counts as a disagreement rather than an abort: a fixture that
        blows up is a broken fixture, and it must fail here as a named check
        instead of taking the rest of the suite down with it.
        """
        namespace = {}
        try:
            exec(compile(text, tag, "exec"), namespace)
        except Exception as error:                       # noqa: BLE001
            return ["%s: will not compile (%s)" % (tag, error)]
        out = []
        for items, n in cases:
            try:
                got = namespace["take"](items, n)
            except Exception as error:                   # noqa: BLE001
                out.append("take(%r, %r) raised %s" % (items, n, error))
                continue
            if got != items[:n]:
                out.append("take(%r, %r) -> %r" % (items, n, got))
        return out

    broken = disagreements(source, "<tripwire>")
    still_broken = disagreements(fixed_source, "<tripwire-fixed>")
    report(broken, "the planted defect is real: the snippet disagrees with its "
                   "docstring", broken)
    report(not still_broken,
           "changing only the defect line fixes it, so the trap line is not a "
           "second defect", still_broken)
    report(ox["TRIPWIRE_TRAP_LINE"] != ox["TRIPWIRE_DEFECT_LINE"]
           and "len(items)" in lines[ox["TRIPWIRE_TRAP_LINE"] - 1],
           "the trap line is where the fixture says it is")

    # A model that could not be reached has no capability verdict. Recording a
    # 429 as "missed" would turn an outage into a claim about the model.
    # A verdict nobody can re-score is an assertion, not evidence.
    report(ox["summarize_reply"]("line 5\n\n  is   wrong") == "line 5 is wrong",
           "a recorded reply is flattened to one line")
    long_reply = "5 " + "x" * 500
    kept = ox["summarize_reply"](long_reply)
    report(len(kept) <= ox["TRIPWIRE_REPLY_CHARS"] + 6 and kept.endswith("[...]")
           and kept.startswith("5 "),
           "a long reply is trimmed and marked, keeping its opening", len(kept))
    try:
        blank = ox["summarize_reply"](None) == "" and ox["summarize_reply"]("") == ""
    except Exception:                                     # noqa: BLE001
        blank = False
    report(blank, "no reply summarises to empty rather than crashing")

    try:
        empty = ox["score_tripwire"](None) == ("malformed", [])
    except Exception:                                     # noqa: BLE001
        empty = False
    report(empty, "no content scores malformed rather than crashing")

    # Every venue must be probeable at all: a chat endpoint and a key variable.
    for name, spec in sorted(ox["VENUES"].items()):
        report(spec.get("chat_url", "").startswith("https://")
               and bool(spec.get("key_env")),
               "%s declares a probeable chat endpoint and key variable" % name)


def test_tier_separation():
    print("\n=== probe results stay out of the catalog ===")
    import glob
    catalogs = [p for p in glob.glob("snapshots/*/*.json") if not p.endswith("-access.json")]
    access = glob.glob("snapshots/*/*-access.json")

    # The whole point of the separate file: a catalog snapshot records what the
    # venue published, an access file records what happened when we called it.
    # Merging them would blur Measured into Observed.
    leaked = []
    for path in catalogs:
        data = json.loads(open(path, encoding="utf-8").read())
        if "results" in data or any("access" in m for m in data.get("models", [])):
            leaked.append(path)
    report(not leaked, "no catalog snapshot carries probe results", leaked)

    bad = []
    for path in access:
        data = json.loads(open(path, encoding="utf-8").read())
        if data.get("tier") != "observed":
            bad.append("%s: tier is %r" % (path, data.get("tier")))
        if "models" in data:
            bad.append("%s: carries a catalog model list" % path)
        for row in data.get("results", []):
            if row.get("access") not in ("ok", "empty_content", "no_credit",
                                         "rate_limited", "unauthorized",
                                         "not_found", "upstream_error", "error"):
                bad.append("%s: unknown access %r" % (path, row.get("access")))
            if "tripwire" in row:
                if row["tripwire"] not in (None, "correct", "overcalled",
                                           "missed", "malformed"):
                    bad.append("%s: unknown tripwire %r" % (path, row["tripwire"]))
                # A capability verdict on a call that never landed would read as
                # a fact about the model instead of about the hour.
                if row.get("access") != "ok" and row["tripwire"] is not None:
                    bad.append("%s: %s scored %r without a reply"
                               % (path, row.get("id"), row["tripwire"]))
    report(not bad, "every access file declares tier=observed and known verdicts", bad)


def test_corpus():
    print("\n=== the corpus manifest ===")
    path = HERE / "corpora" / "corpus-manifest.json"
    report(path.exists(), "a corpus manifest is committed", str(path))
    if not path.exists():
        return
    data = json.loads(path.read_text(encoding="utf-8"))

    version = data.get("corpus_version")
    report(isinstance(version, int) and version <= 0,
           "corpus_version is an int at or below the current shape", version)

    modes = {"review", "diff", "ask"}          # ox's SYSTEM_PROMPTS keys
    statuses = {"active", "proposed", "blocked", "retired"}
    checks = {"human", "git-apply", "json-parse", "answer-key"}

    tasks = {}
    problems = []
    for project in data.get("projects", []):
        pid = project.get("id", "?")
        for field in ("url", "license", "visibility", "visibility_verified",
                      "commit", "commit_verified", "why", "tasks"):
            if field not in project:
                problems.append("%s: missing %s" % (pid, field))
        # Public code only is the pipeline's rule, not a preference; a target
        # that is not public has no business being reachable from a fixture.
        if project.get("visibility") != "public":
            problems.append("%s: visibility %r" % (pid, project.get("visibility")))
        # A verified pin must be a full SHA -- a short one is ambiguous the day
        # the target repository grows into the collision.
        if project.get("commit_verified") and not re.match(
                r"^[0-9a-f]{40}$", project.get("commit") or ""):
            problems.append("%s: commit_verified but the pin is not a full SHA" % pid)
        for task in project.get("tasks", []):
            tid = task.get("id")
            if tid in tasks:
                problems.append("duplicate task id %r" % tid)
            tasks[tid] = task
            if task.get("mode") not in modes:
                problems.append("%s: unknown mode %r" % (tid, task.get("mode")))
            if task.get("status") not in statuses:
                problems.append("%s: unknown status %r" % (tid, task.get("status")))
            if task.get("verification") not in checks:
                problems.append("%s: unknown verification %r"
                                % (tid, task.get("verification")))
            # A task may pin a different commit from its project -- the clean
            # control sits one commit later than the batch that found its
            # defect -- and the override is held to the same standard.
            if task.get("commit_verified") and not re.match(
                    r"^[0-9a-f]{40}$", task.get("commit") or ""):
                problems.append("%s: commit_verified but the pin is not a full SHA"
                                % tid)
            if task.get("status") == "active":
                if not project.get("visibility_verified"):
                    problems.append("%s: active task in a project whose visibility "
                                    "was never verified" % tid)
                if not (task.get("commit_verified") or project.get("commit_verified")):
                    problems.append("%s: active task with an unverified pin" % tid)
    report(not problems, "every corpus entry declares a known shape", problems[:4])

    # An active task is one a run can be reproduced from today, so it has to
    # carry all three halves of the payload: the pin's files, their size, and
    # the prompt as sent.
    incomplete = []
    for tid, task in tasks.items():
        if task.get("status") != "active":
            continue
        if not task.get("files"):
            incomplete.append("%s: no files" % tid)
        if not isinstance(task.get("bytes"), int):
            incomplete.append("%s: bytes is not an int" % tid)
        prompt = task.get("prompt")
        if not prompt:
            incomplete.append("%s: no prompt" % tid)
        elif not (HERE / prompt).exists():
            incomplete.append("%s: prompt %s is missing" % (tid, prompt))
        # A mechanically scored task is only scoreable if the criteria are
        # written down. Reconstructing them after seeing the output is how a
        # fixture turns into a post-hoc opinion.
        if task.get("verification") in ("git-apply", "answer-key", "json-parse"):
            key = task.get("answer_key")
            if not key:
                incomplete.append("%s: %s scoring with no answer key"
                                  % (tid, task.get("verification")))
            elif not (HERE / key).exists():
                incomplete.append("%s: answer key %s is missing" % (tid, key))
        # A scorer is a claim that a script applies the key; the script must exist.
        if task.get("scorer") and not (HERE / task["scorer"]).exists():
            incomplete.append("%s: scorer %s is missing" % (tid, task["scorer"]))
    report(not incomplete, "every active task can be reproduced", incomplete)
    report(tasks.get("oxbox-ask-grounding", {}).get("scorer") == "corpora/scorers/ask_grounding.py"
           and (HERE / "corpora/scorers/ask_grounding.py").exists(),
           "ask-grounding names a scorer that runs the pinned ox rather than trusting the key")

    # Prompt files are payload: every byte is sent to the model, so the repo's
    # own SPDX convention stops at this directory.
    tainted = [p.name for p in sorted((HERE / "corpora" / "prompts").glob("*.txt"))
               if "SPDX-License-Identifier" in p.read_text(encoding="utf-8")]
    report(not tainted, "no prompt file carries an SPDX header into the payload",
           tainted)

    missing = []
    for tid, task in tasks.items():
        for cited in task.get("evidence", []):
            if not (HERE / cited).exists():
                missing.append("%s: %s" % (tid, cited))
    report(not missing, "every corpus entry cites evidence that exists", missing)

    # The link that makes a matched comparison findable: an observation naming a
    # task id must name one that exists.
    obs = sorted(p for p in (HERE / "observations").glob("*.md")
                 if p.name != "README.md")
    dangling = []
    for path in obs:
        match = re.search(r"^corpus:\s*(\S+)", path.read_text(encoding="utf-8"),
                          re.MULTILINE)
        if match and match.group(1) not in tasks:
            dangling.append("%s: %s" % (path.name, match.group(1)))
    report(not dangling, "every observation's corpus field names a real task",
           dangling)


def load_costcheck():
    source = (HERE / "costcheck.py").read_text(encoding="utf-8")
    source = source.replace('if __name__ == "__main__":', "if False:")
    namespace = {"__name__": "costcheckmod", "__file__": str(HERE / "costcheck.py")}
    exec(compile(source, str(HERE / "costcheck.py"), "exec"), namespace)
    return namespace


def test_costcheck():
    print("\n=== cost accounting ===")
    cc = load_costcheck()

    # The shape that matters: one API response is written to the transcript
    # once per content block, each copy carrying the SAME usage in full. Three
    # records, one response. Anything that does not dedupe reports 3x.
    one_response = [
        {"type": "assistant", "timestamp": "2026-08-30T01:11:26.100Z",
         "requestId": "req_A", "message": {"id": "msg_A", "model": "claude-opus-5",
          "content": [{"type": "thinking"}],
          "usage": {"input_tokens": 4, "output_tokens": 100,
                    "cache_read_input_tokens": 5000, "cache_creation_input_tokens": 20,
                    "output_tokens_details": {"thinking_tokens": 60}}}},
    ]
    one_response.append(json.loads(json.dumps(one_response[0])))
    one_response[1]["message"]["content"] = [{"type": "text"}]
    one_response.append(json.loads(json.dumps(one_response[0])))
    one_response[2]["message"]["content"] = [{"type": "tool_use"}]
    records = list(one_response) + [
        # A subagent turn: verification fan-out, counted in its own lane.
        {"type": "assistant", "timestamp": "2026-08-30T01:20:00.000Z",
         "requestId": "req_B", "isSidechain": True,
         "message": {"id": "msg_B", "model": "claude-opus-5",
                     "usage": {"input_tokens": 7, "output_tokens": 200,
                               "cache_read_input_tokens": 10, "cache_creation_input_tokens": 0}}},
        # Outside any window we ask for, and a different model.
        {"type": "assistant", "timestamp": "2026-08-30T09:00:00.000Z",
         "requestId": "req_C", "message": {"id": "msg_C", "model": "claude-haiku-4-5",
                     "usage": {"input_tokens": 1, "output_tokens": 9,
                               "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0}}},
        # Not an assistant turn, and a turn with no usage: both ignored.
        {"type": "user", "timestamp": "2026-08-30T01:12:00.000Z", "message": {"role": "user"}},
        {"type": "assistant", "timestamp": "2026-08-30T01:13:00.000Z",
         "message": {"id": "msg_D", "model": "claude-opus-5"}},
    ]
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "session.jsonl"
        path.write_text("\n".join(json.dumps(r) for r in records) + "\n", encoding="utf-8")

        turns = list(cc["iter_turns"](path))
        report(len(turns) == 3, "one API response counts once, not once per content block",
               "%d turns from %d records" % (len(turns), len(records)))

        totals, span, _ = cc["gather"]([path], None, None)
        report(sorted(totals) == [("claude-haiku-4-5", "main"), ("claude-opus-5", "main"),
                                  ("claude-opus-5", "subagent")],
               "subagent turns are counted in their own lane", sorted(totals))
        main = totals[("claude-opus-5", "main")]
        report(main["input"] == 4 and main["cache_read"] == 5000
               and main["output"] == 100 and main["thinking"] == 60,
               "cache reads stay out of the input column", main)

        windowed, _, dropped = cc["gather"]([path], "2026-08-30T01:00:00",
                                            "2026-08-30T01:30:00")
        report(("claude-haiku-4-5", "main") not in windowed and dropped == 1,
               "the window excludes turns outside it", dropped)

    # The ox side: reasoning is inside completion, not beside it, and a run
    # that never got a reply must not report zeros.
    with tempfile.TemporaryDirectory() as tmp:
        run = Path(tmp)
        (run / "meta.json").write_text(json.dumps(
            {"model": "minimax/minimax-m3:free", "venue": "openrouter", "mode": "review",
             "context_bytes": 22910, "timestamp": "2026-08-30T01-11-26Z"}), encoding="utf-8")
        (run / "response.json").write_text(json.dumps(
            {"usage": {"prompt_tokens": 5668, "completion_tokens": 33914, "cost": 0,
                       "completion_tokens_details": {"reasoning_tokens": 32973}}}),
            encoding="utf-8")
        parsed = cc["read_run"](str(run))
        report(parsed["completion"] == 33914 and parsed["reasoning"] == 32973
               and parsed["reasoning"] < parsed["completion"],
               "reasoning is read from inside the completion count", parsed["reasoning"])
        (run / "response.json").unlink()
        failed = cc["read_run"](str(run))
        report(failed.get("error") and failed["completion"] is None,
               "a run with no reply reports that, not zero tokens", failed.get("error"))

    # A dry run writes meta.json, request.json and status.json and never calls
    # anyone. Reporting it as a failed run puts a phantom outage in the
    # availability record; reporting it as a run at all inflates usage.
    with tempfile.TemporaryDirectory() as tmp:
        run = Path(tmp)
        (run / "meta.json").write_text(json.dumps(
            {"model": "m", "venue": "openrouter", "mode": "ask", "context_bytes": 0,
             "timestamp": "2026-08-30T19-02-20Z"}), encoding="utf-8")
        (run / "status.json").write_text(json.dumps({"dry_run": True, "ok": True}),
                                         encoding="utf-8")
        dry = cc["read_run"](str(run))
        report(dry.get("dry_run") and "dry run" in (dry.get("error") or ""),
               "a dry run is reported as a dry run, not a failed call",
               dry.get("error"))
        (run / "status.json").write_text(json.dumps({"dry_run": False, "ok": False}),
                                         encoding="utf-8")
        broke = cc["read_run"](str(run))
        report(not broke.get("dry_run") and "did not complete" in (broke.get("error") or ""),
               "a real run with no reply is still reported as incomplete",
               broke.get("error"))

    # Window comparison is lexicographic against the transcript's own stamps, so
    # the two must be the same shape to the second. A bound that parsed to a
    # different width (an offset instead of Z, say) would compare wrong rather
    # than fail, and silently shift every window.
    stamp = cc["parse_stamp"]
    forms = {"2026-08-30T01:05Z": "2026-08-30T01:05:00",
             "2026-08-30T01:05:21Z": "2026-08-30T01:05:21",
             "2026-08-30": "2026-08-30T00:00:00",
             "2026-08-30T01:05:21.339Z": "2026-08-30T01:05:21"}
    def parsed(text):
        # A rejection here is a failure to report, not a reason to abort the
        # suite: parse_stamp exits the process on bad input by design.
        try:
            return stamp(text)
        except SystemExit:
            return "REJECTED"
    wrong = ["%s -> %r" % (k, parsed(k)) for k, v in forms.items() if parsed(k) != v]
    report(not wrong, "every accepted timestamp form lands on the transcript's shape", wrong)
    report(all(parsed(k) != "REJECTED" and len(parsed(k)) == 19 for k in forms)
           and stamp(None) is None,
           "a parsed bound is the same width as a transcript stamp")
    try:
        stamp("last tuesday")
        rejected = False
    except SystemExit:
        rejected = True
    report(rejected, "an unreadable timestamp stops the run instead of shifting it")

    # costcheck runs against a transcript the harness is still appending to, so
    # the final line is routinely a half-written record.
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "live.jsonl"
        good = json.dumps(records[3])
        path.write_text(good + "\n" + good[:len(good) // 2], encoding="utf-8")
        try:
            turns = list(cc["iter_turns"](path))
            survived = len(turns) == 1
        except ValueError:
            survived = False
        report(survived, "a half-written last line is skipped, not fatal")

    # Two batches in one window is the normal case, and the totals row is the
    # figure that gets quoted.
    two = [{"model": "m", "venue": "v", "mode": "review", "context_bytes": 1,
            "timestamp": "A", "prompt": 5668, "completion": 33914, "reasoning": 32973,
            "cost": 0},
           {"model": "m", "venue": "v", "mode": "review", "context_bytes": 2,
            "timestamp": "B", "prompt": 7037, "completion": 18312, "reasoning": 15702,
            "cost": 0}]
    totals = {("claude-opus-5", "main"): {"turns": 1, "input": 100, "output": 200,
                                          "cache_read": 0, "cache_write": 0, "thinking": 0}}
    text = cc["render"](two, totals, ("A", "B"), (None, None), None)
    report("| **total** | | | | 12,705 | 52,226 | 48,675 |" in text,
           "several runs in one window sum into a total row")

    # A window cannot be priced from a whole-session record. Reporting the
    # session's dollars beside a 40-minute window would read as the window's.
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "priced.jsonl"
        priced = records[:3] + [{"type": "cost-state", "totalCostUSD": 23.06,
                                 "modelUsage": {"claude-opus-5": {}}}]
        path.write_text("\n".join(json.dumps(r) for r in priced) + "\n", encoding="utf-8")
        whole = subprocess.run([sys.executable, str(HERE / "costcheck.py"),
                                "--session", str(path)],
                               capture_output=True, text=True, timeout=60)
        windowed = subprocess.run([sys.executable, str(HERE / "costcheck.py"),
                                   "--session", str(path),
                                   "--from", "2026-08-30T01:00Z", "--to", "2026-08-30T01:30Z"],
                                  capture_output=True, text=True, timeout=60)
        report("$23.06" in whole.stdout and "$" not in windowed.stdout,
               "a windowed run never quotes the whole session's dollars",
               windowed.stdout[-90:])
        report("Window: 2026-08-30T01:00:00 .. 2026-08-30T01:30:00 (given)." in windowed.stdout
               and "Upper bound" in windowed.stdout,
               "every report states its window and that it is an upper bound")

    # The transcript path is a harness-internal convention, not an interface.
    # When it moves, the promise is that costcheck says so and names where it
    # looked -- guessing, or reporting an empty session as a cheap run, is the
    # failure that would matter.
    missed = []
    # Both spellings, because the real keys begin with a dash and argparse
    # reads a bare -Users-... as a flag. A documented invocation that cannot be
    # typed is a defect; this caught one.
    for spelling in ("no-such-project-key", "--project=-no-such-project-key"):
        argv = ([sys.executable, str(HERE / "costcheck.py")]
                + ([spelling] if spelling.startswith("--")
                   else ["--project", spelling]))
        gone = subprocess.run(argv, capture_output=True, text=True, timeout=60)
        if not (gone.returncode != 0 and "no transcript directory" in gone.stderr
                and "--session" in gone.stderr):
            missed.append("%s -> %s" % (spelling, gone.stderr.strip()[:60]))
    report(not missed, "a moved transcript directory is reported, not guessed at", missed)

    # And the dashless spelling has to actually resolve to the dashed directory,
    # or the workaround for argparse is only a nicer error message.
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "-Users-someone-src-thing").mkdir()
        (root / "-Users-someone-src-thing" / "s.jsonl").write_text("", encoding="utf-8")
        saved = cc["TRANSCRIPT_ROOT"]
        cc["TRANSCRIPT_ROOT"] = root
        try:
            found = cc["find_transcripts"]("Users-someone-src-thing")
            resolved = [p.name for p in found] == ["s.jsonl"]
        except SystemExit:
            resolved = False
        finally:
            cc["TRANSCRIPT_ROOT"] = saved
        report(resolved, "a project key resolves with or without its leading dash")


def load_usagereport():
    source = (HERE / "usagereport.py").read_text(encoding="utf-8")
    source = source.replace('if __name__ == "__main__":', "if False:")
    namespace = {"__name__": "usagereportmod", "__file__": str(HERE / "usagereport.py")}
    exec(compile(source, str(HERE / "usagereport.py"), "exec"), namespace)
    return namespace


def test_pricing():
    print("\n=== catalog pricing ===")
    cc = load_costcheck()
    catalog = {"venue": "openrouter", "captured_at": "2026-09-01T00:00:00Z",
               "payload": {"data": [
                   {"id": "anthropic/claude-sonnet-5",
                    "pricing": {"prompt": "0.000002", "completion": "0.00001"}},
                   {"id": "minimax/minimax-m3:free",
                    "pricing": {"prompt": "0", "completion": "0"}},
               ]}}
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "2026-09-01.json"
        path.write_text(json.dumps(catalog), encoding="utf-8")
        prices = cc["price_from_catalog"](path, "anthropic/claude-sonnet-5")
        report(prices == (0.000002, 0.00001), "per-token prices are read from the "
               "archived OpenRouter catalog", prices)
        run = {"venue": "openrouter", "model": "anthropic/claude-sonnet-5",
               "prompt": 1000, "completion": 2000, "cost": None}
        priced = cc["price_run"](dict(run), path)
        report(abs(priced["usd"] - 0.022) < 1e-9 and priced["priced_from"] == path.name,
               "usd is prompt*in + completion*out, and names the catalog it came from",
               (priced["usd"], priced["priced_from"]))
        # Reasoning is inside completion, so it must not be added again.
        with_reasoning = cc["price_run"](dict(run, reasoning=1500), path)
        report(abs(with_reasoning["usd"] - priced["usd"]) < 1e-12,
               "reasoning tokens are not priced twice", with_reasoning["usd"])
        free = cc["price_run"](dict(run, model="minimax/minimax-m3:free"), path)
        report(free["usd"] == 0 and cc["dollars"](free) == "free",
               "a zero-priced row renders as free", cc["dollars"](free))
        unknown = cc["price_run"](dict(run, model="nobody/nothing"), path)
        report(unknown["usd"] is None and cc["dollars"](unknown) == "-",
               "a model the catalog does not list is unpriced, never estimated",
               cc["dollars"](unknown))
        other = {"venue": "zenmux", "payload": {"data": [{"id": "x", "pricing": {}}]}}
        path.write_text(json.dumps(other), encoding="utf-8")
        report(cc["price_from_catalog"](path, "x") is None,
               "only the OpenRouter catalog shape is priced", None)
        incomplete = cc["price_run"]({"venue": "openrouter", "model": "m",
                                      "prompt": None, "completion": None}, path)
        report(incomplete["usd"] is None, "a run with no reply is not priced", None)


def test_usagereport():
    print("\n=== weekly usage ===")
    ur = load_usagereport()

    def write_run(root, repo, stamp, status):
        run = root / repo / "logs" / stamp
        run.mkdir(parents=True)
        (run / "status.json").write_text(json.dumps(status), encoding="utf-8")
        return run

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        manifest = root / "m.json"
        manifest.write_text(json.dumps({"recommendations": [
            {"venue": "openrouter", "model": "paid-one", "cost": "paid"},
            {"venue": "openrouter", "model": "used-one", "cost": "free"},
            {"venue": "opencode", "model": "never-called", "cost": "free"}]}),
            encoding="utf-8")
        info = {"path": str(manifest), "sha256": "abc"}
        real = {"ok": True, "dry_run": False, "model": "used-one", "mode": "review",
                "prompt_tokens": 10, "completion_tokens": 20, "reasoning_tokens": 15,
                "truncated": False, "manifest": info, "attempts": [
                    {"position": 1, "venue": "openrouter", "model": "paid-one",
                     "skipped": "cost=paid (pass --allow-paid to use it)"},
                    {"position": 2, "venue": "openrouter", "model": "used-one"}]}
        write_run(root, "repoA", "2026-08-30T01-11-26Z", real)
        dry = dict(real, dry_run=True)
        write_run(root, "repoA", "2026-08-30T02-00-00Z", dry)
        old = dict(real)
        write_run(root, "repoB", "2026-08-01T01-00-00Z", old)
        # 26 seconds past a window that ends at 01:11:00. This one only lands
        # outside if the stamp's "-" separators are turned back into ":":
        # "-" sorts below ":", so an unconverted stamp compares as earlier and
        # silently drifts into the window.
        write_run(root, "repoB", "2026-08-30T01-11-26Z", dict(real))
        # A second run claimed in the same second. Both oxbox implementations
        # suffix the directory (-2, -3, ...) rather than sharing it; the suffix
        # orders names and is not part of the time, so the stamp must come out
        # identical to the unsuffixed run's and land on the same side of the
        # window. A fixed-width conversion turns it into a fourth colon field.
        suffixed = write_run(root, "repoB", "2026-08-30T01-11-26Z-2", dict(real))
        # A checkout one level deeper than <root>/<repo>, which is why the
        # sweep carries a second pattern.
        write_run(root, "group/nested", "2026-08-30T01-05-00Z", dict(real))
        broken = root / "repoB" / "logs" / "2026-08-30T03-00-00Z"
        broken.mkdir(parents=True)
        (broken / "status.json").write_text("{not json", encoding="utf-8")

        found, swept, _ = ur["find_runs"]([root])
        report(len(found) == 7, "the sweep reaches nested checkouts too", len(found))

        kept, dryruns, outside, unreadable = ur["collect"](
            found, "2026-08-30T00:00:00", None)
        report(len(kept) == 4 and len(dryruns) == 1,
               "a dry run is never counted as a run",
               "kept=%d dry=%d" % (len(kept), len(dryruns)))
        stamps = {r["dir"].name: r["stamp"] for r in kept}
        report(stamps.get(suffixed.name) == "2026-08-30T01:11:26"
               and ur["stamp_to_iso"](suffixed.name) == "2026-08-30T01:11:26",
               "a collision-suffixed run directory reads as its second, not as a fourth field",
               stamps.get(suffixed.name))

        tight, _, past, _ = ur["collect"](found, "2026-08-30T00:00:00",
                                          "2026-08-30T01:11:00")
        report(past == 5 and len(tight) == 1,
               "the ox stamp format compares correctly against the window",
               "outside=%d kept=%d" % (past, len(tight)))
        report(len(unreadable) == 1,
               "an unreadable status file is reported, not silently dropped",
               unreadable)

        used, skips, failures, truncated, tokens = ur["tally"](kept)
        report(list(skips.values()) == [4]
               and "cost=paid" in list(skips)[0][1],
               "a skipped entry is tallied with the reason ox gave", skips)

        entries = ur["manifest_entries"](kept)
        text = ur["render"](kept, dryruns, outside, unreadable, swept, [],
                            ("2026-08-30T00:00:00", None), entries)
        report("never-called" in text and "used-one" not in text.split("Never reached")[1],
               "entries the week never reached are named")
        # The watermark is compared against run DIRECTORY NAMES by whoever
        # prunes, so it has to be written in that shape. ox names directories
        # 2026-08-30T16-05-13Z; an ISO watermark fails in the dangerous
        # direction, because "-" sorts below ":" and every same-hour run then
        # looks already-read.
        log_dir = root / "repoA" / "logs"
        ur["write_watermark"](log_dir, "2026-08-30T16-05-13Z", None, 3)
        mark = json.loads((log_dir / ur["WATERMARK"]).read_text(encoding="utf-8"))
        newer = "2026-08-30T16-59-59Z"
        older = "2026-08-30T15-00-00Z"
        report(newer > mark["scraped_through"] and not (older > mark["scraped_through"]),
               "a run directory name compares correctly against the watermark",
               mark["scraped_through"])
        report(mark["scraped_through_iso"] == "2026-08-30T16:05:13",
               "the watermark also carries a human-readable timestamp",
               mark["scraped_through_iso"])
        report("unparseable watermark is not an absent one" in mark["contract"],
               "the contract tells a pruner to fail closed on a damaged watermark")
        report(not list(log_dir.glob("*.tmp")),
               "the atomic write leaves no temporary file behind",
               [p.name for p in log_dir.glob("*.tmp")])

        report("1 dry runs excluded" in text,
               "the report says how many dry runs it set aside")


def test_repo_discipline():
    print("\n=== the repo's own rules ===")

    # Committed snapshots must carry the fields that say how far to trust them.
    # Access files live alongside catalogs but are a different document with a
    # different schema and a different evidence tier; test_tier_separation
    # covers them.
    snapshots = sorted(p for p in (HERE / "snapshots").rglob("*.json")
                       if not p.name.endswith("-access.json"))
    report(bool(snapshots), "snapshots are committed", len(snapshots))
    bad = []
    for path in snapshots:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not all(k in data for k in ("venue", "pricing_class", "roster_scope",
                                       "captured_at", "models")):
            bad.append(path.name)
        elif data["pricing_class"] == "B":
            if any(m.get("free") is False for m in data["models"]):
                bad.append("%s: class B recorded free=False" % path.name)
        elif any(m.get("free") is None for m in data["models"]):
            bad.append("%s: class A recorded free=None" % path.name)
    report(not bad, "every snapshot declares its class and respects it", bad)

    # Raw catalog archives: every model as served, so pricing claims about
    # paid or since-delisted models stay checkable. Wrapper fields only; the
    # payload is deliberately unnormalized.
    catalogs = sorted((HERE / "catalogs").rglob("*.json"))
    report(bool(catalogs), "catalog archives are captured", len(catalogs))
    bad = []
    for path in catalogs:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not all(k in data for k in ("captured_at", "venue", "source", "payload")):
            bad.append(path.name)
    report(not bad, "every catalog archive says when and where it was captured", bad)

    # Vendor-authored prose cannot be relicensed by this repo, so it must not be
    # committed here at all. The archive's job -- keeping a claim about a paid or
    # delisted model checkable -- needs ids, pricing and capabilities, which are
    # facts. Marketing copy is the vendor's, and an Apache grant over it is a
    # grant nobody here can make.
    leaked, undeclared = [], []
    for path in catalogs:
        data = json.loads(path.read_text(encoding="utf-8"))
        if "redacted_fields" not in data:
            undeclared.append(path.name)
        payload = data.get("payload") or {}
        rows = (payload.get("data") or payload.get("models") or []) if isinstance(payload, dict) else []
        for row in rows:
            if not isinstance(row, dict):
                continue
            for field in ("description",):
                if row.get(field):
                    leaked.append("%s: %s carries %s" % (path.name, row.get("id"), field))
    report(not leaked, "no committed catalog carries vendor-authored prose", leaked[:3])
    report(not undeclared, "every catalog declares what was redacted from it", undeclared)

    # Observations are the Observed tier; the schema is what lets the generator
    # group them without interpreting prose.
    obs = sorted(p for p in (HERE / "observations").glob("*.md") if p.name != "README.md")
    report(bool(obs), "observations are committed", len(obs))
    kinds = {"findings", "hygiene", "access", "availability", "efficiency",
             "card-contradiction"}
    sources = {"oxbox-run", "probe", "manual"}
    problems = []
    for path in obs:
        text = path.read_text(encoding="utf-8")
        match = re.search(r"^---\n(.*?)\n---\n", text, re.DOTALL | re.MULTILINE)
        if not match:
            problems.append("%s: no frontmatter" % path.name)
            continue
        fields = dict(re.findall(r"^(\w+):\s*(.+)$", match.group(1), re.MULTILINE))
        for required in ("date", "venue", "model", "kind", "source", "agent"):
            if required not in fields:
                problems.append("%s: missing %s" % (path.name, required))
        if fields.get("kind") not in kinds:
            problems.append("%s: unknown kind %r" % (path.name, fields.get("kind")))
        if fields.get("source") not in sources:
            problems.append("%s: unknown source %r" % (path.name, fields.get("source")))
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", fields.get("date", "")):
            problems.append("%s: date not YYYY-MM-DD" % path.name)
        if not path.name.startswith(fields.get("date", "\0")):
            problems.append("%s: filename disagrees with its date field" % path.name)
    report(not problems, "every observation carries valid frontmatter", problems[:4])

    # A baseline is a reference point, not a candidate: a paid model run on
    # the same fixture so a free model's count means something. A free model
    # can never be one -- the free tier is what the survey is *about*. A paid
    # model may wear both hats (glm-5.3-flash is rank 2 of the 2026-09-01
    # manifest and a baseline), and then the baseline observation is not what
    # moves its manifest entry. Whether a baseline can carry an Editor's
    # Rating is test_ratings' question.
    roles = {"candidate", "baseline"}
    free_recommended = set()
    for path in sorted((HERE / "manifests").glob("*.json")):
        if path.is_symlink():
            continue
        for rec in json.loads(path.read_text(encoding="utf-8")).get("recommendations", []):
            if rec.get("cost") == "free":
                free_recommended.add(rec.get("model"))
    bad_roles, baseline_in_manifest = [], []
    for path in obs:
        text = path.read_text(encoding="utf-8")
        head = re.search(r"^---\n(.*?)\n---\n", text, re.DOTALL | re.MULTILINE)
        if not head:
            continue
        fields = dict(re.findall(r"^(\w+):\s*(.+)$", head.group(1), re.MULTILINE))
        role = fields.get("role")
        if role is None:
            continue
        if role not in roles:
            bad_roles.append("%s: %r" % (path.name, role))
            continue
        if role != "baseline":
            continue
        model = fields.get("model", "").strip('"')
        if model.endswith(":free") or model in free_recommended:
            baseline_in_manifest.append("%s: %s" % (path.name, model))
    report(not bad_roles, "every observation role is candidate or baseline", bad_roles)
    report(not baseline_in_manifest, "no free model is a baseline",
           baseline_in_manifest)

    # Both halves of the cost, from 2026-08-30 on. Earlier observations are
    # grandfathered rather than backfilled: editing a published one to add a
    # number nobody measured at the time is exactly what the archive is for
    # preventing.
    COST_RULE_FROM = "2026-08-30"
    uncosted = []
    for path in obs:
        text = path.read_text(encoding="utf-8")
        head = re.search(r"^---\n(.*?)\n---\n", text, re.DOTALL | re.MULTILINE)
        if not head:
            continue
        fields = dict(re.findall(r"^(\w+):\s*(.+)$", head.group(1), re.MULTILINE))
        if fields.get("date", "") < COST_RULE_FROM:
            continue
        if fields.get("kind") != "findings" or fields.get("source") != "oxbox-run":
            continue
        if not re.search(r"^##+\s+Cost\b", text, re.MULTILINE):
            uncosted.append(path.name)
    report(not uncosted, "every findings run since %s reports what it cost"
           % COST_RULE_FROM, uncosted)

    # The load-bearing rule -- a probe cannot recommend a model -- now lives in
    # test_ratings: a probe carries no measured fields, so it has no row, so it
    # cannot be rated.

    # manifests/latest.json is what a consumer points --manifest at when it just
    # wants the current advice. A symlink rather than a copy, so it cannot drift
    # from the file it names, and checked here because the failure mode is
    # silent: a stale pointer serves last week's ranking forever without erroring.
    manifest_dir = HERE / "manifests"
    dated = sorted(manifest_dir.glob("oxbox-manifest-*.json"))
    latest = manifest_dir / "latest.json"
    problems = []
    if not dated:
        problems.append("no dated manifests")
    elif not latest.is_symlink():
        problems.append("latest.json is missing or is not a symlink")
    else:
        target = os.readlink(str(latest))
        if "/" in target:
            problems.append("latest.json points outside its directory: %s" % target)
        if target != dated[-1].name:
            problems.append("latest.json -> %s, newest is %s" % (target, dated[-1].name))
        if not latest.exists():
            problems.append("latest.json is dangling")
    report(not problems, "latest.json points at the newest manifest", problems)

    # Provider pages are the only edited-in-place documents; they must date
    # their verification, because rate limits rot faster than anything here.
    providers = sorted(p for p in (HERE / "providers").glob("*.md")
                       if p.name != "README.md")
    report(bool(providers), "provider pages are committed", len(providers))
    stale = [p.name for p in providers
             if not re.search(r"^last_verified:\s*\d{4}-\d{2}-\d{2}",
                              p.read_text(encoding="utf-8"), re.MULTILINE)]
    report(not stale, "every provider page dates its verification", stale)

    # SPDX on everything, per the repo convention.
    tracked = subprocess.run(["git", "ls-files"], capture_output=True, text=True,
                             cwd=str(HERE)).stdout.split()
    missing = []
    for name in tracked:
        if not name.endswith((".md", ".py", ".yml")) and name != "oxsurvey":
            continue
        if name == "LICENSE":
            continue
        path = HERE / name
        # A file that is staged but gone from disk used to crash this loop with
        # a FileNotFoundError, which reads as a broken test rather than as the
        # staging mistake it is. Report it.
        if not path.exists():
            missing.append("%s: tracked but not on disk" % name)
            continue
        body = path.read_text(encoding="utf-8", errors="replace")
        if "SPDX-License-Identifier" not in body:
            missing.append(name)
    report(not missing, "every source and doc file carries an SPDX header", missing)


def load_ratings():
    source = (HERE / "ratings.py").read_text(encoding="utf-8")
    source = source.replace('if __name__ == "__main__":', "if False:")
    namespace = {"__name__": "ratingsmod", "__file__": str(HERE / "ratings.py")}
    exec(compile(source, str(HERE / "ratings.py"), "exec"), namespace)
    return namespace


def test_ratings():
    print("\n=== the digits and the Editor's Rating ===")
    rt = load_ratings()

    # The buckets. The speed row was checked against the recorded runs before
    # it was adopted (docs/decisions.md): a rubric that puts the real data in
    # one bucket is not a rubric.
    speed, quality, cost = rt["speed_digit"], rt["quality_digit"], rt["cost_digit"]
    report([speed(12), speed(189), speed(544), speed(1289)] == [5, 3, 2, 0],
           "speed digits land the recorded runs in different buckets")
    report(speed(None) is None and speed(30, timed_out=True) == 0,
           "speed: unmeasured is a dash, a timeout is 0")
    report([quality(10, 10), quality(8, 10), quality(5, 10), quality(3, 10),
            quality(1, 10), quality(0, 10)] == [5, 4, 3, 2, 1, 0],
           "quality digits follow the rubric's fractions")
    report(quality(8, 8, required_ok=False) == 0 and quality(None, 8) is None,
           "quality: a failed required gate is 0, no count is a dash")
    report([cost(0.001, 1, 1.0), cost(0.05, 1, 1.0), cost(0.5, 1, 1.0),
            cost(2, 1, 1.0), cost(8, 1, 1.0), cost(20, 1, 1.0)] == [5, 4, 3, 2, 1, 0],
           "cost digits are logarithmic against the ceiling")
    report(cost(1, 0, 1.0) == 0 and cost(1, 1, None) is None and cost(None, 1, 1.0) is None,
           "cost: no real defect is 0, no ceiling or no total is a dash")

    # The record the digits come from. Nobody types a digit: the derived keys
    # are forbidden in frontmatter, and only a run carries measured fields.
    obs = rt["load_observations"]()
    tasks = rt["load_corpus"]()
    # A field that is not a number would crash the bucketing below, and a
    # traceback is a broken test rather than the report it should be; check
    # the record before reading it.
    unparsed = []
    for o in obs:
        for key in ("wall_s", "findings", "real", "hits", "hits_of", "self_hits",
                    "usd_model", "usd_total"):
            if key in o:
                try:
                    rt["_num"](o[key])
                except ValueError:
                    unparsed.append("%s: %s=%r" % (o["_file"], key, o[key]))
    report(not unparsed, "every measured field is a number", unparsed)
    if unparsed:
        return
    rows = rt["run_rows"](obs, tasks)
    report(bool(rows), "run-backed observations produce catalog rows", len(rows))
    typed = [o["_file"] for o in obs if any(k in o for k in rt["DERIVED_KEYS"])]
    report(not typed, "no observation types a quality, cost or speed digit", typed)
    # Run-output fields belong to runs. A check record (a manual observation
    # that names a run and carries harness_* fields) is the one exception, and
    # it may carry only the harness fields plus the run it checked.
    run_output = [k for k in rt["MEASURED_FIELDS"]
                  if k not in ("disqualifier", "run") and not k.startswith("harness_")]
    probes = [o["_file"] for o in obs
              if o.get("source") != "oxbox-run" and not o.get("corrects")
              and any(k in o for k in run_output)]
    report(not probes, "no probe or manual observation carries run-output fields (a correction may)", probes)
    dangling = [o["_file"] for o in obs if o.get("corrects")
                and o["corrects"].strip().split("/")[-1] not in {x["_file"] for x in obs}]
    report(not dangling, "every correction names an observation that exists", dangling)
    corrected = [o["_file"] for o in obs if o.get("_corrected_by")]
    synthetic = [{"_file": "a.md", "model": "m", "real": "3", "findings": "4", "role": "candidate"},
                 {"_file": "b.md", "model": "m", "corrects": "a.md", "real": "0", "role": "candidate"}]
    by = {x["_file"]: x for x in synthetic}
    for x in synthetic:
        t = by.get(x.get("corrects", ""))
        if t:
            for key in rt["CORRECTABLE"]:
                if key in x:
                    t[key] = x[key]
    report(by["a.md"]["real"] == "0" and by["a.md"]["findings"] == "4",
           "a correction overlays only the fields it carries")
    orphan_checks = [o["_file"] for o in obs
                     if o.get("harness_window") and o.get("kind") not in rt["ROW_KINDS"]
                     and not o.get("run")]
    report(not orphan_checks, "every check record names the run it checked", orphan_checks)
    missing = []
    for o in obs:
        if o.get("source") != "oxbox-run" or o.get("kind") not in rt["ROW_KINDS"]:
            continue
        if o.get("date", "") < rt["RULE_FROM"]:
            continue
        if "run" not in o or "wall_s" not in o:
            missing.append("%s: no run or wall_s" % o["_file"])
        if not (("findings" in o and "real" in o) or "hits" in o):
            missing.append("%s: no findings/real or hits" % o["_file"])
    report(not missing, "every run-backed row since %s carries run, wall_s and a count"
           % rt["RULE_FROM"], missing)
    undeclared = [tid for tid, t in tasks.items()
                  if "quality" not in t or "cost_ceiling_usd_per_real" not in t]
    report(not undeclared, "every corpus task declares its quality rubric and cost ceiling",
           undeclared)
    uncounted = [r["file"] for r in rows
                 if r["fixture"] and (tasks.get(r["fixture"]) or {}).get("quality")
                 and r["hits"] is None]
    report(not uncounted, "every run on a fixture with a seeded set records its hits",
           uncounted)

    # The one hand-written column. On the scale or null, dated and explained
    # when written, only for a model that was actually run, never for a model
    # whose only runs are baselines.
    path = HERE / "editor-ratings.json"
    data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    report("ratings" in data, "editor-ratings.json is committed")
    ratings = data.get("ratings", {})
    off_scale = [m for m, e in ratings.items()
                 if e.get("rating") not in (None,) + tuple(rt["SCALE"])]
    report(not off_scale, "every Editor's Rating is on the scale or null", off_scale)
    undated = [m for m, e in ratings.items()
               if e.get("rating") and not (e.get("date") and e.get("why"))]
    report(not undated, "every written rating carries a date and a why", undated)
    tried = {r["model"] for r in rows}
    unknown = [m for m in ratings if m not in tried]
    report(not unknown, "every rated model was actually run", unknown)
    baselines = rt["baseline_only"](obs)
    rated_baselines = [m for m, e in ratings.items() if e.get("rating") and m in baselines]
    report(not rated_baselines, "no baseline-only model carries an Editor's Rating",
           rated_baselines)

    # The manifest is derived from the rating. Exercised on synthetic data so
    # every branch is seen to bite, then applied to the real latest manifest
    # once it is dated on or after the rule.
    check = rt["check_manifest"]
    synth = {"a": {"rating": "Good"}, "b": {"rating": "Acceptable"},
             "c": {"rating": "Marginal"}, "d": {"rating": "Good"}}
    disq = {"d": ("2026-09-06", "not_found")}

    def manifest(*models):
        return {"recommendations": [{"model": m} for m in models]}

    report(not check(manifest("a", "b"), synth, disq, set()),
           "Goods then Acceptables, minus the disqualified, is a valid manifest")
    report(check(manifest("a", "c"), synth, disq, set()),
           "a Marginal in the manifest is refused")
    report(check(manifest("b", "a"), synth, disq, set()),
           "an Acceptable ranked above a Good is refused")
    report(check(manifest("a"), synth, disq, set()),
           "a rated Acceptable missing from the manifest is refused")
    report(check(manifest("a", "b", "d"), synth, disq, set()),
           "a model with a standing disqualifier in the manifest is refused")
    report(check(manifest("a", "b"), synth, {}, {"a"}),
           "a baseline-only model in the manifest is refused")
    report(check(manifest("a", "b", "z"), synth, disq, set()),
           "an unrated model in the manifest is refused")
    latest = json.loads((HERE / "manifests" / "latest.json").read_text(encoding="utf-8"))
    if latest.get("issue_date", "") >= rt["RULE_FROM"]:
        problems = check(latest, ratings, rt["open_disqualifiers"](obs), baselines)
        report(not problems, "the latest manifest is derived from the Editor's Rating",
               problems)
    else:
        print("[skip] manifest %s predates the rating rule (%s); grandfathered"
              % (latest.get("issue_date"), rt["RULE_FROM"]))

    # The cost comparison: the checking half is priced from the catalog, a
    # shared window is charged once, a free-tier id is free even when the venue
    # publishes no price, and a failed gate buys nothing.
    prices = {"anthropic/claude-fable-5.1": {"prompt": "0.00001", "completion": "0.00005",
                                             "input_cache_read": "0.00000025",
                                             "input_cache_write": "0.0000125"},
              "z-ai/glm-5.3-flash": {"prompt": "0.000000075", "completion": "0.00000025"},
              "anthropic/claude-sonnet-5": {"prompt": "0.000002", "completion": "0.00001"}}
    window = {"harness_model": "claude-fable-5-1", "harness_window": "w",
              "harness_in": "1000000", "harness_out": "1000000",
              "harness_cache_read": "1000000", "harness_cache_write": "1000000"}
    report(abs(rt["price_window"](window, prices) - 72.75) < 1e-9,
           "a harness window is priced from the supervisor's catalog row, cache included")
    report(rt["price_window"]({"harness_model": "nobody", "harness_window": "w"}, prices) is None,
           "a window whose supervisor the catalog does not price is unpriced, not zero")
    report(rt["window_seconds"]("2026-09-06T21:22Z..2026-09-06T21:27Z") == 300
           and rt["window_seconds"]("w") is None,
           "a window's span is read from its key; a keyless window has no time")
    tier = rt["tier_of"]
    report([tier("nemotron-3-ultra-free", prices, None), tier("z-ai/glm-5.3-flash", prices, 0.001),
            tier("anthropic/claude-sonnet-5", prices, 0.04), tier("mistral/leanstral-1-5", prices, None)]
           == ["free", "cheap paid", "frontier", "paid, price unknown"],
           "tiers: free by id or bill, cheap and frontier by list price, unknown named as such")
    base = {"source": "oxbox-run", "kind": "findings", "role": "candidate", "venue": "v",
            "harness_model": "claude-fable-5-1", "harness_window": "shared",
            "harness_in": "0", "harness_out": "100000", "harness_cache_read": "0",
            "harness_cache_write": "0"}
    a = dict(base, model="a", findings="4", real="2", usd_model="0", _file="a")
    b = dict(base, model="b", findings="4", real="2", usd_model="0", _file="b")
    costs = {r["model"]: r for r in rt["cost_rows"]([a, b], prices, tasks={})}
    report(abs(costs["a"]["check_usd_per_run"] - 2.5) < 1e-9
           and abs(costs["a"]["usd_per_real"] - 1.25) < 1e-9
           and abs(costs["a"]["total_usd_per_run"] - 2.5) < 1e-9,
           "a $5 window shared by two runs is charged $2.50 to each, once, and the total adds the model half")
    gated = dict(base, model="g", corpus="oxbox-secret-scanner-fix", hits="8", hits_of="8",
                 applies="false", usd_model="0.01", _file="g")
    task = {"oxbox-secret-scanner-fix": {"quality": {"of": 8, "requires": ["applies"]}}}
    g = rt["cost_rows"]([gated], prices, tasks=task)[0]
    report(g["real"] == 0 and g["usd_per_real"] is None,
           "hits behind a failed gate count for nothing in the cost table")
    # A metered check record carries the venue's bill, which outranks a
    # token-priced window for the same run and checker, and is never repriced.
    billed = {"kind": "efficiency", "source": "manual", "run": "r1", "harness_model": "claude-fable-5-1",
              "harness_window": "2026-09-07T00:10Z..2026-09-07T00:13Z", "harness_venue": "openrouter",
              "harness_in": "17402", "harness_out": "7934", "harness_usd": "0.57072", "_file": "m"}
    priced = {"kind": "efficiency", "source": "manual", "run": "r1", "harness_model": "claude-fable-5-1",
              "harness_window": "w", "harness_in": "66", "harness_out": "9744",
              "harness_cache_read": "114776", "harness_cache_write": "75805", "_file": "p"}
    report(abs(rt["price_window"](billed, prices) - 0.57072) < 1e-9
           and abs(rt["price_window"](billed, prices, as_model="anthropic/claude-sonnet-5") - 0.57072) < 1e-9,
           "a billed check record prices at its bill, under any supervisor's rates")
    row = dict(base, model="r", run="r1", findings="3", real="1", usd_model="0.001", _file="r")
    row.pop("harness_window"); row.pop("harness_model")
    rows = [rt["measure"](row, {})]
    for order in ([billed, priced], [priced, billed]):
        rt["attach_checks"](rows, order)
        report(rows[0]["checks"]["claude-fable-5-1"] is billed,
               "the billed record wins over the token-priced one for the same run and checker (order %s)"
               % ", ".join(o["_file"] for o in order))
    pair = rt["same_batch"]([billed, priced, dict(priced, harness_model="claude-opus-5", _file="q")], prices)
    labels = [c["checker"] for e in pair for c in e["checkers"]]
    report(pair and len(labels) == 3 and "claude-fable-5-1 via openrouter (billed)" in labels,
           "the same-batch table keeps the metered request beside the in-harness session", labels)
    unbilled_venue = [o["_file"] for o in obs if ("harness_usd" in o) != ("harness_venue" in o)]
    report(not unbilled_venue, "every billed check record names the venue that billed it", unbilled_venue)
    harness_numeric = []
    for o in obs:
        for key in ("harness_in", "harness_out", "harness_cache_read", "harness_cache_write", "harness_usd"):
            if key in o:
                try:
                    rt["_num"](o[key])
                except ValueError:
                    harness_numeric.append("%s: %s" % (o["_file"], key))
        if ("harness_window" in o) != ("harness_model" in o):
            harness_numeric.append("%s: window without model or model without window" % o["_file"])
    report(not harness_numeric, "every harness field is numeric and every window names its supervisor",
           harness_numeric)

    # The disqualifier rule: open until a later run clears it, same day clears.
    open_marks = rt["open_disqualifiers"]
    stale = [{"model": "m", "source": "oxbox-run", "kind": "access", "date": "2026-09-01",
              "disqualifier": "not_found", "role": "candidate", "_file": "x"}]
    cleared = stale + [{"model": "m", "source": "oxbox-run", "kind": "findings",
                        "date": "2026-09-01", "role": "candidate", "_file": "y"}]
    report("m" in open_marks(stale, catalog_root=Path(tempfile.gettempdir()) / "no-catalogs-here")
           and "m" not in open_marks(cleared, catalog_root=Path(tempfile.gettempdir()) / "no-catalogs-here"),
           "a disqualifier stands until a run dated on or after it")
    # Delisting: absent from the venue's newest archived catalog, dated by it,
    # and a later run does not clear it.
    with tempfile.TemporaryDirectory() as tmp:
        cat = Path(tmp) / "openrouter"
        cat.mkdir()
        (cat / "2026-09-01.json").write_text(json.dumps(
            {"payload": {"data": [{"id": "vendor/listed"}]}}), encoding="utf-8")
        rows = [{"model": "vendor/listed", "venue": "openrouter", "source": "oxbox-run",
                 "kind": "findings", "date": "2026-09-06", "role": "candidate", "_file": "l"},
                {"model": "vendor/gone", "venue": "openrouter", "source": "oxbox-run",
                 "kind": "findings", "date": "2026-09-06", "role": "candidate", "_file": "g"}]
        marks = open_marks(rows, catalog_root=Path(tmp))
        report(marks.get("vendor/gone") == ("2026-09-01", "delisted") and "vendor/listed" not in marks,
               "a model missing from its venue's newest catalog is delisted, dated by that catalog")
    live = open_marks(obs)
    report(live.get("x-preview-f-free", ("", ""))[1] == "delisted"
           and live.get("z-ai/glm-5.3-free", ("", ""))[1] == "delisted"
           and "minimax/minimax-m3:free" not in live,
           "the two delisted rows in the record are marked and the listed ones are not")


def main():
    ox = load_oxsurvey()
    test_adapters(ox)
    test_snapshot_shape(ox)
    test_diff_and_triggers(ox)
    test_cli()
    test_access_probe(ox)
    test_tier_separation()
    test_corpus()
    test_costcheck()
    test_pricing()
    test_usagereport()
    test_repo_discipline()
    test_ratings()

    print("\nplatform: %s" % sys.platform)
    total = PASSES + len(FAILURES)
    if FAILURES:
        print("survey checks failed: %d/%d passed" % (PASSES, total))
        for label in FAILURES:
            print("  - %s" % label)
        return 1
    print("survey checks hold: %d/%d passed" % (PASSES, total))
    return 0


if __name__ == "__main__":
    sys.exit(main())
