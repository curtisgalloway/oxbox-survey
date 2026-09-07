#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Curtis Galloway
# SPDX-License-Identifier: Apache-2.0
"""The catalog table: measured digits per tried model, and the Editor's Rating.

Every model the survey has put through ox gets a row, failures included. Three
0-5 digits are bucketed from values the observation frontmatter records --
quality (recall against the fixture's seeded set), cost (USD per real defect,
both halves, against the fixture's ceiling) and speed (wall clock) -- and the
thresholds are the table printed by `--rubric`. Nobody types a digit. Zero is
measured and worst; a dash is unmeasured.

The Editor's Rating (Good / Acceptable / Marginal / Poor) is the one column a
human writes, in editor-ratings.json, and this script only reads it. The
manifest is derived from that column: Good and Acceptable are in, Goods above
Acceptables, Marginal and Poor out, and a standing disqualifier holds a model
out whatever its rating. See docs/decisions.md, "The Editor's Rating replaces
the status markers".

    python3 ratings.py              # the two tables, markdown
    python3 ratings.py --rubric     # the threshold table an issue must print
    python3 ratings.py --json       # rows as JSON, for the generator
"""

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OBSERVATIONS = HERE / "observations"
CORPUS = HERE / "corpora" / "corpus-manifest.json"
EDITOR_RATINGS = HERE / "editor-ratings.json"

SCALE = ("Good", "Acceptable", "Marginal", "Poor")
IN_MANIFEST = ("Good", "Acceptable")
RULE_FROM = "2026-09-06"  # manifests dated here or later are derived from ratings

# Observation kinds that describe a run's output. Access and availability
# observations contribute disqualifiers, never rows.
ROW_KINDS = ("findings", "hygiene")
MEASURED_FIELDS = ("run", "wall_s", "findings", "real", "hits", "hits_of",
                   "applies", "self_hits", "usd_model", "usd_total",
                   "timed_out", "disqualifier", "harness_model", "harness_window",
                   "harness_in", "harness_out", "harness_cache_read",
                   "harness_cache_write", "harness_unpriced", "harness_note",
                   "harness_seconds", "harness_usd", "harness_venue")

# The checking half is priced at the supervisor's own list price from the
# archived OpenRouter catalog, cache reads and writes included; the harness
# names its model the way the transcript does, the catalog the way OpenRouter
# does. Measured, not a multiplier: Fable's cache read is $0.25 per million
# on the 2026-09-01 catalog, a quarter of the usual 10%-of-input guess.
HARNESS_MODEL_IDS = {
    "claude-fable-5-1": "anthropic/claude-fable-5.1",
    "claude-opus-5": "anthropic/claude-opus-5",
    "claude-sonnet-5": "anthropic/claude-sonnet-5",
}
CATALOGS = HERE / "catalogs" / "openrouter"

# "Cheap paid" for the cost comparison: a list completion price at or under
# this, per million tokens. Provisional; the editor's rule is "cheap enough
# is a candidate" and this is the first number put to it.
CHEAP_COMPLETION_USD_PER_MTOK = 1.0
DERIVED_KEYS = ("quality", "cost", "speed")  # never typed into frontmatter


# --- the buckets -----------------------------------------------------------
#
# The wording in docs/decisions.md ("most, missed a minor one", "about half")
# is what a reader sees; these fractions are how a script decides it. "Minor"
# is not machine-decidable, so the cut is on the fraction alone.

def quality_digit(hits, of, required_ok=True):
    """0-5 from hits over the fixture's total. A failed required gate is 0."""
    if hits is None or not of:
        return None
    if not required_ok or hits <= 0:
        return 0
    if hits >= of:
        return 5
    frac = hits / float(of)
    if frac >= 0.75:
        return 4
    if frac >= 0.5:
        return 3
    if frac >= 0.25:
        return 2
    return 1


def cost_digit(usd_total, real, ceiling):
    """0-5 from USD per real result, both halves, on a log scale to the ceiling.

    "Real" is a verified-real finding on a review run, or a hit on a fixture
    with a seeded set. The ceiling is Fable 5.1's USD per real result on the
    same fixture and lives in the corpus manifest; while it is null the digit
    is unmeasured. A run with nothing real has nothing to divide by and is a
    0 -- it spent money and returned nothing usable.
    """
    if usd_total is None or ceiling is None or real is None:
        return None
    if real <= 0:
        return 0
    ratio = (usd_total / float(real)) / float(ceiling)
    if ratio < 0.01:
        return 5
    if ratio < 0.1:
        return 4
    if ratio < 1:
        return 3
    if ratio <= 3:
        return 2
    if ratio <= 10:
        return 1
    return 0


def speed_digit(wall_s, timed_out=False):
    """0-5 from wall clock. Checked against the recorded runs before adoption."""
    if timed_out:
        return 0
    if wall_s is None:
        return None
    if wall_s < 30:
        return 5
    if wall_s < 120:
        return 4
    if wall_s < 300:
        return 3
    if wall_s < 600:
        return 2
    if wall_s < 1200:
        return 1
    return 0


RUBRIC = [
    ("Quality", "seeded defects found, of those present",
     ["all", "3/4 or more", "half or more", "a quarter or more", "any", "none, or no output"]),
    ("Cost", "USD per real finding or hit, both halves, against the fixture's Fable 5.1 ceiling",
     ["under 1/100", "under 1/10", "under 1x", "up to 3x", "up to 10x",
      "over 10x, or nothing real"]),
    ("Speed", "wall clock per run",
     ["under 30 s", "under 2 min", "under 5 min", "under 10 min", "under 20 min",
      "20 min or more, or timed out"]),
]


def rubric_markdown():
    lines = ["| Dimension | Measured | 5 | 4 | 3 | 2 | 1 | 0 |",
             "|---|---|---|---|---|---|---|---|"]
    for name, measured, levels in RUBRIC:
        lines.append("| %s | %s | %s |" % (name, measured, " | ".join(levels)))
    return "\n".join(lines)


# --- reading the record ----------------------------------------------------

def frontmatter(text):
    head = re.search(r"^---\n(.*?)\n---\n", text, re.DOTALL | re.MULTILINE)
    if not head:
        return None
    return dict(re.findall(r"^(\w+):\s*(.+)$", head.group(1), re.MULTILINE))


def _num(value):
    if value is None:
        return None
    value = value.strip().strip('"')
    try:
        return int(value)
    except ValueError:
        return float(value)


def _bool(value):
    if value is None:
        return None
    return value.strip().lower() in ("true", "yes")


CORRECTABLE = ("findings", "real", "hits", "hits_of", "applies", "self_hits",
               "wall_s", "usd_model", "usd_total", "timed_out", "disqualifier")


def load_observations(root=OBSERVATIONS):
    """Every observation's frontmatter, plus the file it came from.

    A published observation is never edited. A later observation that names
    it in `corrects:` and carries measured fields overlays those fields here,
    so the digits follow the corrected record while the original stays as
    written; the overlay is recorded on the target as `_corrected_by`.
    """
    out = []
    for path in sorted(root.glob("*.md")):
        if path.name == "README.md":
            continue
        fields = frontmatter(path.read_text(encoding="utf-8"))
        if fields is None:
            continue
        fields = dict(fields)
        fields["_file"] = path.name
        fields["model"] = fields.get("model", "").strip('"')
        fields.setdefault("role", "candidate")
        out.append(fields)
    by_file = {f["_file"]: f for f in out}
    for f in out:
        target = by_file.get((f.get("corrects") or "").strip().split("/")[-1])
        if not target:
            continue
        for key in CORRECTABLE:
            if key in f:
                target[key] = f[key]
        target.setdefault("_corrected_by", []).append(f["_file"])
    return out


def load_corpus(path=CORPUS):
    data = json.loads(path.read_text(encoding="utf-8"))
    tasks = {}
    for project in data.get("projects", []):
        for task in project.get("tasks", []):
            tasks[task["id"]] = task
    return tasks


def load_editor_ratings(path=EDITOR_RATINGS):
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("ratings", {})


def load_prices(catalog_dir=CATALOGS):
    """model id -> pricing dict (USD per token, strings) from the newest catalog."""
    paths = sorted(catalog_dir.glob("*.json"))
    if not paths:
        return {}, None
    data = json.loads(paths[-1].read_text(encoding="utf-8"))
    rows = (data.get("payload") or {}).get("data") or []
    return {r.get("id"): (r.get("pricing") or {}) for r in rows if isinstance(r, dict)}, paths[-1].name


def supervisor_price_line(model_id, prices):
    """'$10/$50, cache $0.25/$12.50 per M' for a supervisor's catalog row."""
    pricing = prices.get(model_id) or {}
    if not pricing:
        return "unpriced"
    per_m = lambda key: float(pricing.get(key) or 0) * 1_000_000  # noqa: E731
    return "$%g/$%g, cache read $%g, write $%g per M" % (
        per_m("prompt"), per_m("completion"), per_m("input_cache_read"),
        per_m("input_cache_write"))


def window_seconds(window):
    """Seconds spanned by a harness_window like 2026-09-06T21:22Z..2026-09-06T21:27Z."""
    if not window or ".." not in window:
        return None
    from datetime import datetime
    try:
        start, end = (datetime.strptime(part.strip(), "%Y-%m-%dT%H:%MZ")
                      for part in window.split("..", 1))
    except ValueError:
        return None
    return (end - start).total_seconds()


def billed(fields):
    """A check record's billed USD (harness_usd), or None when it was token-priced.

    A metered check sends the same verification task through a venue as one
    request and records what the venue billed (ox's venue_cost). That figure
    is the checking half itself, not an estimate of it, so it outranks a
    window priced from token counts. Decided 2026-09-06, round 4 question 3.
    """
    value = fields.get("harness_usd") if fields else None
    if value in (None, ""):
        return None
    return _num(value)


def price_window(fields, prices, as_model=None):
    """USD for one harness window from its token counts, or None if unpriced.

    A billed record returns its bill (see billed()); as_model does not apply
    to it, because a bill is not a token count. Otherwise as_model reprices
    the same tokens at another supervisor's row, so the table can show what
    the window would have cost under the standing supervisor rather than the
    one that happened to do the checking.
    """
    usd_billed = billed(fields)
    if usd_billed is not None:
        return usd_billed
    model = as_model or HARNESS_MODEL_IDS.get(fields.get("harness_model", ""))
    pricing = prices.get(model)
    if not pricing or "harness_window" not in fields:
        return None
    usd = 0.0
    for key, price_key in (("harness_in", "prompt"), ("harness_out", "completion"),
                           ("harness_cache_read", "input_cache_read"),
                           ("harness_cache_write", "input_cache_write")):
        count = _num(fields.get(key)) or 0
        usd += count * float(pricing.get(price_key) or 0)
    return usd


def tier_of(model, prices, usd_model):
    """free / cheap paid / frontier / paid (price unknown), from the list price.

    Free is a zero bill or a free-tier id (":free" on OpenRouter, "-free" on
    the class B venues, which publish no price at all). Paid tiers split on
    the catalog's completion price; a paid model the catalog does not price
    is named as such rather than guessed.
    """
    if usd_model == 0 or model.endswith(":free") or model.endswith("-free"):
        return "free"
    pricing = prices.get(model) or {}
    completion = float(pricing.get("completion") or 0) * 1_000_000
    if not completion:
        return "paid, price unknown"
    if completion <= CHEAP_COMPLETION_USD_PER_MTOK:
        return "cheap paid"
    return "frontier"


# --- rows ------------------------------------------------------------------

def measure(fields, tasks):
    """One run-backed observation to its digits and raw figures."""
    task = tasks.get(fields.get("corpus", ""), {})
    rubric = task.get("quality") or {}
    hits = _num(fields.get("hits"))
    hits_of = _num(fields.get("hits_of")) or rubric.get("of")
    required_ok = True
    for name in rubric.get("requires", []):
        if _bool(fields.get(name)) is False:
            required_ok = False
    real = _num(fields.get("real"))
    # The cost divisor: verified-real findings on a review run, hits on a
    # fixture with a seeded set.
    divisor = real if real is not None else hits
    if not required_ok and divisor is not None:
        divisor = 0  # a patch that does not apply bought nothing, whatever it hit
    row = {
        "divisor": divisor,
        "harness_window": fields.get("harness_window"),
        "harness_model": fields.get("harness_model"),
        "harness_usd": None,  # filled by cost_rows, which knows the prices
        "harness_unpriced": fields.get("harness_unpriced"),
        "_fields": fields,
        "file": fields["_file"],
        "date": fields.get("date"),
        "venue": fields.get("venue"),
        "model": fields["model"],
        "role": fields.get("role", "candidate"),
        "fixture": fields.get("corpus") or None,
        "run": fields.get("run"),
        "quality": quality_digit(hits, hits_of, required_ok) if rubric else None,
        "cost": cost_digit(_num(fields.get("usd_total")), divisor,
                           task.get("cost_ceiling_usd_per_real")),
        "speed": speed_digit(_num(fields.get("wall_s")), _bool(fields.get("timed_out"))),
        "hits": hits, "hits_of": hits_of,
        "findings": _num(fields.get("findings")), "real": real,
        "usd_model": _num(fields.get("usd_model")),
        "usd_total": _num(fields.get("usd_total")),
        "wall_s": _num(fields.get("wall_s")),
    }
    return row


CEILING_CHECKER = "claude-fable-5-1"  # the ruler's own checking, for both-halves totals


def attach_checks(rows, observations):
    """Give each row its check records, keyed by checker.

    A check record is any observation that names a run and carries harness
    fields: a deliberate measurement of checking that run, by the checker it
    names. It replaces the row's own window for the same checker, and adds a
    window for a different one, so a run checked twice has two entries.
    """
    checks = {}
    for f in observations:
        if f.get("run") and f.get("harness_window") and f.get("kind") not in ROW_KINDS:
            for run_id in [x.strip() for x in f["run"].split(",")]:
                per = checks.setdefault(run_id, {})
                prior = per.get(f.get("harness_model"))
                # Two records by the same checker for one run: the billed one
                # wins over the token-priced one; otherwise the later file.
                if prior is not None and billed(prior) is not None and billed(f) is None:
                    continue
                per[f.get("harness_model")] = f
    for r in rows:
        r["checks"] = {}
        if r["harness_window"]:
            r["checks"][r["harness_model"]] = r["_fields"]
        for run_id in [x.strip() for x in (r["run"] or "").split(",") if x.strip()]:
            r["checks"].update(checks.get(run_id, {}))


def run_rows(observations, tasks, prices=None):
    """One row per run-backed findings or hygiene observation.

    A row's both-halves total is its own usd_total field when the observation
    recorded one (a mechanically scored fixture, where the checker is the
    scorer). Otherwise, when the ceiling checker has a check record for the
    run, the total is the model half plus that check's priced window, and the
    cost digit follows from it. A row with neither has no cost digit.
    """
    if prices is None:
        prices, _ = load_prices()
    rows = []
    for fields in observations:
        if fields.get("source") != "oxbox-run" or fields.get("kind") not in ROW_KINDS:
            continue
        if fields["model"] in ("", "-"):
            continue
        rows.append(measure(fields, tasks))
    attach_checks(rows, observations)
    for r in rows:
        if r["usd_total"] is None and r["usd_model"] is not None:
            check = r["checks"].get(CEILING_CHECKER)
            check_usd = price_window(check, prices) if check and check is not r["_fields"] else None
            if check_usd is not None:
                r["usd_total"] = r["usd_model"] + check_usd
                r["usd_total_from"] = "check record"
                task = tasks.get(r["fixture"] or "", {})
                r["cost"] = cost_digit(r["usd_total"], r["divisor"], task.get("cost_ceiling_usd_per_real"))
    return rows


CATALOG_ROOT = HERE / "catalogs"


def listed_models(venue, catalog_root=CATALOG_ROOT):
    """(catalog date, set of model ids) from a venue's newest archived catalog.

    The archive holds every model the venue served, paid and free, so absence
    from it is delisting rather than a change of price. None if the venue has
    no archive.
    """
    paths = sorted((catalog_root / venue).glob("*.json")) if venue else []
    if not paths:
        return None, None
    data = json.loads(paths[-1].read_text(encoding="utf-8"))
    payload = data.get("payload") or {}
    rows = payload.get("data") or payload.get("models") or (payload if isinstance(payload, list) else [])
    ids = {r.get("id") or r.get("model") or r.get("name") for r in rows if isinstance(r, dict)}
    return paths[-1].stem, ids


def open_disqualifiers(observations, catalog_root=CATALOG_ROOT):
    """model -> (date, reason) for a disqualifier no later run has cleared.

    A disqualifier is open while no run-backed row for the same model is
    dated on or after it. Same-day success clears it: the record is dated by
    day, and a refusal fixed the same afternoon is not standing.

    Delisting is a disqualifier too, decided 2026-09-06: a model absent from
    the newest archived catalog of the venue its rows name is `delisted`,
    dated by that catalog, and a later run cannot clear it, only a catalog
    that lists it again. A rating on a delisted row stays on the record; the
    manifest cannot carry a model the venue no longer serves.
    """
    latest_success = {}
    marks = {}
    venues = {}
    for fields in observations:
        if fields.get("source") == "oxbox-run" and fields.get("kind") in ROW_KINDS:
            venues.setdefault(fields["model"], fields.get("venue"))
    delisted = {}
    listings = {}
    for model, venue in venues.items():
        if model in ("", "-") or not venue:
            continue
        if venue not in listings:
            listings[venue] = listed_models(venue, catalog_root)
        date, ids = listings[venue]
        if ids is not None and model not in ids:
            delisted[model] = (date, "delisted")
    for fields in observations:
        if fields.get("source") != "oxbox-run":
            continue
        model = fields["model"]
        date = fields.get("date", "")
        if fields.get("disqualifier"):
            if date >= marks.get(model, ("", ""))[0]:
                marks[model] = (date, fields["disqualifier"])
        elif fields.get("kind") in ROW_KINDS:
            latest_success[model] = max(latest_success.get(model, ""), date)
    standing = {m: mark for m, mark in marks.items()
                if latest_success.get(m, "") < mark[0]}
    for model, mark in delisted.items():
        standing.setdefault(model, mark)
    return standing


def per_fixture(rows):
    """(model, fixture) -> n and the worst digit seen on that fixture."""
    out = {}
    for row in rows:
        key = (row["venue"], row["model"], row["fixture"])
        cell = out.setdefault(key, {"n": 0, "quality": None, "cost": None,
                                    "speed": None, "role": row["role"],
                                    "findings": 0, "real": 0, "usd_model": None,
                                    "any_raw": False})
        cell["n"] += 1
        for dim in DERIVED_KEYS:
            if row[dim] is not None:
                cell[dim] = row[dim] if cell[dim] is None else min(cell[dim], row[dim])
        if row["findings"] is not None:
            cell["findings"] += row["findings"]
            cell["real"] += row["real"] or 0
            cell["any_raw"] = True
        if row["usd_model"] is not None:
            cell["usd_model"] = (cell["usd_model"] or 0) + row["usd_model"]
    return out


def baseline_only(observations):
    """Models whose every run-backed observation is a baseline."""
    roles = {}
    for fields in observations:
        if fields.get("source") != "oxbox-run" or fields["model"] in ("", "-"):
            continue
        roles.setdefault(fields["model"], set()).add(fields.get("role", "candidate"))
    return {m for m, r in roles.items() if r == {"baseline"}}


def manifest_expected(ratings, disqualifiers, baseline_models):
    """The models a derived manifest must carry, in tier order.

    Goods first, then Acceptables; within a tier the editor's order is the
    file's order. A standing disqualifier or baseline-only status holds a
    model out regardless of its rating.
    """
    expected = []
    for tier in IN_MANIFEST:
        for model, entry in ratings.items():
            if entry.get("rating") != tier:
                continue
            if model in disqualifiers or model in baseline_models:
                continue
            expected.append(model)
    return expected


def check_manifest(manifest, ratings, disqualifiers, baseline_models):
    """Problems with a manifest against the rating rule. Empty means it holds."""
    problems = []
    entries = manifest.get("recommendations", [])
    models = [e.get("model") for e in entries]
    for model in models:
        rating = (ratings.get(model) or {}).get("rating")
        if rating not in IN_MANIFEST:
            problems.append("%s is in the manifest rated %r" % (model, rating))
        if model in disqualifiers:
            problems.append("%s is in the manifest with %s standing since %s"
                            % (model, disqualifiers[model][1], disqualifiers[model][0]))
        if model in baseline_models:
            problems.append("%s is in the manifest on baseline runs only" % model)
    expected = manifest_expected(ratings, disqualifiers, baseline_models)
    for model in expected:
        if model not in models:
            problems.append("%s is rated %s and missing from the manifest"
                            % (model, ratings[model]["rating"]))
    tiers = [IN_MANIFEST.index((ratings.get(m) or {}).get("rating"))
             for m in models if (ratings.get(m) or {}).get("rating") in IN_MANIFEST]
    if tiers != sorted(tiers):
        problems.append("an Acceptable is ranked above a Good")
    return problems


# --- rendering -------------------------------------------------------------

def _d(value):
    return "-" if value is None else str(value)


def catalog_markdown(observations=None, tasks=None, ratings=None):
    observations = load_observations() if observations is None else observations
    tasks = load_corpus() if tasks is None else tasks
    ratings = load_editor_ratings() if ratings is None else ratings
    rows = run_rows(observations, tasks)
    cells = per_fixture(rows)
    disq = open_disqualifiers(observations)
    baselines = baseline_only(observations)

    out = ["## Tried", "",
           "| Model | Venue | Runs | Disqualifier | Editor's Rating | Why |",
           "|---|---|---|---|---|---|"]
    models = {}
    for (venue, model, _), cell in cells.items():
        entry = models.setdefault((venue, model), {"n": 0, "role": cell["role"]})
        entry["n"] += cell["n"]
    for (venue, model), entry in sorted(models.items(), key=lambda kv: kv[0][1]):
        rating = ratings.get(model) or {}
        if model in baselines:
            shown, why = "baseline", "reference only, never in the manifest"
        elif rating.get("rating"):
            shown = "%s (%s)" % (rating["rating"], rating.get("date", "undated"))
            why = rating.get("why") or ""
        else:
            shown, why = "unrated", ""
        mark = disq.get(model)
        out.append("| `%s` | %s | %d | %s | %s | %s |" % (
            model, venue, entry["n"],
            "%s since %s" % (mark[1], mark[0]) if mark else "none",
            shown, why))

    out += ["", "## Per fixture", "",
            "| Model | Fixture | n | Quality | Cost | Speed | Real / findings | Model USD |",
            "|---|---|---|---|---|---|---|---|"]
    for (venue, model, fixture), cell in sorted(cells.items(),
                                                key=lambda kv: (kv[0][1], kv[0][2] or "")):
        raw = "%d / %d" % (cell["real"], cell["findings"]) if cell["any_raw"] else "-"
        usd = "-" if cell["usd_model"] is None else "$%.4f" % cell["usd_model"]
        out.append("| `%s` | %s | %d | %s | %s | %s | %s | %s |" % (
            model, fixture or "(real work)", cell["n"], _d(cell["quality"]),
            _d(cell["cost"]), _d(cell["speed"]), raw, usd))
    out += ["", "Digits are bucketed from recorded values; the worst run on a fixture "
            "is shown when n > 1. A dash is unmeasured, never zero. Rubric:", "",
            rubric_markdown()]
    return "\n".join(out)


def checkers_in(observations):
    """Every supervisor that has checked a run-backed row, in the record."""
    names = set()
    for f in observations:
        if f.get("harness_window") and f.get("harness_model"):
            names.add(f["harness_model"])
    return sorted(names)


def same_batch(observations, prices):
    """Runs checked by more than one supervisor: per checker, tokens, USD, time."""
    by_run = {}
    # Rows' own windows first, then check records, so a deliberate check of a
    # run replaces the window the row's session happened to record.
    ordered = sorted((f for f in observations
                      if f.get("run") and f.get("harness_window") and f.get("harness_model")),
                     key=lambda f: 0 if f.get("kind") in ROW_KINDS else 1)
    for f in ordered:
        if f.get("kind") in ROW_KINDS and "," in f["run"]:
            continue
        # A metered check keeps its own row beside the in-harness one, so the
        # same checker's agentic session and single billed request sit side by
        # side; the label names the venue that billed it.
        label = f["harness_model"] + (" via %s (billed)" % f["harness_venue"]
                                      if billed(f) is not None else "")
        for run_id in [x.strip() for x in f["run"].split(",")]:
            by_run.setdefault(run_id, {})[label] = f
    out = []
    for run_id, per in sorted(by_run.items()):
        if len({f["harness_model"] for f in per.values()}) < 2 and len(per) < 2:
            continue
        entry = {"run": run_id, "checkers": []}
        for name, f in sorted(per.items()):
            entry["checkers"].append({
                "checker": name,
                "billed": billed(f) is not None,
                "input": _num(f.get("harness_in")), "output": _num(f.get("harness_out")),
                "cache_read": _num(f.get("harness_cache_read")),
                "cache_write": _num(f.get("harness_cache_write")),
                "usd": price_window(f, prices),
                "seconds": _num(f.get("harness_seconds")) if f.get("harness_seconds")
                           else window_seconds(f["harness_window"]),
                "note": f.get("harness_note"),
            })
        out.append(entry)
    return out


def cost_rows(observations, prices, tasks=None, checker=None):
    """Per model: the model half and the checking half, per run and per real.

    The model half is the mean of usd_model over the model's priced rows. The
    checking half is every distinct harness window those rows name, priced at
    the supervisor's list price and counted once, split evenly across the
    rows (of any model) it covers -- an upper bound, since a window holds
    whatever else the session did. "Real" uses the same divisor as the cost
    digit: verified-real findings on a review run, hits on a seeded fixture,
    zero when a required gate failed. USD per real is computed over the rows
    that have a window, so an unwindowed run's findings do not dilute it.
    """
    tasks = load_corpus() if tasks is None else tasks
    rows = run_rows(observations, tasks, prices)
    if checker is not None:
        for r in rows:
            f = r["checks"].get(checker)
            r["harness_model"] = checker if f else None
            r["harness_window"] = f.get("harness_window") if f else None
            r["_fields"] = f if f else r["_fields"]
            r["harness_unpriced"] = f.get("harness_unpriced") if f else None
            r["_billed"] = billed(f) is not None if f else False
    windows = {}
    for r in rows:
        if r["harness_window"]:
            key = (r["harness_model"], r["harness_window"])
            w = windows.setdefault(key, {"usd": price_window(r["_fields"], prices),
                                        "seconds": window_seconds(r["harness_window"]), "rows": 0})
            w["rows"] += 1
    per_model = {}
    for r in rows:
        m = per_model.setdefault(r["model"], {"venue": r["venue"], "runs": 0, "usd_sum": 0.0,
                                              "priced": 0, "real": 0, "check": 0.0,
                                              "check_runs": 0, "check_real": 0,
                                              "check_model_usd": 0.0, "unpriced": False,
                                              "checked_by": set(), "wall": 0.0, "timed": 0,
                                              "check_seconds": 0.0, "check_timed": 0,
                                              "check_wall": 0.0, "output_unmeasured": False,
                                              "billed_runs": 0})
        m["runs"] += 1
        if r["usd_model"] is not None:
            m["usd_sum"] += r["usd_model"]
            m["priced"] += 1
        m["real"] += r["divisor"] or 0
        if r["wall_s"] is not None:
            m["wall"] += r["wall_s"]
            m["timed"] += 1
        # Two cases where the checking half is zero by construction and no
        # window applies: a fixture scored mechanically (git-apply, json-parse),
        # where the scorer is the check; and a review run that emitted nothing,
        # where there is nothing to read. Decided 2026-09-06 while removing
        # the "unpriced share" caveat: a write-up window is not a check.
        task = tasks.get(r["fixture"] or "", {})
        mechanical = task.get("verification") in ("git-apply", "json-parse")
        empty = r["findings"] == 0 and r["hits"] is None
        if mechanical or empty:
            m["check_runs"] += 1
            m["check_real"] += r["divisor"] or 0
            m["check_model_usd"] += r["usd_model"] or 0
            m["check_wall"] += r["wall_s"] or 0
            m["check_timed"] += 1
            continue
        if r["harness_window"]:
            w = windows[(r["harness_model"], r["harness_window"])]
            if w["usd"] is None:
                m["unpriced"] = True
            else:
                m["check"] += w["usd"] / w["rows"]
                m["checked_by"].add(r["harness_model"])
                m["check_wall"] += r["wall_s"] or 0
                if w["seconds"] is not None:
                    m["check_seconds"] += w["seconds"] / w["rows"]
                    m["check_timed"] += 1
                m["check_runs"] += 1
                m["check_real"] += r["divisor"] or 0
                m["check_model_usd"] += r["usd_model"] or 0
                if r.get("_billed"):
                    m["billed_runs"] += 1
            note = (r["harness_unpriced"] or "").strip().lower()
            if note.startswith("output unmeasured"):
                m["output_unmeasured"] = True   # every in-harness check has this; a floor
            elif note:
                m["unpriced"] = True            # work outside the window entirely
    out = []
    for model, m in per_model.items():
        model_avg = (m["usd_sum"] / m["priced"]) if m["priced"] else None
        per_real = None
        if m["check_runs"] and m["check_real"]:
            per_real = (m["check_model_usd"] + m["check"]) / m["check_real"]
        out.append({
            "model": model, "venue": m["venue"], "runs": m["runs"],
            "tier": tier_of(model, prices, model_avg),
            "model_usd_per_run": model_avg,
            "check_usd_per_run": (m["check"] / m["check_runs"]) if m["check_runs"] else None,
            # Both halves over the checked runs only, so an unchecked run's model
            # half is not averaged in against a checking half it never had.
            "total_usd_per_run": ((m["check_model_usd"] + m["check"]) / m["check_runs"])
                                 if m["check_runs"] else None,
            "checked_by": ", ".join(sorted(m["checked_by"])),
            "billed_runs": m["billed_runs"],
            "check_runs": m["check_runs"], "check_unpriced": m["unpriced"],
            "output_unmeasured": m["output_unmeasured"],
            "wall_per_run": (m["wall"] / m["timed"]) if m["timed"] else None,
            "check_seconds_per_run": (m["check_seconds"] / m["check_timed"]) if m["check_timed"] else None,
            "total_seconds_per_run": ((m["check_wall"] + m["check_seconds"]) / m["check_runs"])
                                     if m["check_timed"] else None,
            "real": m["real"], "check_real": m["check_real"],
            "usd_per_real": per_real,
        })
    return out


def costs_markdown(observations=None, prices=None):
    observations = load_observations() if observations is None else observations
    if prices is None:
        prices, catalog = load_prices()
    else:
        catalog = "given"
    order = {"frontier": 0, "cheap paid": 1, "paid, price unknown": 2, "free": 3}

    def usd(v):
        return "-" if v is None else "$%.4f" % v

    def clock(v):
        if v is None:
            return "-"
        return "%d s" % round(v) if v < 120 else "%.0f min" % (v / 60)

    out = ["## What it costs", ""]
    for name in checkers_in(observations):
        rows = cost_rows(observations, prices, checker=name)
        unchecked = sorted(r["model"] for r in rows if not r["check_runs"])
        rows = [r for r in rows if r["check_runs"]]
        rows.sort(key=lambda r: (order.get(r["tier"], 9), -(r["model_usd_per_run"] or 0), r["model"]))
        out += ["### Checked by %s (%s)" % (name, supervisor_price_line(HARNESS_MODEL_IDS.get(name, ""), prices)), "",
                "| Tier | Model | Runs | Model half, per run | Model time, per run | Checked runs | Checking half, per run (upper bound) | Checking time, per run (window share) | Total, per checked run | Total time, per checked run | Real findings | USD per real finding |",
                "|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for r in rows:
            check = usd(r["check_usd_per_run"])
            if r["output_unmeasured"]:
                check += " †"
            if r["billed_runs"]:
                check += " ‡" if r["billed_runs"] == r["check_runs"] else " (‡ %d of %d)" % (r["billed_runs"], r["check_runs"])
            if r["check_unpriced"]:
                check += " + an unpriced share"
            out.append("| %s | `%s` | %d | %s | %s | %s | %s | %s | %s | %s | %d | %s |" % (
                r["tier"], r["model"], r["runs"], usd(r["model_usd_per_run"]), clock(r["wall_per_run"]),
                "%d of %d" % (r["check_runs"], r["runs"]) if r["check_runs"] else "none",
                check, clock(r["check_seconds_per_run"]),
                usd(r["total_usd_per_run"]), clock(r["total_seconds_per_run"]),
                r["real"], usd(r["usd_per_real"])))
        if any(r["output_unmeasured"] for r in rows):
            out += ["", "† Checked by a fresh subagent whose output tokens the harness does not record; "
                        "input and cache are priced, output is not, so the figure is a floor."]
        if any(r["billed_runs"] for r in rows):
            out += ["", "‡ Metered: the verification task sent through OpenRouter as one request, and the "
                        "figure is what the venue billed, not a priced window. Where a run has both, the bill wins."]
        if unchecked:
            out += ["", "No run checked by this supervisor: %s." % ", ".join("`%s`" % m for m in unchecked)]
        out.append("")
    pairs = same_batch(observations, prices)
    if pairs:
        out += ["### The same batch, checked by more than one supervisor", ""]
        for entry in pairs:
            out += ["Run `%s`:" % entry["run"], "",
                    "| Checker | Input | Output | Cache read | Cache write | USD | Wall clock |",
                    "|---|---|---|---|---|---|---|"]
            for c in entry["checkers"]:
                out.append("| %s | %s | %s | %s | %s | %s | %s |" % (
                    c["checker"], commas(c["input"]), commas(c["output"]) + (" (derived)" if c["note"] and not c["billed"] else ""),
                    commas(c["cache_read"]), commas(c["cache_write"]),
                    usd(c["usd"]) + (" billed" if c["billed"] else " at list"), clock(c["seconds"])))
            notes = ["%s: %s" % (c["checker"], c["note"]) for c in entry["checkers"] if c["note"] and not c["billed"]]
            if notes:
                out += ["", "Derived. " + " ".join(n + "." for n in notes)]
            out.append("")
    out += ["The model half is what the venue billed or the catalog computes for the run. The checking half is the supervisor's tokens in the window that verified the run, "
            "priced at the supervisor's list price on the %s OpenRouter catalog with cache reads "
            "and writes, counted once per window and split across the runs it covers. A window "
            "holds whatever else the session did, so it is an upper bound. A real finding is a "
            "verified-real finding on a review run or a correct hit on a seeded fixture, and USD per "
            "real finding is both halves over the checked runs divided by the real findings those "
            "runs produced. Cheap paid means a list "
            "completion price at or under $%.2f per million. Time is a cost too: model time is the "
            "run's wall clock from the log timestamps; checking time is the verification window's "
            "span, split across the runs it covers, an upper bound like the dollars beside it. The "
            "total is both halves per checked run, so an unchecked run's model half is not averaged "
            "against a checking half it never had; total time is the model's wall clock plus the "
            "checking window share, per checked run." % (catalog, CHEAP_COMPLETION_USD_PER_MTOK),
            "",
            "**One table per checking model, because the checking model sets the checking half.** "
            "A different supervisor is a different bill and a different token count, not a repricing; "
            "where one run was checked by more than one supervisor the same-batch table above shows "
            "each on its own tokens. USD per real finding uses the supervisor that actually checked."]
    return "\n".join(out)


def commas(value):
    return "-" if value is None else "{:,}".format(int(value))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--rubric", action="store_true", help="print the threshold table")
    parser.add_argument("--json", action="store_true", help="rows as JSON")
    parser.add_argument("--costs", action="store_true",
                        help="the cost comparison: model half, checking half, per tier")
    args = parser.parse_args(argv)
    if args.rubric:
        print(rubric_markdown())
        return 0
    if args.costs:
        print(costs_markdown())
        return 0
    if args.json:
        observations = load_observations()
        rows = run_rows(observations, load_corpus())
        print(json.dumps({"rows": rows,
                          "disqualifiers": open_disqualifiers(observations),
                          "baseline_only": sorted(baseline_only(observations)),
                          "ratings": load_editor_ratings()}, indent=2))
        return 0
    print(catalog_markdown())
    return 0


if __name__ == "__main__":
    sys.exit(main())
