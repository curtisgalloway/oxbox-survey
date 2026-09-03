<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

# Decisions

Choices whose reasoning is not recoverable from the code, with the measurement
that settled each one and what would reverse it. Written because this repo was
rebuilt from a clean history and the arguments would otherwise have survived
only in commit messages that no longer exist.

Decisions already documented where they apply are not repeated here: the
watermark format is in [log-contract.md](log-contract.md), the corpus rules in
[../corpora/README.md](../corpora/README.md), the evidence tiers in
[../README.md](../README.md).

## Vendor prose is stripped from archived catalogs; other vendor fields are not

**Decided** 2026-08-30. `catalogs/` blanks each model's `description` at capture
and declares it in `redacted_fields`. `links.details` and `privacy_comments` are
kept.

**Why.** Everything in this repo is Apache-2.0, and `description` is not ours to
relicense — it is vendor-authored marketing copy, and it was bulky: 87,715 and
82,967 characters from OpenRouter, 224,324 and 225,030 from Requesty, ~620 KB
across four archives. It also made redistribution depend on four terms-of-service
documents nobody had read.

The two fields that look similar and were kept were measured rather than assumed,
because the first instinct to strip them was wrong. `links.details` is a URL path
(`/api/v1/models/<id>/endpoints`), not prose. `privacy_comments` is ten distinct
values across Requesty's entire roster, longest 73 characters, mostly a URL or
`N/A` — factual, far below any threshold of originality, and load-bearing for the
survey's data-terms axis.

**What would change it.** A venue whose terms explicitly permit redistribution,
or a `description` that stops being marketing copy. Neither is likely; check the
measurement before assuming a new field is prose.

## The tripwire disqualifies but cannot rank

**Decided** 2026-08-30, after running it. `oxsurvey --probe --tripwire` asks every
model one question with a planted defect and a plausible non-defect, scored
mechanically.

**Why it cannot rank.** It does not discriminate. Fired at the whole field — 38
models across three venues — **18 answered and 17 scored `correct`**. The one
exception was a content-safety classifier returning `malformed`. Zero
`overcalled`: the trap line fooled nobody. A screen where everyone scores full
marks orders nothing, and the fixture is a ten-line off-by-one that any current
model finds.

**Why it is still worth running.** It is an excellent reachability screen. Twenty
of those 38 catalogued free models could not be called at all — 10 `not_found`, 4
rate-limited, 3 errors, 2 unauthorized, 1 upstream error — which halves the field
before any expensive work. It also caught a card contradiction:
`nvidia/nemotron-3-super-120b-a12b` and `-ultra-550b-a55b` 404 on OpenRouter and
answer fine on Requesty. The catalog lists models the endpoint does not serve.

**What would change it.** A harder fixture — a defect needing reasoning across
the whole function, or one where the obvious answer is the trap. Until then the
shortlist is still picked by hand, and a tripwire result may never justify a
`USE`: `source: probe` has never carried a recommendation and this does not
change that.

## Third-party packages are allowed here, and not in oxbox

**Decided** 2026-08-30. The stdlib-only rule was retired for this repo. Nothing
here needs a dependency yet, so the code is unchanged; what changed is that
stdlib-only is a description rather than a rule.

**Why.** It was inherited from oxbox without its reason. oxbox's whole product is
a containment claim, so a dependency there is code on the trusted side of the
boundary, in the process holding the API key — a compromised package would not
bypass the jail, it would make the jail irrelevant. This repo builds manifests and
reports against a public catalog. It guarantees nothing, and a rule it cannot
justify on its own terms is cargo-culted.

**What follows.** Add the first dependency with `uv`, never `pip install` — the
system `python3` on macOS is PEP 668-managed and refuses pip. Adding one also
means re-deciding the Python floor: 3.9 exists because that is the stock macOS
interpreter, which is why CI has no install step. The first dependency brings a
uv-managed interpreter with it, and 3.11 would let `costcheck.py` drop its
hand-rolled `parse_stamp` for `datetime.fromisoformat`.

## The report is not in this repository

**Decided** 2026-08-30. Editions live in the `oxbox.ai` repo; this one holds
machinery and evidence.

**Why.** The prose is the publication and is all rights reserved; it cannot sit in
a tree whose LICENSE grants everyone a copy. The split follows the licence line
exactly, and it cost nothing in enforcement: `surveytest.py` validates
`snapshots/`, `catalogs/`, `observations/`, `providers/` and `corpora/`, and never
validated the editions. Moving `observations/` instead would have cost six checks
including the load-bearing one — that a `source: probe` observation can never
claim a `USE` — so observations stay, as the Observed *tier*, which is evidence
rather than publication.

## Editions before the first publication are numbered 0.x

**Decided** 2026-08-30. The three pre-launch editions are 0.1–0.3. The first
published one is issue 1.

**Why.** None of them was ever published. Numbering them 1–3 would make the first
edition anyone actually reads issue 4.

**The rule it clarifies.** "Never edit a published observation" assumes
publication happened. Before issue 1, nothing had readers, so redacting,
renumbering and path-fixing pre-launch material is finishing a draft rather than
rewriting history. **The rule binds from issue 1 onward.**

## latest.json is a symlink, not a copy

**Decided** 2026-08-30. `manifests/latest.json` points at the newest dated
manifest so a consumer can use `--manifest` without knowing the date.

**Why a symlink.** A copy drifts, and the drift is silent: a stale pointer serves
last week's ranking forever without erroring. A test asserts it resolves to the
newest dated manifest.

**The cost.** Anything globbing `manifests/*.json` sees the newest manifest twice.
That broke the site generator before it shipped; `oxsite` now skips symlinks. Any
future consumer needs the same guard.

## A dry run is not a run

**Decided** 2026-08-30, from the data. `usagereport.py` counts only
`status.dry_run == false`, and `costcheck.py` reports a dry run as a dry run
rather than as a failed call.

**Why.** In the first window measured, **21 of 27 log directories were dry runs**.
Counting them would have inflated usage 4.5× and, worse, reported models as
reachable on requests that never left the machine. Reporting them as failures
would have put phantom outages in the availability record.

## The generator review is not published

**Decided** 2026-09-01, at the user's direction while reviewing issue 1: "The
generator review is really only for you and me to iterate on debugging how the
generator works, it should not be part of the survey that's published."

**Where it goes instead.** `docs/generator-reviews/<date>.md`, one file per
edition, Apache-2.0 like the rest of this repo. It still has to be written every
run; the skill's own rule that part 2 is never skipped stands. What changed is
the audience.

**What would change it.** Nothing foreseeable. The three pre-launch editions
carry their reviews inline and are left as they are.

## Paid frontier models run as baselines, never as candidates

**Decided** 2026-09-02, when the first baseline runs were made. A survey of free
and stealth models reports "13 of 15 findings real" and has no way to say whether
that is good. The only thing that can say so is the same fixture, same bytes, put
to a model whose quality is not in question -- so a small fixed set is run through
`ox` on the corpus, from the OpenRouter venue that already exists, and recorded as
observations with `role: baseline`. The set, approved by the user the same day:

| Role | Model | Why this one |
|---|---|---|
| frontier ruler | `anthropic/claude-sonnet-5` | the paid model a reader would otherwise reach for |
| frontier ruler | `openai/gpt-5.6-sol` | the other one; same list price, and a survey that omits the largest vendor reads as if it were avoiding it |
| cheap frontier | `google/gemini-3.7-flash` | the price tier readers actually compare free models against |
| pay-a-little open weights | `deepseek/deepseek-v4-flash` | seven cents per million in: the real competitor to free |
| pay-a-little open weights | `z-ai/glm-5.3-flash` | already rank 2 of the manifest as a paid entry, and never run |

Left out on purpose: Opus and the GPT Pro tiers (nobody weighs a free model
against $25--$180 per million output, and Opus is the verifier's own family),
Codex variants (a different product shape), and the rest of the frontier (Grok,
Kimi, Qwen Max, Mistral Medium) until a reader asks the question one of them
answers. Five is the ceiling without a reason, because each addition is five runs
of which two are human-verified.

**What a baseline is not.** It is not a recommendation and cannot become one: no
status marker, never ranked, and never a free model -- the free tier is the
subject, not the ruler. A paid model can be both a manifest entry and a baseline
(`z-ai/glm-5.3-flash` is rank 2 and a baseline), and when it is, its baseline
observations do not move its entry; only a candidate run does. The survey's scope
is what a free model can do, and the baseline is the ruler, not a contestant. The
generator's rule that there is no league table stands; a reference figure beside
a count is a comparison of two numbers on one fixture, not a ranking of the field.

**Why through ox and OpenRouter, not a vendor SDK or a subscription CLI.** The
comparison is only worth anything if the payload is byte-identical and the audit
trail is the same shape. `ox` already records `context_bytes`, the request and
the response for every run, and the corpus checks `context_bytes` against the
fixture. A vendor SDK would need a second code path whose request shape differs
in ways nobody has measured; an agentic CLI on a subscription gives the model
tools, a workspace and a system prompt of its own, which is a different
experiment entirely (the `inkling-free` observation of 2026-09-01 is about that
gap). Pricing is the one thing OpenRouter costs extra, and it is small: the
three mechanical fixtures against both baselines came to well under a dollar.

**Who verifies.** A Claude agent, against the pin, the same way for baselines
and candidates. The user's first call was Fable; revised the same evening to
**Claude Opus 5 as the standing supervisor**, on price -- verification is the
expensive half of every run and Opus is the practical choice for it. The
observations dated 2026-09-02 for Sonnet 5, Gemini 3.7 Flash and GPT-5.6 sol were
verified by Fable and say so in their `agent:` field; everything after is Opus
unless the field says otherwise. The self-preference objection -- Claude judging
Claude -- is real and is handled by protocol rather than by choosing a
different judge: findings are verified against the source, counts are recorded
per finding with the file and line, and for the human-scored review fixtures the
model's identity is stripped from the batch before verification. Mechanical
fixtures do not have the problem at all, which is why they ran first.

**Real defects get fixed, not just recorded.** The user's standing instruction
(2026-09-02): any verified finding a run produces in one of the user's repos is
fixed the same session, and the observation cites the fixing commit. The first
two were the clean-control fixture's own: the metadata oracle stat()ing
`/etc/shadow` (Gemini) and the network probes passing vacuously on an offline
host (GPT), both fixed in oxbox `0090c35`.

**Cost is now in dollars.** `costcheck.py` prices a run's tokens from the
archived OpenRouter catalog and prints a `usd` column, labelled computed rather
than billed. A baseline's dollars beside a free model's verification tokens is
the comparison the 2026-08-30 cost rule was written for.

**What would change it.** A baseline that turns out to be *worse* than the free
tier on a fixture is not a reason to drop it -- that is a finding. A reason to
change the decision would be the fixtures becoming a benchmark with an answer key
derived from baseline output, at which point "the baseline is the ruler" has
quietly become "the baseline is the answer", and the corpus README's rule that
there is no expected-findings key needs to be re-decided rather than eroded.
