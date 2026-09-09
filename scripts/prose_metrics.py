#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Curtis Galloway
# SPDX-License-Identifier: Apache-2.0
"""Measure the prose density of an issue, so a rules change can be shown to work.

The survey's readers are engineers picking a free model, not the person who
wrote the generator, and the complaint this answers is that the issues read
dense -- long stacked clauses, unexpanded acronyms, abstractions where a verb
would do. This script does not judge prose. It counts six things that dense
prose does more of, so a before/after is a table rather than an impression.

Deliberately NOT Flesch, Flesch-Kincaid, or any grade-level composite. They
punish "endpoint context" and "supported_parameters" for being long words when
those are the correct words, and they reward a short sentence however many
clauses are nested in it. On this corpus they are close to noise.

What is counted, per issue and per section:

  sentences        count, median length, and the fraction over 30 words. The
                   distribution is the signal; a mean hides the tail that
                   actually costs the reader.
  acronyms         every one used, and the ones used before being expanded.
  nominalizations  -tion|-ment|-ance|-ence|-ency|-ity, the mechanical scan.
                   Noisy by construction -- see --terms.
  noun stacks      three or more consecutive technical-or-capitalized nouns
                   with no preposition or verb between them.
  slop             hits against the vendored EQ-Bench list (scripts/data/).

Only prose is measured. Tables, code fences, headings, HTML comments and
navigation lines are stripped first: a catalog table is meant to be dense, and
counting it would swamp the paragraphs this is about.

    python3 scripts/prose_metrics.py FILE...            # the table
    python3 scripts/prose_metrics.py --json FILE...     # for a diff
    python3 scripts/prose_metrics.py --terms FILE...    # what it matched, to audit
    python3 scripts/prose_metrics.py --sections FILE... # per section, to locate

Editions live in the oxbox.ai repo and are all rights reserved, so pass paths;
nothing here copies them in. Numbers about a text are not the text.
"""

import argparse
import json
import re
import statistics
import sys
from pathlib import Path

LONG_SENTENCE = 30  # words; the threshold the fraction is taken against

DATA = Path(__file__).resolve().parent / "data" / "slop_phrases.json"


# --------------------------------------------------------------------------
# Extracting prose from markdown
# --------------------------------------------------------------------------

def strip_to_prose(text):
    """Return [(section title, [paragraph, ...]), ...] keeping only prose.

    Drops HTML comments, fenced code, tables, headings, horizontal rules and
    the nav/link-list lines. Keeps paragraphs and list items -- the survey
    carries real argument inside bullets ("*Why you should care:*"), so
    dropping them would measure the wrong half of the issue.

    Source lines are reflowed into paragraphs first. The editions are hard
    wrapped at about 78 columns, and splitting sentences per line instead of
    per paragraph reports the wrap width (median 7 words, nothing over 30)
    rather than anything about the prose.
    """
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    sections = []
    current = ["(preamble)", []]
    buf = []
    fenced = False

    def flush():
        if buf:
            current[1].append(" ".join(buf))
            del buf[:]

    for raw in text.splitlines():
        line = raw.rstrip()
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            flush()
            fenced = not fenced
            continue
        if fenced:
            continue
        if stripped.startswith("#"):
            flush()
            if current[1]:
                sections.append(current)
            current = [stripped.lstrip("#").strip() or "(untitled)", []]
            continue
        if not stripped:
            flush()
            continue
        if stripped.startswith("|") or set(stripped) <= set("-|: "):
            flush()
            continue
        if re.fullmatch(r"(\*|-|_){3,}", stripped):
            flush()
            continue
        # nav rows: link soup joined by bullets, no sentence in them. Two or
        # more links, because a single link on its own line is a wrapped
        # paragraph's continuation, and dropping it cuts the sentence in half.
        if (re.fullmatch(r"(\[[^\]]+\]\([^)]*\)\s*[•·|,]?\s*)+", stripped)
                and len(re.findall(r"\]\(", stripped)) > 1):
            flush()
            continue
        # a bare footnote/source line: "[1]: http..."
        if re.match(r"^\[[^\]]+\]:\s*\S+$", stripped):
            flush()
            continue
        stripped = re.sub(r"^>\s?", "", stripped)
        # a new list item starts a new paragraph; its continuation lines do not
        if re.match(r"^([-*+]|\d+[.)])\s+", stripped):
            flush()
            stripped = re.sub(r"^([-*+]|\d+[.)])\s+", "", stripped)
        buf.append(stripped)
    flush()
    if current[1]:
        sections.append(current)
    return sections


def flatten_inline(text):
    """Reduce inline markdown to the words a reader actually reads."""
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)          # images
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)      # links -> text
    text = re.sub(r"\[([^\]]+)\]\[[^\]]*\]", r"\1", text)     # ref links
    text = re.sub(r"`([^`]*)`", lambda m: m.group(1).replace(" ", " "),
                  text)                                        # code -> one token
    text = re.sub(r"(\*\*|__|\*|_)", "", text)                 # emphasis
    text = text.replace("—", " -- ").replace("–", " - ")
    return text


# --------------------------------------------------------------------------
# Sentences
# --------------------------------------------------------------------------

# Things a naive split on "." would shatter. Each is masked before splitting.
_PROTECT = [
    r"https?://\S+",                       # URLs
    r"\b\d+\.\d+(?:\.\d+)*\b",             # 0.15, v2.2.0, 5.3
    r"\b[A-Za-z][\w-]*\.[a-z]{2,}(?:/\S*)?",  # oxbox.ai, openrouter.ai/stealth
    r"\b(?:e\.g|i\.e|cf|vs|etc|approx|Dr|Mr|Ms|Inc|Ltd|Co|No|St|Fig|Sec)\.",
    r"\b[A-Z]\.(?:[A-Z]\.)+",              # U.S.A.
]
_MASK = "\x01"  # sentinel; spelled as an escape so the file stays greppable


def split_sentences(paragraph):
    holes = []

    def stash(m):
        holes.append(m.group(0))
        return "%s%d%s" % (_MASK, len(holes) - 1, _MASK)

    masked = paragraph
    for pat in _PROTECT:
        masked = re.sub(pat, stash, masked)

    parts = re.split(r"(?<=[.!?])[\"')\]]*\s+(?=[\"'(\[]*[A-Z0-9])", masked)

    out = []
    for part in parts:
        restored = re.sub(
            _MASK + r"(\d+)" + _MASK, lambda m: holes[int(m.group(1))], part
        ).strip()
        if restored and re.search(r"[A-Za-z]", restored):
            out.append(restored)
    return out


def words_of(sentence):
    """Word tokens. A code span or slug counts as one word, which is what it
    costs a reader; a bare number or bullet marker is not a word."""
    toks = re.findall(r"[\w ][\w /:.+-]*", sentence)
    return [t for t in toks if re.search(r"[A-Za-z]", t)]


# --------------------------------------------------------------------------
# The five other counts
# --------------------------------------------------------------------------

ACRONYM_RE = re.compile(r"\b([A-Z][A-Z0-9]{1,7})\b")

# Never acronyms: single letters, units, currencies and the report's own
# evidence-tier markers, which every issue defines in its own trust section.
NOT_ACRONYMS = {
    "I", "A", "OK", "TL", "DR", "AM", "PM", "UTC", "USD", "US", "UK", "EU",
    "M", "R", "N", "GB", "MB", "KB", "TB", "K",
}

# Acronyms this readership is assumed to know, so using one unexpanded is not
# a finding. The reader is "an engineer competent in adjacent areas who has not
# read a previous issue" -- which settles GLM and SWE (expand them; they are
# this report's vocabulary, not the industry's) but genuinely does not settle
# API, JSON, CPU or AI.
#
# TODO(editor): this is the audience call, and it belongs to whoever knows the
# readership. Anything left out of this set must be expanded at first use in
# every issue, per the "Expand every acronym at first use" rule in SKILL.md.
# Expanding AI as "artificial intelligence (AI)" in a report about models
# reads as padding; leaving JSON unexpanded may not. Add or remove entries and
# re-run with --terms to see what changes.
ASSUMED_KNOWN = {
    "API", "JSON", "CPU", "AI", "URL", "HTTP", "CLI", "LLM",
    # Ruled by the editor 2026-09-08, from the first generated run:
    # NVIDIA and CNBC are well known, and GLM is clear in the context of
    # models. BIS is not, and stays flagged -- the standing regulatory caveat
    # glosses it as "(Commerce Department export controls)", which says what
    # the bureau does without ever saying that the letters are Bureau of
    # Industry and Security. A gloss is not an expansion.
    "NVIDIA", "CNBC", "GLM",
}

ACRONYM_SKIP = NOT_ACRONYMS | ASSUMED_KNOWN

NOMINALIZATION_RE = re.compile(
    r"\b([A-Za-z]{4,}?(?:tion|ment|ance|ence|ency|ity))\b", re.I
)

FUNCTION_WORDS = set("""
a an the of in on at to for from by with without into onto over under about
across through during before after between among against per via than as is
are was were be been being has have had do does did can could will would may
might must shall should and or but nor so yet if that which who whom whose
when where why how not no its it this these those their there here we you they
he she i our your his her them us me my
""".split())

VERBY = re.compile(r"(?:ed|ing|es|s)$")


def find_acronyms(prose_text):
    """Every acronym used, plus the ones whose first use has no expansion
    before it. An expansion is the parenthetical form in either direction:
    'Bureau of Industry and Security (BIS)' or 'BIS (Bureau of ...)'."""
    expanded_at = {}
    for m in re.finditer(r"\(([A-Z][A-Z0-9]{1,7})\)", prose_text):
        expanded_at.setdefault(m.group(1), m.start())
    for m in re.finditer(r"\b([A-Z][A-Z0-9]{1,7})\b\s*\([^)]{4,}\)", prose_text):
        expanded_at.setdefault(m.group(1), m.start())

    first_use = {}
    counts = {}
    for m in ACRONYM_RE.finditer(prose_text):
        acr = m.group(1)
        if acr in ACRONYM_SKIP:
            continue
        # A letter followed by digits is a model designator, not an acronym:
        # the M3 of "MiniMax M3", the S2 of "Laguna S 2.1". There is nothing
        # to expand.
        if re.fullmatch(r"[A-Z]\d+", acr):
            continue
        counts[acr] = counts.get(acr, 0) + 1
        first_use.setdefault(acr, m.start())

    unexpanded = sorted(
        acr for acr, pos in first_use.items()
        if acr not in expanded_at or expanded_at[acr] > pos
    )
    return counts, unexpanded


def find_nominalizations(prose_text):
    hits = {}
    for m in NOMINALIZATION_RE.finditer(prose_text):
        w = m.group(1).lower()
        hits[w] = hits.get(w, 0) + 1
    return hits


def find_noun_stacks(sentences, minimum=3):
    """Runs of >= `minimum` consecutive tokens that all look like nouns and
    none of which is a function word or an obvious verb form.

    A heuristic without a POS tagger, so it over-fires on title case and
    under-fires on all-lowercase stacks. Use --terms to read what it matched
    before believing a number."""
    stacks = []
    # A run may not cross punctuation. Without this the counter fires on every
    # comma list of model ids ("OpenRouter, ZenMux, Requesty"), which is a list
    # and not a noun stack.
    chunks = []
    for sentence in sentences:
        chunks.extend(re.split(r"[,;:()\[\]\u2014\u2013]|\s--\s|\.\s", sentence))
    for sentence in chunks:
        toks = re.findall(r"[\w ][\w /:_.+-]*", sentence)
        run = []
        for i, tok in enumerate(toks):
            low = tok.lower().strip(".,;:")
            technical = bool(re.search(r"[\d_/:]| |-", tok))
            capitalized = tok[:1].isupper() and i > 0
            nounish = (technical or capitalized) and low not in FUNCTION_WORDS
            if nounish and not (capitalized and VERBY.search(low) and not technical):
                run.append(tok)
                continue
            if len(run) >= minimum:
                stacks.append(" ".join(run))
            run = []
        if len(run) >= minimum:
            stacks.append(" ".join(run))
    return stacks


def is_name_run(stack):
    """True when every token is a product identifier -- capitalized, or a slug
    with a digit or hyphen in it.

    On this corpus that is most of what the stack counter finds: "Nemotron 3
    Ultra", "Claude Fable 5.1", "big-pickle OpenCode Zen". Those are names, and
    a name cannot be broken apart with a preposition, so counting them as noun
    stacks measures the subject matter rather than the writing. Both totals are
    reported; neither is dropped."""
    toks = stack.split()
    return all(t[:1].isupper() or re.search(r"[\d_/-]", t) for t in toks)


def load_slop():
    with open(DATA) as f:
        return json.load(f)["phrases"]


def find_slop(prose_text, phrases):
    low = " " + re.sub(r"\s+", " ", prose_text.lower()) + " "
    hits = {}
    for phrase in phrases:
        if " " in phrase:
            n = low.count(" " + phrase + " ")
            n += len(re.findall(re.escape(phrase) + r"[.,;:!?]", low))
        else:
            n = len(re.findall(r"\b" + re.escape(phrase) + r"\b", low))
        if n:
            hits[phrase] = n
    return hits


# --------------------------------------------------------------------------
# Assembly
# --------------------------------------------------------------------------

def measure(path, slop_phrases):
    text = Path(path).read_text(encoding="utf-8")
    sections = strip_to_prose(text)

    per_section = []
    all_sentences = []
    all_prose = []
    for name, lines in sections:
        flat = [flatten_inline(p) for p in lines]
        blob = " ".join(flat)
        sents = []
        for para in flat:
            sents.extend(split_sentences(para))
        all_sentences.extend(sents)
        all_prose.append(blob)
        lengths = [len(words_of(s)) for s in sents]
        per_section.append({
            "section": name,
            "sentences": len(sents),
            "median_words": statistics.median(lengths) if lengths else 0,
            "over_30": sum(1 for n in lengths if n > LONG_SENTENCE),
            "words": sum(lengths),
        })

    prose_text = " ".join(all_prose)
    lengths = [len(words_of(s)) for s in all_sentences]
    acr_counts, unexpanded = find_acronyms(prose_text)
    nominals = find_nominalizations(prose_text)
    stacks = find_noun_stacks(all_sentences)
    slop = find_slop(prose_text, slop_phrases)

    n = len(all_sentences)
    return {
        "file": str(path),
        "prose_words": sum(lengths),
        "sentences": n,
        "median_sentence_words": statistics.median(lengths) if lengths else 0,
        "mean_sentence_words": round(statistics.mean(lengths), 1) if lengths else 0,
        "p90_sentence_words": (
            sorted(lengths)[int(0.9 * (len(lengths) - 1))] if lengths else 0
        ),
        "sentences_over_30": sum(1 for x in lengths if x > LONG_SENTENCE),
        "frac_over_30": round(
            sum(1 for x in lengths if x > LONG_SENTENCE) / n, 4) if n else 0.0,
        "acronyms_total": sum(acr_counts.values()),
        "acronyms_distinct": len(acr_counts),
        "acronyms_unexpanded": len(unexpanded),
        "unexpanded_list": unexpanded,
        "nominalizations": sum(nominals.values()),
        "nominalizations_per_1k": round(
            1000 * sum(nominals.values()) / sum(lengths), 1) if lengths else 0,
        "noun_stacks": len(stacks),
        "noun_stacks_excl_names": sum(1 for x in stacks if not is_name_run(x)),
        "slop_hits": sum(slop.values()),
        "slop_distinct": len(slop),
        "_terms": {
            "acronyms": dict(sorted(acr_counts.items(), key=lambda kv: -kv[1])),
            "nominalizations": dict(
                sorted(nominals.items(), key=lambda kv: -kv[1])[:40]),
            "noun_stacks": stacks,
            "slop": slop,
        },
        "_sections": per_section,
    }


COLUMNS = [
    ("file", "issue", "{}"),
    ("prose_words", "prose words", "{}"),
    ("sentences", "sents", "{}"),
    ("median_sentence_words", "median", "{}"),
    ("p90_sentence_words", "p90", "{}"),
    ("frac_over_30", ">30w", "{:.0%}"),
    ("acronyms_total", "acr", "{}"),
    ("acronyms_unexpanded", "acr unexp", "{}"),
    ("nominalizations", "nominal", "{}"),
    ("nominalizations_per_1k", "/1k words", "{}"),
    ("noun_stacks", "stacks", "{}"),
    ("noun_stacks_excl_names", "stacks-x", "{}"),
    ("slop_hits", "slop", "{}"),
]


def render_table(rows):
    header = [c[1] for c in COLUMNS]
    body = []
    for r in rows:
        cells = []
        for key, _, fmt in COLUMNS:
            v = r[key]
            cells.append(Path(v).name if key == "file" else fmt.format(v))
        body.append(cells)
    widths = [max(len(header[i]), *(len(b[i]) for b in body))
              for i in range(len(header))]
    out = ["| " + " | ".join(h.ljust(widths[i]) for i, h in enumerate(header)) + " |"]
    out.append("|" + "|".join("-" * (w + 2) for w in widths) + "|")
    for b in body:
        out.append("| " + " | ".join(
            b[i].ljust(widths[i]) for i in range(len(b))) + " |")
    return "\n".join(out)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("files", nargs="+", help="markdown issues to measure")
    p.add_argument("--json", action="store_true", help="full result as JSON")
    p.add_argument("--terms", action="store_true",
                   help="print what each counter matched, to audit it")
    p.add_argument("--sections", action="store_true",
                   help="per-section sentence table, to locate the density")
    args = p.parse_args(argv)

    slop_phrases = load_slop()
    rows = [measure(f, slop_phrases) for f in args.files]

    if args.json:
        print(json.dumps(rows, indent=2))
        return 0

    print(render_table(rows))

    if args.sections:
        for r in rows:
            print("\n== %s ==" % Path(r["file"]).name)
            for s in sorted(r["_sections"], key=lambda s: -s["over_30"]):
                if not s["sentences"]:
                    continue
                print("  %-34s n=%-4d median=%-4s >30w=%d"
                      % (s["section"][:34], s["sentences"],
                         s["median_words"], s["over_30"]))

    if args.terms:
        for r in rows:
            t = r["_terms"]
            print("\n== %s ==" % Path(r["file"]).name)
            print("  unexpanded acronyms: %s" % (", ".join(r["unexpanded_list"]) or "none"))
            print("  top nominalizations: %s" % ", ".join(
                "%s(%d)" % (k, v) for k, v in list(t["nominalizations"].items())[:15]))
            print("  slop: %s" % (", ".join(
                "%s(%d)" % (k, v) for k, v in t["slop"].items()) or "none"))
            print("  noun stacks (%d, of which %d are names):"
                  % (len(t["noun_stacks"]),
                     sum(1 for x in t["noun_stacks"] if is_name_run(x))))
            for stack in t["noun_stacks"][:25]:
                print("    %-44s %s" % (
                    stack, "(name)" if is_name_run(stack) else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
