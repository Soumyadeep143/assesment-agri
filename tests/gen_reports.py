"""Generate the three Markdown reports from tests/results.json (real pytest results)."""
import json, pathlib, re, collections, datetime, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
R = json.load(open(ROOT / "tests" / "results.json"))
MUT = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else None

def kind(n): return "unit" if "test_unit.py" in n else "integration"
def cls(n):
    m = re.search(r"::(Test\w+)::", n); return m.group(1) if m else "-"
def name(n): return n.split("::")[-1]
def pretty(c): return re.sub(r"(?<!^)(?=[A-Z])", " ", c.replace("Test", "", 1))
AREA = {
 "DataLoading": "A. Data loading & schema (data dictionary)", "Cleaning": "B. Cleaning: missing values, outliers, anomalies",
 "ForecastFunctions": "C. Forecasting functions (baselines, ETS, ARIMA, GBM)", "Metrics": "D. Evaluation metrics",
 "RollingCV": "E. Rolling-origin cross-validation", "SelectionTuning": "F. Model selection & fine-tuning", "Holdout": "G. Train vs test hold-out, residuals, robustness",
 "Forecast": "H. 12-month forecast & intervals", "Artifact": "I. Model artifact & predict()", "Monitoring": "J. Monitoring helpers (PSI, rolling MAPE)",
 "NotebookStructure": "1. Notebook as a deliverable", "RequirementAlignment": "2. Requirement alignment (brief, sentence by sentence)",
 "PipelineIntegration": "3. Pipeline integration (clean → CV → model → forecast → artifact)", "NarrativeConsistency": "4. Narrative numbers vs computed numbers",
 "DeploymentSnippets": "5a. Deployment snippets (Django / Next.js / React Native)", "FastAPIService": "5b. FastAPI service executed with TestClient",
 "MonitoringAndBusinessLoop": "6. Monitoring & business-loop coverage"}
now = datetime.date.today().isoformat()

def report(which, title, intro):
    rows = [r for r in R if kind(r["nodeid"]) == which]
    p = sum(r["outcome"] == "passed" for r in rows); f = sum(r["outcome"] == "failed" for r in rows); s = sum(r["outcome"] == "skipped" for r in rows)
    L = [f"# {title}", "", f"_Generated {now} from the real pytest run (`tests/results.json`). Python/pytest executed the notebook's own code cells in a sandbox copy._", "", intro, "",
         "## Summary", "", "| Metric | Value |", "|---|---|", f"| Total test cases | **{len(rows)}** |", f"| Passed | **{p}** |", f"| Failed | **{f}** |", f"| Skipped | {s} |",
         f"| Pass rate | **{p/len(rows)*100:.1f}%** |", f"| Cumulative test time | {sum(r['duration'] for r in rows):.1f}s (excludes the one-off notebook execution fixture) |", ""]
    if f:
        L += ["### Failures", ""] + [f"- `{name(r['nodeid'])}` — {r['error']}" for r in rows if r["outcome"] == "failed"] + [""]
    by = collections.OrderedDict()
    for r in rows: by.setdefault(cls(r["nodeid"]).replace("Test", "", 1), []).append(r)
    L += ["## Results by feature area", "", "| Area | Cases | Passed |", "|---|---|---|"]
    for c, rs in by.items(): L.append(f"| {AREA.get(c, c)} | {len(rs)} | {sum(x['outcome']=='passed' for x in rs)} |")
    L += ["", "## Detailed test cases", ""]
    i = 0; pre = "U" if which == "unit" else "I"
    for c, rs in by.items():
        L += [f"### {AREA.get(c, c)}", "", "| ID | Test | What it verifies | Result |", "|---|---|---|---|"]
        for r in rs:
            i += 1; res = {"passed": "✅ PASS", "failed": "❌ FAIL", "skipped": "⏭ SKIP"}[r["outcome"]]
            L.append(f"| {pre}-{i:03d} | `{name(r['nodeid'])}` | {r['doc'].replace('|', '/')} | {res} |")
        L.append("")
    if MUT and which == "unit":
        pass
    return "\n".join(L), len(rows), p, f

u, nu, pu, fu = report("unit", "Unit Test Report — Monthly Price Forecasting Notebook",
    "Unit tests check **one function or one data property at a time**: schema of the CSV, each cleaning rule (including synthetic spike/level-shift inputs), each forecasting function, each metric against hand-computed values, the rolling-CV mechanics (including a no-leakage spy test), tuning grids, hold-out figures, interval maths, the saved artifact and `predict()`, and monitoring helpers. Target: **≥ 100 cases**.")
i, ni, pi_, fi = report("integration", "Integration Test Report — Monthly Price Forecasting Notebook",
    "Integration tests check **components working together and the deliverable as a whole**: the executed notebook, every sentence of the business-case brief mapped to evidence in the notebook, the end-to-end data flow (cleaning → CV → model → forecast → artifact → API), narrative numbers vs. computed numbers, and the Django / FastAPI / Next.js / React Native snippets (the FastAPI code is **actually executed** with FastAPI's TestClient). Target: **≥ 50 cases**.")
(ROOT / "UNIT_TEST_REPORT.md").write_text(u); (ROOT / "INTEGRATION_TEST_REPORT.md").write_text(i)
json.dump({"unit": [nu, pu, fu], "integration": [ni, pi_, fi]}, open(ROOT / "tests" / "counts.json", "w"))
print("unit", nu, pu, fu, "| integration", ni, pi_, fi)
