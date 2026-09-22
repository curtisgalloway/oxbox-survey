#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Curtis Galloway
# SPDX-License-Identifier: Apache-2.0
"""Score the reviewing agent, the way the corpus scores the reviewed model.

    ./verifiercheck.py build --pin <dir>
    ./verifiercheck.py run --arm opus --all
    ./verifiercheck.py run --arm gemini --all
    ./verifiercheck.py score

costcheck.py established that verification is the expensive half of a run. This
asks the question that follows: does it have to be, and how would we know if a
cheaper verifier were good enough. It replays findings the survey has already
recorded verdicts for, puts them to two reviewing agents under the same
contract, and scores both against the record.

**An arm is a model AND a harness, and the pair is what gets measured.** The two
arms are separate CLIs, so a verdict gap is not attributable to the model alone.
What narrows it here is that neither arm gets tools: the pinned source is inlined
into the prompt and both run in an empty working directory, so the payload is
byte-identical and is the whole world. That is corpus-manifest.json's rule for
candidates applied one layer up, and it costs something real -- the evidence set
is fixed in advance instead of chosen by the verifier, which is not how the
standing supervisor works in production. Say which arm, not which model, in
anything written from this.

**The pin must be a history-free export, not a git worktree.** A worktree shares
.git with the parent, and in the oxbox case the very next commit after the pin
(0090c35) names both real defects in its subject line. Build the tree with
`git archive <pin> | tar -x -C <dir>`; `build` refuses a directory with a .git
in it.

**The key is not independent of the Claude arm.** The recorded verdicts were
reached by Claude agents. Agreement with them is therefore worth less on the
Claude side than on the other, and the number that carries real information is
the disagreement list -- the rows where the two arms differ, which a human reads
and settles. `score` prints that list first for exactly that reason.
"""

import argparse
import collections
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KEY = os.path.join(HERE, "corpora", "answers", "oxbox-clean-control-verdicts.json")
PROMPT = os.path.join(HERE, "corpora", "prompts", "verify-findings.txt")

# The evidence a verifier is allowed to reach, inlined into every batch. This
# list is the experiment's main compromise and is stated rather than hidden: a
# verifier that roams chooses its own evidence, and two verifiers that roam
# differently produce a verdict gap nobody can attribute. Fixing the set makes
# the payload byte-identical across arms -- corpus-manifest.json's rule for
# candidates, applied one layer up -- at the price of pre-deciding what is worth
# reading. The set is every file the recorded verdicts actually cite.
EVIDENCE = ["jailtest.py", "oxbox", "profiles/jail.sb", "guardtest.py", ".gitignore"]

# An arm is a command template plus how that CLI wants its prompt.
#
# Neither arm gets tools. Both run with an empty working directory, so even a
# tool call that slipped through would find nothing: the payload is the whole
# world. This is what makes a verdict difference the model's rather than the
# harness's -- and it is also the only shape agy runs in headlessly, since it
# reaches for a shell command to read a file and headless mode auto-denies the
# "command" permission with no way to prompt.
#
# The prompt goes to claude on stdin and to agy attached to --print. That is not
# a preference: agy's flag parser takes the next argv element as --print's value,
# so a bare --print eats whatever flag follows it and drops the real prompt.
# The ox arms are the ones that can be priced. A subscription CLI reports no
# tokens -- agy publishes none at all -- so the arms below it can be compared for
# accuracy and not for cost, which is the wrong way round for a question that is
# entirely about cost. Through ox the venue's own usage accounting comes back in
# status.json, `costcheck.py` prices it from the archived catalog, and the source
# rides as --files so context_bytes is recorded the way every corpus run records
# it. ox is also toolless by construction, so "control tool use" costs nothing to
# arrange: there is no tool to control.
#
# Effort is each model's OWN default, not a matched level: gemini-3.8-flash is
# medium, claude-opus-5 is high, per reasoning.default_effort in the catalog.
# The question is what a supervisor actually costs to run, and a matched rung
# would price a setting nobody would choose.
#
# The send command is resolved from PATH as `oxbox send`: oxbox 0.7.0
# (2026-09-06) renamed `ox` and put the script off PATH, and that release is
# the first Homebrew build with the full effort ladder, so the checkout path
# this used to pin (chosen on 2026-09-03 because the brew `ox` then lacked
# `medium`) is no longer needed and no longer exists. The tripwire below still
# reads the level from meta.json, because a build that silently dropped an
# effort would run at its default without failing.
OX = ["oxbox", "send"]

# The scratch build the local arms use; see the note on those arms. It is not
# installed and not on PATH, so the path is given at run time.
LOCAL_SEND = [os.environ.get("VERIFIERCHECK_LOCAL_SEND", "./oxbox-send-http")]

# Where the local arms reach ollama. The host is deliberately NOT written down:
# it is a machine on a private network, and this repository is public. Set
# VERIFIERCHECK_OLLAMA_URL to the OpenAI-compatible chat-completions endpoint --
# the full URL, not a prefix, because oxbox uses --base-url as the endpoint
# itself.
OLLAMA_URL = os.environ.get("VERIFIERCHECK_OLLAMA_URL",
                            "http://localhost:11434/v1/chat/completions")

ARMS = {
    "opus": {
        "key_author": "claude-opus-5",
        "model": "claude-opus-5",
        "harness": "claude-code-cli",
        "priced": False,
        "prompt": "stdin",
        "cmd": [
            "claude", "-p", "--model", "opus",
            "--permission-mode", "manual",
            "--permission-prompts", "none",
        ],
    },
    "gemini": {
        "model": "gemini-3.8-flash-medium",
        "harness": "agy-cli",
        "priced": False,
        "prompt": "--print={prompt}",
        "cmd": [
            "agy", "--model", "gemini-3.8-flash-medium",
            "--effort", "medium",
            "--output-format", "text",
            "--disable-slash-commands",
            "--print-timeout", "10m",
        ],
    },
    "or-opus": {
        "checks_own": ["anthropic/claude-opus-5"],
        "key_author": "claude-opus-5",
        "model": "anthropic/claude-opus-5",
        "harness": "ox-openrouter",
        "priced": True,
        "effort": "high",
        "max_tokens": "128000",
        "evidence": "files",
    },
    "or-gemini": {
        "model": "google/gemini-3.8-flash",
        "harness": "ox-openrouter",
        "priced": True,
        "effort": "medium",
        "max_tokens": "65536",
        "evidence": "files",
    },
    # The price ceiling, and the arm with a conflict of interest. Fable 5.1 is
    # $10/$50 -- 2x Opus 5, 13x gemini-3.8-flash -- and it was the survey's first
    # standing supervisor before the job was moved to Opus on price.
    #
    # It therefore WROTE 11 of the 15 rows it is scored against: the sonnet,
    # gemini-3.7 and gpt batches carry `agent: claude-fable-5-1`, and only the
    # deepseek and glm batches (L1-L4) were Opus's. Its agreement score is
    # circular by construction and must not be read as accuracy.
    #
    # It is worth running anyway, for the one thing only this arm can test: P2 is
    # Fable's own prior verdict, reached WITH tools and the whole repository, and
    # every arm so far has refuted it. If Fable toolless also refutes it, the key
    # row is a judgment its own author will not reproduce, and four arms have not
    # missed anything -- the key has.
    "or-fable": {
        "checks_own": ["anthropic/claude-fable-5.1"],
        "key_author": "claude-fable-5-1",
        "model": "anthropic/claude-fable-5.1",
        "harness": "ox-openrouter",
        "priced": True,
        "effort": "high",
        "max_tokens": "128000",
        "evidence": "files",
        "wrote_key_rows": ["S1", "S2", "G1", "P1", "P2", "P3", "P4", "P5", "P6",
                           "P7", "P8"],
    },

    # ---- The cheap checkers -------------------------------------------------
    #
    # The quadrant nobody has run. costcheck.py and the 2026-09-11 special
    # edition both put the bill in the checking half -- GLM-5.3 Flash's own run
    # on this fixture cost $0.0015 and the Opus 5 check of its findings cost 16
    # cents -- so the arms that matter for cost are the ones sitting where Opus
    # sits, not where the candidate sits. These two are the manifest's cheap
    # paid tier, and they are already the production refuter: observations/
    # README.md's checking order puts "a model in the manifest's cheap paid
    # tier" between reproduction and the metered frontier read.
    #
    # Each runs at its OWN default_effort from the 2026-09-20 catalog, as the
    # arms above do -- glm at max, deepseek at high -- because the question is
    # what a supervisor costs to run and a matched rung prices a setting nobody
    # would choose.
    #
    # The cap is 32,768 and not the catalog's maximum, which is the one place
    # these arms deviate from the frontier arms above, and the record is the
    # reason: deepseek-v4-flash spent a whole budget reasoning on this very
    # fixture and returned nothing in 33 minutes (2026-09-06), and a gateway
    # budgets about 80 percent of max_tokens for thinking at high effort. A
    # 131,072-token cap authorizes a 100,000-token thought. A checker that
    # cannot answer inside 32K on a batch of at most a dozen findings is not a
    # cheap checker, and recording that is the measurement, not a failure of it.
    #
    # Both are provider-pinned to the routes in manifests/oxbox-manifest-2026-09-20.json.
    # That is not tidiness: the first unpinned refuter request of 2026-09-11
    # landed on a provider that reasoned for 13k tokens and returned an error
    # after five minutes, and the same batch pinned answered in a minute.
    "or-glm": {
        "checks_own": ["z-ai/glm-5.3-flash"],
        "model": "z-ai/glm-5.3-flash",
        "harness": "ox-openrouter",
        "priced": True,
        "effort": "max",
        "max_tokens": "32768",
        "evidence": "files",
        "provider": {"only": ["z-ai/fp8", "gmicloud/fp8", "streamlake/fp8"],
                     "allow_fallbacks": False,
                     "max_price": {"prompt": 0.15, "completion": 0.5}},
    },
    "or-deepseek": {
        "checks_own": ["deepseek/deepseek-v4-flash"],
        "model": "deepseek/deepseek-v4-flash",
        "harness": "ox-openrouter",
        "priced": True,
        "effort": "high",
        "max_tokens": "32768",
        "evidence": "files",
        "provider": {"only": ["streamlake/fp8", "digitalocean"],
                     "allow_fallbacks": False,
                     "max_price": {"prompt": 0.098, "completion": 0.196}},
    },

    # ---- The free pool ------------------------------------------------------
    #
    # Priced arms in name only: both bill zero, so `priced` is False and they
    # appear in the accuracy tables and not the cost ones. Reporting a $0.0000
    # row beside a real bill invites a reader to add them up, and a free arm's
    # actual cost is a latency and a training-on-input risk, neither of which
    # is a dollar.
    #
    # Chosen because they ANSWERED this fixture as candidates. The free pool's
    # characteristic failure here is silence, not error: north-mini-code:free
    # timed out at 900 seconds twice in an hour (2026-09-08) and
    # ling-3.0-flash-fin:free spent its whole 32K cap reasoning and returned
    # nothing. Its sibling ling-3.0-flash-vl:free finished the same fixture on
    # 2026-09-20, which is why that tag and not the fin one is here.
    "free-ling-vl": {
        "model": "inclusionai/ling-3.0-flash-vl:free",
        "harness": "ox-openrouter",
        "priced": False,
        "effort": "medium",
        "max_tokens": "32768",
        "evidence": "files",
    },
    "free-dots": {
        "model": "dots-studio/dots-3-note-preview:free",
        "harness": "ox-openrouter",
        "priced": False,
        "effort": "medium",
        "max_tokens": "32768",
        "evidence": "files",
    },

    # ---- Local, on the GPU host ---------------------------------------------
    #
    # ollama on the local GPU host through oxbox's --base-url, which needs
    # --api-key-env even for a host that wants no credential, so a dummy variable is named rather than
    # the flag being skipped: oxbox refuses to send a key to an unlisted host by
    # default and that refusal is worth keeping.
    #
    # The RELEASED oxbox refuses a plain-http --base-url outright ("a credential
    # must not travel in cleartext"), which is correct for the internet and
    # wrong for a GPU box on the LAN that serves no TLS. The local arms
    # therefore run a scratch oxbox-send whose ONLY change is that one guard;
    # LOCAL_SEND below names it, and it is not on PATH and is not installed.
    # Everything else -- the audit log, the secret scan, the status file -- is
    # the released code, so a local run is recorded exactly as a hosted one is.
    # If that scratch build is missing, the local arms fail loudly rather than
    # falling back to something unrecorded.
    #
    # Temperature 1.0, not the 0.2 the hosted arms send. Every vendor card for
    # these open-weight thinking models sets 1.0, three of them name low
    # temperature as a cause of endless repetition, and the 2026-09-10 batch
    # watched gemma4:26b and gpt-oss:20b loop away a 100,000-token cap at 0.2
    # and return nothing. That makes the local arms NOT byte-identical in
    # sampling to the hosted ones, which is a stated compromise and not an
    # oversight: at 0.2 there is no local arm to compare at all.
    #
    # The -64k tags are the context-extended builds registered for the v2 runs;
    # the untagged ones carry ollama's default window and truncate the evidence.
    "local-qwen38": {
        "checks_own": ["qwen3.8:27b"],
        "model": "qwen3.8:27b-64k",
        "harness": "ox-ollama",
        "priced": False,
        "effort": "medium",
        "max_tokens": "32768",
        "temperature": "1.0",
        "evidence": "files",
        "base_url": OLLAMA_URL,
        "api_key_env": "OLLAMA_API_KEY",
        "send": LOCAL_SEND,
    },
    "local-gptoss": {
        "model": "gpt-oss:20b-64k",
        "harness": "ox-ollama",
        "priced": False,
        "effort": "medium",
        "max_tokens": "32768",
        "temperature": "1.0",
        "evidence": "files",
        "base_url": OLLAMA_URL,
        "api_key_env": "OLLAMA_API_KEY",
        "send": LOCAL_SEND,
    },
    "local-gemma4": {
        "model": "gemma4:26b-64k",
        "harness": "ox-ollama",
        "priced": False,
        "effort": "medium",
        "max_tokens": "32768",
        "temperature": "1.0",
        "evidence": "files",
        "base_url": OLLAMA_URL,
        "api_key_env": "OLLAMA_API_KEY",
        "send": LOCAL_SEND,
    },
}


def ox_command(arm, pin, stem):
    """One ox invocation, wrapped in `op run` so the key never enters argv.

    --force is here for two lines in guardtest.py and nothing else. ox's secret
    scan flags `guardtest.py:240` and `:242`; both are fixtures the file needs in
    order to assert that ox REFUSES them -- 240 is a sequential-alphabet dummy
    (`sk-abc...012345`) and 242 is `AKIAIOSFODNN7EXAMPLE`, the example key id
    published in AWS's own documentation. Verified by reading them, 2026-09-03.

    This is a standing override on a fixed file set and it is only safe while
    that set is fixed. If EVIDENCE changes, dry-run once WITHOUT --force and
    read what the scanner reports before restoring it; --force suppresses a real
    leak exactly as willingly as a false positive.
    """
    files = ",".join(os.path.join(pin, name) for name in EVIDENCE)

    # A local arm reaches ollama on the GPU host over --base-url and needs no
    # OpenRouter credential, so it is not wrapped in `op run`. oxbox still
    # demands --api-key-env for an unlisted host -- it will not send a key
    # somewhere it does not know by default -- so a dummy variable is named.
    # `run` puts an empty value in the environment for it.
    local = arm.get("base_url")
    prefix = [] if local else ["op", "run", "--env-file", ".env", "--"]
    venue = [] if local else ["--venue", "openrouter"]
    endpoint = (["--base-url", arm["base_url"],
                 "--api-key-env", arm["api_key_env"]] if local else [])

    # Provider routing rides as one JSON object, sent verbatim. Pinning is the
    # survey's rule since oxbox 1.1.0 and it does double duty here: it fixes
    # attribution to a named endpoint, and its max_price guard refuses a route
    # that has repriced above what the manifest was judged on rather than
    # quietly billing it.
    routing = (["--provider", json.dumps(arm["provider"], sort_keys=True)]
               if arm.get("provider") else [])

    return [
        *prefix,
        *(arm.get("send") or OX),
        "--force",
        *venue,
        *endpoint,
        "--model", arm["model"],
        *routing,
        "--effort", arm["effort"],
        "--max-tokens", arm["max_tokens"],
        # 0.2 for the hosted arms, as every arm above sends; the local arms
        # override to the 1.0 their vendor cards set, for the reason recorded
        # beside them.
        "--temperature", arm.get("temperature", "0.2"),
        "--mode", "ask",
        "--files", files,
        "--stdin",
        "--status-file", stem + ".status.json",
        "--output", stem + ".raw.txt",
        # Without this ox writes its audit log under the CWD, which for these
        # runs is the survey repo -- an untracked logs/ appearing in a clean
        # tree. Verifier runs are not corpus runs and do not belong in the
        # oxbox log either; they live beside the rest of the run's artifacts.
        "--log-dir", os.path.join(os.path.dirname(stem), "ox-logs"),
    ]


def load_key():
    with open(KEY, encoding="utf-8") as handle:
        return json.load(handle)


def slug(batch):
    """Short local name for a batch. Never sent to a verifier.

    The model id alone is NOT unique: z-ai/glm-5.3-flash ran this fixture
    twice, as a baseline on 2026-09-02 and as a candidate on 2026-09-06, and
    both are in the key. Two batches sharing a name share their artifact
    paths, so the second run silently overwrites the first and `score` reads
    one arm's verdicts as the other's. A batch therefore carries an explicit
    `name` wherever the model id would collide.
    """
    if isinstance(batch, dict):
        return batch.get("name") or batch["model"].split("/")[-1]
    return batch.split("/")[-1]


def build_evidence(pin):
    """The pinned source, inlined once and shared by every batch."""
    parts = ["-----8<----- begin source at the pin -----8<-----", ""]
    for name in EVIDENCE:
        path = os.path.join(pin, name)
        with open(path, encoding="utf-8") as handle:
            body = handle.read()
        parts.append("===== %s (%d bytes) =====" % (name, len(body.encode("utf-8"))))
        parts.append(body.rstrip())
        parts.append("")
    parts.append("-----8<----- end source -----8<-----")
    return "\n".join(parts) + "\n"


def build_batch(batch, logs):
    """The bytes a verifier sees: an id index, then the findings verbatim.

    The index exists so two arms segment the batch identically. Models number
    their findings inconsistently -- eight numbered items from one, a single
    unnumbered `### Defect:` heading from another -- and a verifier left to
    segment for itself produces a verdict list that cannot be lined up with
    another verifier's. The labels are neutral restatements of each claim and
    carry no verdict; the verbatim text below them is the authority.
    """
    content_path = os.path.join(logs, batch["content"].split("logs/")[-1])
    with open(content_path, encoding="utf-8") as handle:
        content = handle.read()

    lines = [
        "# Findings batch",
        "",
        "%d finding(s) from a code review of jailtest.py, whose source is included"
        % len(batch["findings"]),
        "below along with the launcher, the sandbox profile and the companion test",
        "the findings refer to. Return exactly one verdict for each id below, in",
        "this order:",
        "",
    ]
    if batch["findings"]:
        for finding in batch["findings"]:
            lines.append("  %s  %s" % (finding["id"], finding["label"]))
    else:
        lines.append("  (none -- the review reported no defects)")
        lines.append("")
        lines.append('Return {"verdicts": []} and nothing else.')
    lines += [
        "",
        "The reviewer's own words follow, unedited. The index above exists only to",
        "fix the ids and their order; where it and the text below differ, the text",
        "below is what you are verifying.",
        "",
        "-----8<----- begin review -----8<-----",
        content.rstrip(),
        "-----8<----- end review -----8<-----",
    ]
    return "\n".join(lines) + "\n"


def cmd_build(args):
    if os.path.isdir(os.path.join(args.pin, ".git")):
        sys.stderr.write(
            "verifiercheck: %s has a .git -- a verifier can read the fix commit "
            "there. Use `git archive <pin> | tar -x -C <dir>` instead.\n" % args.pin
        )
        return 2
    key = load_key()
    os.makedirs(args.work, exist_ok=True)
    with open(PROMPT, encoding="utf-8") as handle:
        contract = handle.read()
    evidence = build_evidence(args.pin)
    for batch in key["batches"]:
        name = slug(batch)
        findings = build_batch(batch, args.logs)
        # Two shapes of the same batch. The CLI arms have no way to attach a
        # file, so the source is inlined; ox attaches it with --files and
        # records context_bytes, so its copy carries the findings alone. The
        # two are not byte-comparable to each other and results from them are
        # not pooled -- each generation is compared within itself.
        for suffix, text in (("", contract + "\n\n" + evidence + "\n" + findings),
                             (".nofiles", contract + "\n\n" + findings)):
            out = os.path.join(args.work, "batch-%s%s.txt" % (name, suffix))
            with open(out, "w", encoding="utf-8") as handle:
                handle.write(text)
            print("%-22s %-9s %2d finding(s)  %6d B"
                  % (name, suffix or "inlined", len(batch["findings"]), len(text)))
    print("\npin: %s" % args.pin)
    print("evidence attached by ox: %s" % ", ".join(EVIDENCE))
    return 0


def extract_json(text):
    """Pull the verdict object out of a reply that may be wrapped in prose."""
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.S)
    if fence:
        text = fence.group(1)
    start = text.find("{")
    while start != -1:
        depth, in_str, esc = 0, False, False
        for i in range(start, len(text)):
            ch = text[i]
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
                        return json.loads(text[start:i + 1])
                    except ValueError:
                        break
        start = text.find("{", start + 1)
    return None


def cmd_run(args):
    key = load_key()
    arm = ARMS[args.arm]
    names = [slug(b) for b in key["batches"]]
    todo = names if args.all else [args.batch]
    unknown = [n for n in todo if n not in names]
    if unknown:
        sys.stderr.write("verifiercheck: no such batch: %s\n" % ", ".join(unknown))
        return 2

    os.makedirs(args.work, exist_ok=True)
    # Both arms run here: an empty directory, so a tool call that slipped past
    # the flags would still find nothing to read. The payload is the whole world.
    empty = os.path.join(args.work, "empty-cwd")
    os.makedirs(empty, exist_ok=True)
    failures = 0
    for name in todo:
        stem = os.path.join(args.work, "%s-%s" % (args.arm, name))
        env = None
        is_ox = arm.get("evidence") == "files"
        batch_path = os.path.join(
            args.work, "batch-%s%s.txt" % (name, ".nofiles" if is_ox else ""))
        if not os.path.exists(batch_path):
            sys.stderr.write("verifiercheck: %s missing; run `build` first\n"
                             % batch_path)
            return 2
        with open(batch_path, encoding="utf-8") as handle:
            prompt = handle.read()
        if is_ox:
            if not args.pin:
                sys.stderr.write("verifiercheck: an ox arm needs --pin\n")
                return 2
            cmd, stdin, cwd = ox_command(arm, args.pin, stem), prompt, HERE
            if arm.get("api_key_env"):
                env = dict(os.environ)
                env.setdefault(arm["api_key_env"], "ollama")
        else:
            cmd, stdin, cwd = list(arm["cmd"]), None, empty
            if arm["prompt"] == "stdin":
                stdin = prompt
            else:
                cmd.append(arm["prompt"].format(prompt=prompt))
        sys.stderr.write("verifiercheck: arm=%s batch=%s bytes=%d\n"
                         % (args.arm, name, len(prompt)))
        try:
            proc = subprocess.run(
                cmd, input=stdin, cwd=cwd, capture_output=True,
                text=True, timeout=args.timeout, check=False, env=env,
            )
        except subprocess.TimeoutExpired:
            sys.stderr.write("verifiercheck: arm=%s batch=%s TIMEOUT after %ds\n"
                             % (args.arm, name, args.timeout))
            failures += 1
            continue

        # ox writes the answer to --output itself and keeps stdout for its
        # banner; the CLI arms answer on stdout. Always keep stderr for an ox
        # run even on success -- the banner carries model, effort and the token
        # line, and it is the only place the venue's own framing survives.
        if is_ox:
            with open(stem + ".stderr.txt", "w", encoding="utf-8") as handle:
                handle.write(proc.stderr)
            reply = ""
            if os.path.exists(stem + ".raw.txt"):
                with open(stem + ".raw.txt", encoding="utf-8") as handle:
                    reply = handle.read()
        else:
            reply = proc.stdout
            with open(stem + ".raw.txt", "w", encoding="utf-8") as handle:
                handle.write(reply)
        if proc.returncode != 0:
            with open(stem + ".stderr.txt", "w", encoding="utf-8") as handle:
                handle.write(proc.stderr)
            sys.stderr.write("verifiercheck: arm=%s batch=%s exit=%d, stderr kept\n"
                             % (args.arm, name, proc.returncode))
            failures += 1
            continue
        parsed = extract_json(reply)
        if parsed is None:
            sys.stderr.write("verifiercheck: arm=%s batch=%s produced no JSON; "
                             "raw reply kept at %s.raw.txt\n" % (args.arm, name, stem))
            failures += 1
            continue
        with open(stem + ".json", "w", encoding="utf-8") as handle:
            json.dump(parsed, handle, indent=2)
        if is_ox:
            got = resolved_effort(read_status(stem))
            if got != arm["effort"]:
                sys.stderr.write(
                    "verifiercheck: arm=%s batch=%s WENT OUT AT effort=%s, "
                    "wanted %s -- the run is at the wrong rung and its cost is "
                    "not comparable\n" % (args.arm, name, got, arm["effort"]))
                failures += 1
        print("%-10s %-22s %d verdict(s)%s"
              % (args.arm, name, len(parsed.get("verdicts", [])),
                 "  " + token_line(stem) if arm["priced"] else ""))
    return 1 if failures else 0


PRICES = {
    # USD per token, from the live OpenRouter catalog on 2026-09-03. Kept here
    # rather than read from catalogs/ because gemini-3.8-flash post-dates the
    # newest archived capture (2026-09-01); the next ./oxsurvey run supersedes
    # this and the figures should be recomputed from the archive then.
    "anthropic/claude-opus-5": (5.0e-6, 25.0e-6),
    "anthropic/claude-fable-5.1": (10.0e-6, 50.0e-6),
    "google/gemini-3.8-flash": (0.75e-6, 3.75e-6),
    # Added 2026-09-20 for the cheap arms, from catalogs/openrouter/2026-09-20.json.
    # Without them `priced` returns None and the cheap arms' usd column reads
    # $0.0000 against a real venue bill -- which reads as "free" rather than as
    # "not in the table", and is the more dangerous of the two errors here.
    "z-ai/glm-5.3-flash": (0.09e-6, 0.30e-6),
    "deepseek/deepseek-v4-flash": (0.03724e-6, 0.07448e-6),
}


def read_status(stem):
    path = stem + ".status.json"
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def resolved_effort(status):
    """The effort level the request actually went out at, from the run's log.

    Not the flag that was typed. `meta.json`'s effort field records the level ox
    resolved to, which is the only thing that survives the ways a run can go out
    at the wrong rung. Passing --effort as a flag fails loudly on an ox that does
    not know the level, but an effort set through a manifest entry is silently
    ignored by an older ox and resolves to its built-in default -- a completed,
    priced, plausible run at a rung nobody chose, with nothing in stderr to say
    so. Checking the log catches both, and catches a tree that moved underneath
    the run, which no promise from anyone else can.
    """
    if not status or not status.get("log_dir"):
        return None
    path = os.path.join(status["log_dir"], "meta.json")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as handle:
        return json.load(handle).get("effort")


def venue_cost(status):
    """What the venue itself says the run cost, from usage.cost in its reply.

    OpenRouter populates this on every response and ox does not ask for it --
    none of these runs' request.json carries a `usage` key. An oxbox handoff
    records the opposite as a dead end; it is wrong, verified across eleven runs
    on 2026-09-03.

    It is recorded BESIDE the catalog figure and does not replace it. A price
    derived from an archived catalog is reproducible -- anyone can recompute it
    from bytes in this repo -- while a number read off a live response cannot be
    checked later by anyone who was not there. The venue's figure is worth having
    as its own claim, and as a check: across ten successful runs the two agreed
    to the cent, which is the only independent test costcheck.py's pricing has.
    """
    # ox records it in status.json from oxbox e8d722b on. Runs made before that
    # -- including the ten this experiment is built on -- have no such key, so
    # the response body stays the fallback. `in` rather than `.get()`: the field
    # is None when the venue sent nothing and 0 when a run genuinely billed
    # nothing, and those are different facts.
    if status and "venue_cost" in status:
        return status["venue_cost"]
    if not status or not status.get("log_dir"):
        return None
    path = os.path.join(status["log_dir"], "response.json")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as handle:
        return ((json.load(handle).get("usage") or {}).get("cost"))


def priced(model, status):
    """USD for one ox run. Computed from the catalog, never billed."""
    rates = PRICES.get(model)
    if not rates or not status or status.get("prompt_tokens") is None:
        return None
    prompt = status.get("prompt_tokens") or 0
    completion = status.get("completion_tokens") or 0
    return prompt * rates[0] + completion * rates[1]


def token_line(stem):
    status = read_status(stem)
    if not status:
        return "(no status)"
    usd = priced(status.get("model", ""), status)
    return "prompt=%s completion=%s%s" % (
        status.get("prompt_tokens"), status.get("completion_tokens"),
        " usd=$%.4f" % usd if usd is not None else "")


def read_arm(work, arm, name):
    path = os.path.join(work, "%s-%s.json" % (arm, name))
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    return {v.get("id"): v for v in data.get("verdicts", [])}


# The two ensemble shapes, scored as arms so they land in every table the real
# arms do. Neither is adopted by scoring well here: an ensemble measured on a
# replay is measured against a past judgment, and the bar in docs/decisions.md
# ("Comparing verifiers") still asks for a batch with no key.
#
# CASCADE is the survey's own production rule, written down in
# observations/README.md's checking order: put a batch to a cheap refuter, let
# a REFUTED verdict stand, and send only what it CONFIRMED or left UNCERTAIN to
# the metered frontier. It is asymmetric on purpose -- it spends money on the
# findings that would cost a reader time, and nothing on the ones the cheap arm
# already killed -- and its exposure is precisely a cheap arm that refutes a
# real defect, because nothing downstream ever sees that row.
#
# DISAGREE is the shape a two-agent hand-off falls into: run both, act on what
# they agree about, escalate where they differ. It is scored here because the
# user asked whether it generalizes, and the honest answer on this record is in
# the numbers: P2 is a row where two independent arms agreed and were both
# wrong, so a disagreement router escalates it never and inherits the error at
# full confidence. Agreement is not a second opinion when the two readers share
# a prior.
ROUTER_SHAPES = ("cascade", "disagree")


def router_verdicts(rows, shape, cheap, escalate):
    """Synthetic verdict per row, plus the batches that had to escalate.

    A row where any component arm is missing stays '-': absent data is not an
    ensemble decision, and filling it in would let an unfinished run score.
    """
    verdicts, escalated = {}, set()
    for index, row in enumerate(rows):
        parts = [row[arm] for arm in cheap]
        if "-" in parts or row[escalate] == "-":
            verdicts[index] = "-"
            continue
        if shape == "cascade":
            # One refuter by contract; a cascade over two is a different
            # procedure and is not what the checking order describes.
            cheap_verdict = parts[0]
            if cheap_verdict == "REFUTED":
                verdicts[index] = cheap_verdict
                continue
        else:
            if len(set(parts)) == 1:
                verdicts[index] = parts[0]
                continue
        verdicts[index] = row[escalate]
        escalated.add(row["batch"])
    return verdicts, escalated


def router_cost(work, batches, cheap, escalate, escalated):
    """What the router billed: every cheap run, plus escalated batches.

    Escalation is charged a WHOLE batch of the escalation arm, not a share of
    one. The evidence payload is the five pinned files and it dominates the
    prompt, so a batch that escalates one finding re-sends all of it. A
    row-proportional figure would be cheaper and would describe a pipeline that
    does not exist.

    An unpriced cheap arm contributes zero, because it billed zero. That makes
    the router's dollar figure the escalation arm's bill alone, which is the
    true statement about a free or local refuter -- its own cost is a latency,
    and a latency does not belong in a column of dollars.
    """
    total = 0.0
    for batch in batches:
        name = slug(batch)
        for arm in cheap:
            if not ARMS.get(arm, {}).get("priced"):
                continue
            status = read_status(os.path.join(work, "%s-%s" % (arm, name)))
            total += (priced(ARMS[arm]["model"], status) or 0.0) if status else 0.0
        if name in escalated and ARMS.get(escalate, {}).get("priced"):
            status = read_status(os.path.join(work, "%s-%s" % (escalate, name)))
            total += (priced(ARMS[escalate]["model"], status) or 0.0) if status else 0.0
    return total


def cmd_score(args):
    key = load_key()
    arms = args.arms.split(",")
    rows, missing, extra = [], [], []
    for batch in key["batches"]:
        name = slug(batch)
        got = {arm: read_arm(args.work, arm, name) for arm in arms}
        for arm, verdicts in got.items():
            if verdicts is None:
                missing.append("%s/%s" % (arm, name))
                continue
            ids = {f["id"] for f in batch["findings"]}
            for vid in verdicts:
                if vid not in ids:
                    extra.append("%s/%s invented id %r" % (arm, name, vid))
        for finding in batch["findings"]:
            row = {"batch": name, "id": finding["id"],
                   "accept": finding["accept"], "recorded": finding["recorded"],
                   "defect": finding.get("defect"),
                   "verified_by": finding.get("verified_by") or []}
            for arm in arms:
                verdicts = got.get(arm) or {}
                entry = verdicts.get(finding["id"])
                row[arm] = (entry or {}).get("verdict", "-")
                row[arm + ":why"] = (entry or {}).get("reason", "")
            rows.append(row)

    # The routers are synthesized from columns that already exist, so they cost
    # nothing to add and cannot disagree with their own components about what a
    # verdict was. They are appended to the accuracy tables and deliberately
    # kept OUT of the disagreement list below, which is about what two readers
    # of the source actually said.
    routers = []
    for spec in (args.router or []):
        try:
            shape, rest = spec.split(":", 1)
            cheap_spec, escalate = rest.split(">", 1)
        except ValueError:
            sys.stderr.write("verifiercheck: --router wants shape:cheap>escalate,"
                             " e.g. cascade:or-glm>or-opus\n")
            return 2
        cheap = cheap_spec.split(",")
        if shape not in ROUTER_SHAPES:
            sys.stderr.write("verifiercheck: no such router shape: %s\n" % shape)
            return 2
        if shape == "disagree" and len(cheap) < 2:
            sys.stderr.write("verifiercheck: a disagree router needs two cheap arms\n")
            return 2
        unknown = [a for a in cheap + [escalate] if a not in arms]
        if unknown:
            sys.stderr.write("verifiercheck: --router names arms that are not "
                             "scored: %s (add them to --arms)\n" % ", ".join(unknown))
            return 2
        label = "%s/%s" % (shape[:4], "+".join(a.split("-")[-1] for a in cheap))
        verdicts, escalated = router_verdicts(rows, shape, cheap, escalate)
        for index, row in enumerate(rows):
            row[label] = verdicts[index]
            row[label + ":why"] = ""
        routers.append({"label": label, "shape": shape, "cheap": cheap,
                        "escalate": escalate, "escalated": escalated,
                        "spec": spec})

    columns = arms + [r["label"] for r in routers]

    # A row missing an arm's verdict is absent data, not a disagreement; counting
    # it as one turns an unfinished run into a finding.
    scorable = [r for r in rows if all(r[a] != "-" for a in arms)]
    disputed = [r for r in scorable if len({r[a] for a in arms}) > 1]
    print("## Disagreements  (%d of %d findings both arms scored)\n"
          % (len(disputed), len(scorable)))
    if not disputed:
        print("None. The two arms returned the same verdict on every finding.\n")
    for row in disputed:
        marks = "  ".join("%s=%s" % (a, row[a]) for a in arms)
        agrees = [a for a in arms if row[a] in row["accept"]]
        print("%-16s %-4s %s   key=%s (%s)"
              % (row["batch"], row["id"], marks,
                 "|".join(row["accept"]), row["recorded"]))
        print("   key agrees with: %s" % (", ".join(agrees) if agrees else "neither"))
        for arm in arms:
            if row[arm + ":why"]:
                print("   %-8s %s" % (arm, row[arm + ":why"][:300]))
        print("")

    print("## Against the recorded key\n")
    head = "%-10s %5s %5s %5s %5s" % ("arm", "n", "ok", "miss", "false")
    print(head)
    print("-" * len(head))
    for arm in columns:
        scored = [r for r in rows if r[arm] != "-"]
        ok = [r for r in scored if r[arm] in r["accept"]]
        # A miss is a real defect called REFUTED; a false is an invention
        # called CONFIRMED. They are not the same mistake and a single
        # accuracy number hides which one an arm makes.
        miss = [r for r in scored
                if "CONFIRMED" in r["accept"] and r[arm] == "REFUTED"]
        false = [r for r in scored
                 if r["accept"] == ["REFUTED"] and r[arm] == "CONFIRMED"]
        print("%-10s %5d %5d %5d %5d"
              % (arm, len(scored), len(ok), len(miss), len(false)))
    print("\nmiss  = a defect the key calls real, refuted by the arm")
    print("false = an invention the key refutes, confirmed by the arm")

    # An arm that wrote a key row cannot be scored on it. The key's verdicts
    # were reached by Fable 5.1 and Opus 5, so those two are marking their own
    # homework on most of this corpus -- and after the 2026-09-20 extension
    # nearly every new row is theirs. The cheap arms author nothing here, which
    # is the one structural advantage they have in this comparison and has to
    # be said out loud rather than left to flatter them.
    # Matched on the arm's declared key_author, not on a string mangled out of
    # its model id: "anthropic/claude-fable-5.1" and "claude-fable-5-1" are the
    # same model spelled two ways, and a heuristic that got that wrong would
    # silently hand an arm credit for rows it wrote.
    authored = {}
    for arm in columns:
        author = ARMS.get(arm, {}).get("key_author")
        authored[arm] = ([r for r in rows if author in r["verified_by"]]
                         if author else [])
    # An arm checking a batch its OWN model emitted is a second conflict, and a
    # different one from writing the key: here the arm is not marking its own
    # marking, it is judging its own work. Five arms have one such batch each,
    # and for a cheap arm it is the batch most likely to flatter it -- a model
    # that reproduces its own reasoning will confirm its own invention. Scored
    # separately rather than dropped, because the size of the effect is itself
    # worth knowing.
    own_rows = {}
    for arm in columns:
        own_models = ARMS.get(arm, {}).get("checks_own") or []
        own_names = {slug(b) for b in key["batches"] if b["model"] in own_models}
        own_rows[arm] = [r for r in rows if r["batch"] in own_names]
    if any(own_rows[a] for a in columns):
        print("\n## The same score, with the arm's own batch left out\n")
        head = "%-10s %9s %8s %9s %9s" % ("arm", "own rows", "left", "ok", "of left")
        print(head)
        print("-" * len(head))
        for arm in columns:
            if not own_rows[arm]:
                continue
            mine = {id(r) for r in own_rows[arm]}
            left = [r for r in rows if id(r) not in mine and r[arm] != "-"]
            ok = [r for r in left if r[arm] in r["accept"]]
            print("%-10s %9d %8d %9d %9s"
                  % (arm, len(own_rows[arm]), len(left), len(ok),
                     "%.0f%%" % (100.0 * len(ok) / len(left)) if left else "n/a"))
        print("\nown rows = findings this arm's own model emitted as a candidate.")

    if any(authored[a] for a in columns):
        print("\n## The same score, on rows the arm did not write\n")
        head = "%-10s %7s %7s %9s %9s" % ("arm", "wrote", "left", "ok", "of left")
        print(head)
        print("-" * len(head))
        for arm in columns:
            mine = {id(r) for r in authored[arm]}
            left = [r for r in rows if id(r) not in mine and r[arm] != "-"]
            ok = [r for r in left if r[arm] in r["accept"]]
            print("%-10s %7d %7d %9d %9s"
                  % (arm, len(authored[arm]), len(left), len(ok),
                     "%.0f%%" % (100.0 * len(ok) / len(left)) if left else "n/a"))
        print("\nwrote = key rows this arm's model produced the recorded verdict for.")
        print("A row an arm wrote is not evidence about that arm; a router built")
        print("from arms that wrote nothing is scored on the whole key.")

    # ok/miss/false still lets a bad supervisor look reasonable, because an arm
    # that confirms nearly everything scores every real defect correct. What a
    # supervisor is actually for is the CONFIRMED list a human then reads, so
    # the figures that matter are how much of that list is worth reading
    # (precision) and how much of the real defect set reached it (recall). An
    # arm with perfect recall and poor precision has not saved any money; it has
    # moved the cost to whoever reads its output.
    print("\n## The list a human would have to read\n")
    head = "%-10s %9s %8s %10s %9s %8s" % (
        "arm", "confirmed", "of which", "precision", "defects", "recall")
    print(head)
    print("-" * len(head))
    for arm in columns:
        # A row whose key accepts more than one verdict is one the record
        # declines to adjudicate, and it cannot be evidence for or against an
        # arm: confirming it is not a false positive, and not confirming it is
        # not a miss. It is therefore excluded from BOTH sides. The first
        # version of this counted such a row as real in the precision numerator
        # and not real in the recall denominator, which mixed two different
        # definitions in one line and made the arms not comparable to each
        # other. Excluding it is also the only resolution that does not let the
        # choice be made by which arm it happens to flatter -- scoring the row
        # as real weakens the arm that hedged it, scoring it as not real
        # weakens the arm that confirmed it, and neither is a reason.
        scored = [r for r in rows if r[arm] != "-" and len(r["accept"]) == 1]
        confirmed = [r for r in scored if r[arm] == "CONFIRMED"]
        good = [r for r in confirmed if "CONFIRMED" in r["accept"]]
        # Recall is over distinct DEFECTS, not findings. Two candidates can find
        # one bug and describe it differently -- P2 and L1 are the same defect --
        # and counting those as two lets an arm be scored as having found and
        # missed the same bug at once, which is exactly what happened to or-opus
        # at "2 of 3" before this. A defect counts as found if the arm confirmed
        # any finding describing it.
        reals = [r for r in scored if r["accept"] == ["CONFIRMED"]]
        defects = collections.defaultdict(list)
        for row in reals:
            defects[row.get("defect") or row["id"]].append(row)
        found = [d for d, group in defects.items()
                 if any(r[arm] == "CONFIRMED" for r in group)]
        print("%-10s %9d %8d %10s %9s %8s"
              % (arm, len(confirmed), len(good),
                 "%.0f%%" % (100.0 * len(good) / len(confirmed))
                 if confirmed else "n/a",
                 "%d of %d" % (len(found), len(defects)),
                 "%.0f%%" % (100.0 * len(found) / len(defects))
                 if defects else "n/a"))

    # The economics. A review costs the candidate's tokens plus the supervisor's,
    # and only the supervisor's scale with how much the candidate emitted -- so
    # an inventive candidate is expensive twice over, once in its own tokens and
    # again in everything spent refuting it. The figure that matters is not cost
    # per run but cost per finding that survived verification.
    # Distinct defects, not findings, for the same reason recall is: P2 and L1
    # are one bug and dividing by three would understate the cost of each.
    real = len({f.get("defect") or f["id"] for b in key["batches"]
                for f in b["findings"] if f["accept"] == ["CONFIRMED"]})
    emitted = sum(len(b["findings"]) for b in key["batches"])
    priced_arms = [a for a in arms if ARMS.get(a, {}).get("priced")]
    if priced_arms:
        print("\n## What the supervisor cost\n")
        head = ("%-12s %6s %10s %11s %9s %9s %9s"
                % ("arm", "runs", "prompt", "completion", "usd", "venue",
                   "usd/real"))
        print(head)
        print("-" * len(head))
        for arm in priced_arms:
            runs = prompt = completion = 0
            total = venue = 0.0
            for batch in key["batches"]:
                stem = os.path.join(args.work, "%s-%s" % (arm, slug(batch)))
                status = read_status(stem)
                # ox writes a status file on every exit, so one can exist with
                # null token counts -- a run still in flight, or one that failed
                # before the venue answered. Counting it as a run would divide a
                # real total by an inflated denominator and quietly understate
                # what a supervisor costs.
                if not status or status.get("prompt_tokens") is None:
                    continue
                runs += 1
                prompt += status.get("prompt_tokens") or 0
                completion += status.get("completion_tokens") or 0
                total += priced(ARMS[arm]["model"], status) or 0.0
                venue += venue_cost(status) or 0.0
            print("%-12s %6d %10s %11s %9s %9s %9s"
                  % (arm, runs, "{:,}".format(prompt), "{:,}".format(completion),
                     "$%.4f" % total, "$%.4f" % venue,
                     "$%.4f" % (total / real) if real else "n/a"))
        print("\n%d findings emitted by the five candidates, %d real by the key."
              % (emitted, real))
        print("usd is computed from the catalog and is the published figure;")
        print("venue is the venue's own usage.cost, recorded as its claim.")

        # Per batch, because this is where the answer lives: supervision is
        # charged per finding emitted, not per finding that turns out to be
        # real, so a candidate's invention rate is a multiplier on the
        # supervisor's bill and not only on the reader's patience.
        print("\n## Supervision charged per batch\n")
        head = "%-20s %8s %6s" % ("batch (candidate)", "emitted", "real")
        for arm in priced_arms:
            head += " %11s" % arm
        print(head)
        print("-" * len(head))
        for batch in key["batches"]:
            name = slug(batch)
            n = len(batch["findings"])
            nreal = sum(1 for f in batch["findings"] if f["accept"] == ["CONFIRMED"])
            line = "%-20s %8d %6d" % (name, n, nreal)
            for arm in priced_arms:
                status = read_status(os.path.join(args.work, "%s-%s" % (arm, name)))
                usd = priced(ARMS[arm]["model"], status) if status else None
                line += " %11s" % ("$%.4f" % usd if usd is not None else "-")
            print(line)
    if routers:
        print("\n## What the router escalated, and what it cost\n")
        head = ("%-18s %-28s %11s %10s %11s"
                % ("router", "cheap > escalate", "escalated", "of batches", "usd"))
        print(head)
        print("-" * len(head))
        nbatch = len(key["batches"])
        for spec in routers:
            usd = router_cost(args.work, key["batches"], spec["cheap"],
                              spec["escalate"], spec["escalated"])
            free_half = [a for a in spec["cheap"]
                         if not ARMS.get(a, {}).get("priced")]
            print("%-18s %-28s %11s %10s %11s"
                  % (spec["label"],
                     "%s > %s" % (",".join(spec["cheap"]), spec["escalate"]),
                     "%d batches" % len(spec["escalated"]),
                     "%d" % nbatch,
                     "$%.4f%s" % (usd, "*" if free_half else "")))
        print("\nescalated counts BATCHES, not findings: the evidence payload is")
        print("the five pinned files and it dominates the prompt, so a batch that")
        print("escalates one row re-sends all of it and is charged in full.")
        print("An escalation rate near 1 is a frontier pipeline wearing a cheap")
        print("arm's name, and its accuracy row above should be read that way.")
        if any(not ARMS.get(a, {}).get("priced")
               for spec in routers for a in spec["cheap"]):
            print("* the cheap half of this router billed nothing, so the figure is")
            print("  the escalation arm's bill alone; that arm's own cost is a")
            print("  latency and is not summed into a column of dollars.")

    if missing:
        print("\nNOT RUN: %s" % ", ".join(missing))
    if extra:
        print("\nINVENTED IDS: %s" % "; ".join(extra))
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    default_work = os.environ.get("VERIFIERCHECK_WORK", "verifier-runs")
    parser.add_argument("--work", default=default_work,
                        help="directory for batches and replies "
                             "(default: %(default)s)")
    parser.add_argument("--logs", default=os.path.join(HERE, "..", "oxbox", "logs"),
                        help="oxbox run logs (default: %(default)s)")
    subs = parser.add_subparsers(dest="command", required=True)

    build = subs.add_parser("build", help="write the blinded batches")
    build.add_argument("--pin", required=True,
                       help="history-free export of the pinned tree")
    build.set_defaults(func=cmd_build)

    run = subs.add_parser("run", help="put one or all batches to one arm")
    run.add_argument("--arm", required=True, choices=sorted(ARMS))
    run.add_argument("--pin", help="required for an ox arm, which attaches the "
                                   "pinned tree with --files")
    run.add_argument("--batch")
    run.add_argument("--all", action="store_true")
    run.add_argument("--timeout", type=int, default=900)
    run.set_defaults(func=cmd_run)

    score = subs.add_parser("score", help="disagreements first, then the key")
    score.add_argument("--arms", default="opus,gemini")
    score.add_argument("--router", action="append", metavar="SHAPE:CHEAP>ESCALATE",
                       help="score an ensemble as an arm; repeatable. "
                            "cascade:or-glm>or-opus is the survey's own "
                            "checking order (a cheap REFUTED stands, anything "
                            "else escalates); "
                            "disagree:or-glm,or-deepseek>or-opus is the "
                            "two-agent hand-off (agree and act, differ and "
                            "escalate). Every arm named must also be in --arms.")
    score.set_defaults(func=cmd_score)

    args = parser.parse_args()
    if args.command == "run" and not args.all and not args.batch:
        parser.error("run needs --batch <name> or --all")
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
