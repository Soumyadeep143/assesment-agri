"""Shared fixtures.  The notebook's own code cells are executed in a sandbox copy of the project, so every
test exercises the REAL notebook code (not a re-implementation)."""
import json, os, pathlib, shutil, time, warnings
import matplotlib
matplotlib.use("Agg")
import nbformat, pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
NB_PATH = pathlib.Path(os.environ.get("NB_PATH", ROOT / "price_forecast.ipynb"))
RESULTS = []


@pytest.fixture(scope="session")
def nbk():
    return nbformat.read(NB_PATH, 4)


@pytest.fixture(scope="session")
def md_text(nbk):
    return "\n".join(c.source for c in nbk.cells if c.cell_type == "markdown")


@pytest.fixture(scope="session")
def code_text(nbk):
    return "\n".join(c.source for c in nbk.cells if c.cell_type == "code")


@pytest.fixture(scope="session")
def sections(nbk):
    """dict {section_number: concatenated text of the section's cells (markdown + code)}"""
    import re
    out, cur = {}, 0
    for c in nbk.cells:
        if c.cell_type == "markdown":
            m = re.match(r"\s*##\s+(\d+)\.", c.source)
            if m:
                cur = int(m.group(1))
            elif re.match(r"\s*##\s+Conclusion", c.source):
                cur = 99
        out[cur] = out.get(cur, "") + "\n" + c.source
    return out


@pytest.fixture(scope="session")
def ns(nbk, tmp_path_factory):
    """Execute every code cell of the notebook (fresh run) inside a temp working dir."""
    import matplotlib.pyplot as plt
    wd = tmp_path_factory.mktemp("nbrun")
    shutil.copy(ROOT / "price_data.csv", wd / "price_data.csv")
    old = os.getcwd(); os.chdir(wd)
    g = {"__name__": "__nb__", "display": lambda *a, **k: None}
    t0 = time.time()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for c in nbk.cells:
            if c.cell_type == "code":
                exec(compile(c.source, "<nb-cell>", "exec"), g)
    plt.close("all")
    g["_workdir"] = wd; g["_runtime"] = time.time() - t0
    yield g
    os.chdir(old)


def pytest_runtest_makereport(item, call):
    if call.when == "call" or (call.when == "setup" and call.excinfo):
        RESULTS.append({"nodeid": item.nodeid, "doc": (item.function.__doc__ or "").strip(),
                        "outcome": "passed" if (call.excinfo is None) else
                        ("skipped" if call.excinfo.typename == "Skipped" else "failed"),
                        "duration": round(call.duration, 4),
                        "error": "" if call.excinfo is None else str(call.excinfo.value)[:300]})


def pytest_sessionfinish(session, exitstatus):
    path = pathlib.Path(os.environ.get("TEST_RESULTS_JSON", ROOT / "tests" / "results.json"))
    path.write_text(json.dumps(RESULTS, indent=1))
