#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Curtis Galloway
# SPDX-License-Identifier: Apache-2.0
"""The cost tables as a workbook, one tab per checking model, for a spreadsheet.

The Doc could not hold a twelve-column table, so the editor asked for a
spreadsheet (2026-09-06). Everything here is read from ratings.py; nothing is
typed. Needs openpyxl, so run it with uv rather than the system python:

    uv run --with openpyxl python3 costsheet.py out.xlsx

Upload the result to the Oxbox Survey Drive folder; Drive converts it to a
Google Sheet with the tabs intact.
"""

import importlib.util, sys
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from openpyxl.utils import get_column_letter
spec = importlib.util.spec_from_file_location("rt", str(__import__("pathlib").Path(__file__).resolve().parent / "ratings.py"))
rt = importlib.util.module_from_spec(spec); spec.loader.exec_module(rt)
obs = rt.load_observations(); prices, catalog = rt.load_prices(); tasks = rt.load_corpus()
wb = Workbook(); wb.remove(wb.active)
def sheet(name, header, rows, note=None):
    ws = wb.create_sheet(name[:31]); ws.append(header)
    for c in ws[1]: c.font = Font(bold=True); c.alignment = Alignment(wrap_text=True, vertical="top")
    for r in rows: ws.append(r)
    for i, h in enumerate(header, 1):
        width = max([len(str(h))] + [len(str(r[i-1])) for r in rows if r[i-1] is not None]) if rows else len(h)
        ws.column_dimensions[get_column_letter(i)].width = min(max(10, width + 2), 46)
    ws.freeze_panes = "B2"
    if note:
        ws.append([]); ws.append([note])
    return ws
order = {"frontier": 0, "cheap paid": 1, "paid, price unknown": 2, "free": 3}
def money(v): return None if v is None else round(v, 4)
def secs(v): return None if v is None else round(v)
for name in rt.checkers_in(obs):
    rows = rt.cost_rows(obs, prices, tasks, checker=name)
    rows.sort(key=lambda r: (order.get(r["tier"], 9), -(r["model_usd_per_run"] or 0), r["model"]))
    sheet("Checked by " + name.replace("claude-", ""),
          ["Tier", "Model", "Venue", "Runs", "Checked runs", "Model half USD/run", "Model time s/run",
           "Checking half USD/run (upper bound)", "Checking time s/run", "Checker output unmeasured (floor)?", "Unpriced share outside any window?",
           "Total USD/checked run", "Total time s/checked run", "Real findings", "USD per real finding"],
          [[r["tier"], r["model"], r["venue"], r["runs"], r["check_runs"], money(r["model_usd_per_run"]),
            secs(r["wall_per_run"]), money(r["check_usd_per_run"]), secs(r["check_seconds_per_run"]),
            "yes" if r.get("output_unmeasured") else "", "yes" if r["check_unpriced"] else "",
            money(r["total_usd_per_run"]), secs(r["total_seconds_per_run"]),
            r["real"], money(r["usd_per_real"])] for r in rows],
          "Checker %s at %s. Prices from the %s OpenRouter catalog. Windows are upper bounds, counted once and split across the runs they cover. Real finding: verified-real on a review run or a correct hit on a seeded fixture." % (name, rt.supervisor_price_line(rt.HARNESS_MODEL_IDS.get(name, ""), prices), catalog))
pairs = rt.same_batch(obs, prices)
sheet("Same batch, two checkers", ["Run", "Checker", "Input", "Output", "Output derived?", "Cache read", "Cache write", "USD at own list price", "Wall clock s"],
      [[e["run"], c["checker"], c["input"], c["output"], "yes" if c["note"] else "", c["cache_read"], c["cache_write"], money(c["usd"]), secs(c["seconds"])] for e in pairs for c in e["checkers"]],
      "Derived output = the Agent tool's reported total minus input minus cache writes; subagent transcripts do not record final output.")
rows = rt.run_rows(obs, tasks); cells = rt.per_fixture(rows); disq = rt.open_disqualifiers(obs); ratings = rt.load_editor_ratings(); baselines = rt.baseline_only(obs)
sheet("Per fixture", ["Model", "Venue", "Fixture", "n", "Quality", "Cost", "Speed", "Real", "Findings", "Model USD"],
      [[m, v, f or "(real work)", c["n"], c["quality"], c["cost"], c["speed"], c["real"] if c["any_raw"] else None, c["findings"] if c["any_raw"] else None, money(c["usd_model"])]
       for (v, m, f), c in sorted(cells.items(), key=lambda kv: (kv[0][1], kv[0][2] or ""))],
      "Digits bucketed from recorded values; worst run on a fixture when n > 1. Blank is unmeasured, never zero.")
sheet("Ratings", ["Model", "Venue", "Runs", "Disqualifier", "Editor's Rating", "Rated", "Why"],
      [[m, v, sum(c["n"] for (vv, mm, _), c in cells.items() if mm == m), ("%s since %s" % (disq[m][1], disq[m][0])) if m in disq else "",
        "baseline" if m in baselines else ((ratings.get(m) or {}).get("rating") or "unrated"),
        (ratings.get(m) or {}).get("date") or "", (ratings.get(m) or {}).get("why") or ""]
       for (v, m) in sorted({(v, m) for (v, m, _) in cells}, key=lambda x: x[1])])
sheet("Rubric", ["Dimension", "Measured", "5", "4", "3", "2", "1", "0"], [[n, m] + lv for n, m, lv in rt.RUBRIC])
out = sys.argv[1]; wb.save(out); print("wrote", out, [ws.title for ws in wb.worksheets])
