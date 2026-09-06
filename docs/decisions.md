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
a tree whose LICENSE grants everyone a copy. The split follows the license line
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
archived OpenRouter catalog and prints a `usd` column, labeled computed rather
than billed. A baseline's dollars beside a free model's verification tokens is
the comparison the 2026-08-30 cost rule was written for.

**What would change it.** A baseline that turns out to be *worse* than the free
tier on a fixture is not a reason to drop it -- that is a finding. A reason to
change the decision would be the fixtures becoming a benchmark with an answer key
derived from baseline output, at which point "the baseline is the ruler" has
quietly become "the baseline is the answer", and the corpus README's rule that
there is no expected-findings key needs to be re-decided rather than eroded.

## Comparing verifiers

**Decided** 2026-09-03, at the user's request: try a cheap model as the standing
supervisor and find out what it costs in accuracy. `costcheck.py` established
that verification is the expensive half of a run; the decision above named Opus 5
the supervisor "on price", which is an argument that has to be re-run whenever a
cheaper candidate appears. Gemini 3.8 Flash is one: $0.75/$3.75 per million
against Opus 5's $5/$25 on the OpenRouter list, 6.7x cheaper on both axes, and at
the margin free through the maintainer's agy subscription.

**Method.** `verifiercheck.py` replays findings the survey has already recorded
verdicts for, rather than verifying anything new. The first set is the fifteen
findings the five 2026-09-02 baselines emitted against `oxbox-clean-control`;
`corpora/answers/oxbox-clean-control-verdicts.json` is the key, transcribed from
those observations' own per-finding tables. Replay is what makes the experiment
cheap enough to repeat: no candidate model is called at all, and the ground truth
already exists.

**Both arms are toolless and get identical bytes.** The pinned source is inlined
into the prompt -- `jailtest.py`, the launcher, the sandbox profile, `guardtest.py`
and `.gitignore`, every file the recorded verdicts cite -- and both arms run in an
empty working directory. This is `corpus-manifest.json`'s byte-identical-payload
rule applied one layer up, and it is a compromise stated rather than hidden: a
verifier that roams picks its own evidence, and two verifiers that roam differently
produce a gap nobody can attribute to either one. The price is that the evidence
set is pre-decided, which is *not* how the standing supervisor works in production.
A result here bounds what a cheap verifier can do on a fixed record; it does not
show what it would do turned loose on a repository.

Three things forced that shape, and each is worth knowing on its own:

- **A `git worktree` leaks the answer key.** A worktree shares `.git` with its
  parent, and the commit immediately after this pin (`0090c35`) names both real
  defects in its subject line, so any verifier that ran `git log` would read the
  answers. The pin is built with `git archive <commit> | tar -x` instead, and
  `verifiercheck.py build` refuses a directory containing a `.git`.
- **The verifier's evidence is a superset of the candidate's.** The fixture is
  6 KB of `jailtest.py`, but the recorded verdicts turn on `oxbox`, `jail.sb` and
  `.gitignore`. Handing a verifier only the reviewed file would make several
  findings unsettleable, and a verifier that answers anyway is the failure this
  is trying to measure.
- **agy cannot read a file headlessly.** It reaches for a shell command rather
  than a native read tool, and headless mode auto-denies the `command`
  permission with no way to prompt. `--dangerously-skip-permissions` would have
  fixed it by giving one arm unrestricted tools while the other stayed
  allowlisted, which is the confound, not a workaround for it.

**The key is not independent of the Claude arm.** The recorded verdicts were
reached by `claude-fable-5-1` and `claude-opus-5`. Agreement with them is
therefore worth less on the Opus side than on the Gemini side, and a summary
statistic hides that. `verifiercheck.py score` prints the disagreement list
first and the aggregate second for that reason: the disagreements are the rows
that carry information, and they are few enough to be settled by hand.

**Results are not observations.** They go to `docs/verifier-comparison-<date>.md`,
one file per run, beside the generator reviews. `observations/` feeds part 2 of
each issue, which is about models the survey recommends or declines to; a verifier
comparison is about the machinery, and its `model:` and `role:` fields would have
to be filled in with something untrue. First run:
[verifier-comparison-2026-09-03.md](verifier-comparison-2026-09-03.md).

**What would change it.** A cheap arm that matches on this record still has to be
shown on a batch with no key before it can take the standing supervisor's job --
replay measures agreement with a past judgment, not the judgment itself. And if a
cheap verifier ever *were* adopted, the observations it produces should say which
arm verified them in the `agent:` field, exactly as the Fable-verified rows do
now; the field already carries that meaning and needs no new rule.

**Cost is measured through ox, not through a subscription.** A subscription CLI
is the cheapest way to run an arm and the worst way to measure one: agy publishes
no token accounting at all, so its half of a comparison cannot be reported under
the rule that a findings run reports both halves of its cost. Priced arms
therefore go through `ox` against OpenRouter, where the venue's usage returns in
`status.json` and `costcheck.py` prices it from the archived catalog, and each
model runs at its own `default_effort` rather than a matched rung -- the question
is what a supervisor costs to run, and a matched rung prices a setting nobody
would choose. If Google ever adds usage reporting to agy, a subscription arm
becomes measurable and this narrows to a preference rather than a requirement.

**A supervisor is scored on the list it hands back, not on its accuracy.** An arm
that confirms nearly everything scores every real defect correct and is useless,
because the job is filtering inventions out. `score` therefore reports precision
and recall over the CONFIRMED list beside ok/miss/false. The first run showed why:
the cheap arm reached 100% recall at 44% precision, catching a defect every other
arm missed while confirming six of eight findings in that batch, and cost $0.90
less while handing a human six more findings to read. A saving denominated in
tokens against a cost denominated in human attention is not a saving.

**A finding is scored as written, not as generously as it could be read.** This
rule was forced by the third run and did not exist before it. The same model
(Fable 5.1) recorded a finding as real on 2026-09-02 with tools and the whole
repository, and refuted it on 2026-09-03 under this contract -- because the
finding's stated failure scenario needs a sandbox that permits networking, and
no such sandbox exists at the pin. Crediting an accurate mechanism whose stated
consequence is unreachable is the generous reading, and it makes "invention"
unscoreable across the whole corpus, because almost every invention contains an
accurate observation somewhere. The strict reading is now the contract's, and
`corpora/prompts/verify-findings.txt` says so in as many words.

An earlier version of this section proposed measuring "wording sensitivity",
after the Opus arm refuted a defect in one batch and confirmed what looked like
the same defect in another. **That was an over-read and the proposal is
withdrawn.** Reading the two findings verbatim shows they are not the same claim:
one asserts only a leak on an impossible premise, the other asserts the leak and
adds the argument that survives it, which is also the argument the upstream fix
implements. Every arm treating them differently was precision. The lesson kept is
narrower and about method: two findings that a summary calls "the same defect"
may not be, and the way to find out is to read what each one actually said.

## The Editor's Rating replaces the status markers

**Decided** 2026-09-06, in a design discussion with the user. The four status
markers `USE` / `TRY` / `HOLD` / `AVOID` are retired. In their place, every
model the survey tried gets a row in the catalog table with three measured
digits, a disqualifier column, and an **Editor's Rating** of Good, Acceptable,
Marginal, or Poor that the user writes and the generator never does. The
manifest is derived from that row: a model is in it exactly when it is rated
Good or Acceptable and has no disqualifier standing. This entry records the
decision; the generator skill, `surveytest.py`, the observation frontmatter and
the catalog table still carry the old markers until the follow-up lands.

**Why the markers went.** They encoded two axes in four words: direction (go,
wait, stop) and evidence (run-backed or card-backed), split asymmetrically so
that only a run could earn `USE` while a card fact could earn `AVOID`. That
asymmetry was the "a recommendation requires a run" rule made lexical, and it
was sound. What failed was `HOLD`, which the 2026-08-24 edition used both for
"the endpoint is 503ing, wait" and for "six findings, zero real, but n=1", and
had to gloss each time. The bolted-on qualifiers `USE (expiring)` and
`AVOID for review` were the other tell: time and scope are axes the words did
not carry. The markers also predate the fixtures and the scorer; since
2026-09-02 quality, cost and speed are measured, and a verdict word that hides
the measurement is worse than the measurement.

**What the user decided, in order.** The recommendation is the manifest: a
model either gets in or it does not. The dimensions that decide it are how well
it did the task, what it cost to extract that (a free model that burns
supervisor tokens is not cheap), and speed, with disqualifiers held outside the
ratings as a plain in-or-out gate. Each dimension gets a 0-5 digit so the row
reads at a glance. If we tried to run it, it is in the table, failures
included. The user is the editor and writes one rating per model as an
editorial verdict, on the IIHS crash-test scale, under the name Editor's Rating.

**The digits are buckets of a measurement, never typed.** Each level is a
threshold on a value the run already records; a script buckets it and the
threshold table is printed in every issue. 0 means measured and worst. An
unrun dimension is a dash, per the "no data is the preferred answer" rule, so 0
can never do `HOLD`'s old double duty. Every digit carries its fixture id and n,
because the fixtures discriminate unequally: all five baselines scored 10 of 10
on `oxbox-ask-grounding`, while the review batches spread from 13 of 15 to 0 of
6. A bare digit would let a saturated fixture launder a weak model.

| Dimension | Measured | 5 | 4 | 3 | 2 | 1 | 0 |
|---|---|---|---|---|---|---|---|
| Quality | seeded defects found, of those present | all | most, missed a minor one | about half | one or two | one, and minor | none, or no output |
| Cost | USD per real defect, both halves, log scale against the Fable 5.1 ceiling | under 1/100 | under 1/10 | under 1x | up to 3x | up to 10x | over 10x, or no real defect to divide by |
| Speed | wall clock per run | under 30 s | under 2 min | under 5 min | under 10 min | under 20 min | 20 min or more, or timed out |

The speed row was checked against the recorded runs before it was adopted:
gpt-5.6-sol at 12 s lands at 5, the MiniMax and Nemotron runs near two to three
minutes at 3, glm-5.3-flash at nine minutes at 2, DeepSeek's 21-minute run at 0.
A rubric that puts the real data in one bucket is not a rubric. The cost row is
logarithmic for the same reason: costs here span a thousandth of a cent to
dollars. The cost thresholds are provisional until one issue of both-halves
figures exists to check them against, the way the speed row was checked.

**Noise is charged once, on the cost row.** Quality is recall against the
fixture's seeded set: did it find the bugs. A false finding costs supervisor
tokens to refute, and cost per real defect already counts both halves, so
folding precision into quality as well would charge the same fault twice and
muddy quality's one question. Nemotron's 2 of 10 reads as a low quality digit
from the misses and a poor cost digit from the eight refutations, which are the
two separate facts a reader needs.

**Gate-style fixtures own their mapping.** `oxbox-secret-scanner-fix` has three
gates and eight verdicts, not a fraction; its quality rubric ("all gates and 8
of 8" for a 5, "does not apply" for a 0) lives beside the task in
`corpora/corpus-manifest.json`, so a frozen fixture's scoring freezes with it.

**Quality digits come from fixtures only; real-work batches keep a raw column.**
MiniMax's 13 of 15 is the strongest evidence in the repo and it came from real
review batches on oxbox's own code, with no seeded set and no recall. Rather
than rate real-work precision as quality with a flag, which is more generous
and less comparable, the table gives real-work batches a raw "real / confirmed"
column that feeds the cost digit and sits in plain view for the editor. The
digit stays frozen-fixture comparable; the evidence stays visible.

**Tried means in the table, and failures distinguish two ways.** A run the
venue refused (404, 503, unauthorized) is a row with the disqualifier column
filled and every digit dashed. A run the model answered with nothing, like
glm-5.3-free's empty content with `finish_reason` set, is a row with quality 0.
That one distinction is what `HOLD` versus `AVOID` never managed. Probes are not
runs, per `observations/README.md`, so probe-only models have no row; their
disqualifiers annotate the catalog listing instead. Baselines were tried, so
they are rows too, with digits, marked baseline, ineligible for the manifest
and carrying no Editor's Rating; a table where gpt-5.6-sol's speed 5 sits beside
a 0 shows the reader what the scale means. This does not conflict with the rule
that a baseline never carries a recommendation: digits are measurements.

**The Editor's Rating is the manifest decision, on the IIHS scale.** Good,
Acceptable, Marginal, Poor: four levels, no neutral middle, so the editor has
to lean, and words whose public meaning a reader already knows. The manifest
line falls where the IIHS's own top award puts it: Good and Acceptable are in,
Goods ranked above Acceptables and the editor's order within each tier;
Marginal and Poor are out. Marginal is a verdict on thin or mixed evidence (2 of
10 with the one that mattered), not a deferral. Poor is an answer that was
worthless (6 findings, 0 real). The one-line reason beside the rating is the
manifest's existing `why` field, written once. The rating is per model, never
per fixture, because the manifest cannot hedge, and that is also why there is
no rollup rule for the digits: the rating is the rollup.

The borrowed names carry a caution. IIHS ratings come off a fixed protocol, so
the words imply a procedure produced them. Here the word is the editor's and
the digits are the procedure. That holds only while the two sit in the same row
and the issue says once, up top, that the rating is the editor's call and the
digits are measured. Shown as words, never as the IIHS's green-through-red; the
no-color-only rule stands.

**Disqualifiers and ratings are orthogonal.** The disqualifier column records
access and venue facts, dated so next week's run rechecks them: unreachable, no
structured output, completion cap under the fixture's need, delisted, rate
limit under the usable floor. The rating records the model's work. A row with a
disqualifier standing keeps its last rating with its date and has no manifest
entry; when the disqualifier clears it returns at that rating without a
re-decision. A reliability dimension (429 rate is measurable) was considered
and left out: a rated 2 inside the manifest still fails the reader's run, and
three dimensions is the smallest set that orders the manifest.

**The generator never writes the rating.** Same principle as the
never-unattended rule for skill revisions, same failure mode: an agent writing
the editor's opinion for them. Unattended runs carry last week's rating forward
with its date visible, so a Good from three weeks ago on a model not run since
is legible as stale rather than silently current. The rating lives in a single
hand-edited file the generator reads; its path is an implementation detail,
its writer is not.

**What the follow-up must enforce**, in `surveytest.py`:

- every manifest entry is rated Good or Acceptable;
- every model rated Good or Acceptable with no open disqualifier is in the
  manifest, and Goods precede Acceptables;
- no digit appears in an issue that the bucketing script did not compute from
  a recorded value, which in practice means observation frontmatter gains
  the measured fields (defects found and present, or gates passed; real and
  confirmed for real-work batches; wall seconds; both-halves USD) and the
  digits are derived from them, never typed.

**What would reverse it.** A model with enough batches on enough fixtures that
a mechanical ordering (pass the disqualifiers, sort by cost per real defect,
speed as tiebreaker) stops being noise; at that point the editor's ordering
within a tier could yield to the formula, though the rating itself stays a
human call. Or the cost thresholds failing their check against a real issue's
figures, which revises the row, not the design.
