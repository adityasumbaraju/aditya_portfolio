"""
Shared fixtures for the manuscript-results test suite.

A single session-scoped fixture runs all five result-generating scripts once
(they are the source of truth, not committed JSON artifacts), then each test
reads the freshly produced output files and asserts the manuscript's published
values. This catches regressions in the code, not just drift in saved files.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
OUTPUTS = ROOT / "outputs"


# ---------------------------------------------------------------------------
# Session-scoped: run every result script exactly once for the whole suite.
# ---------------------------------------------------------------------------
SCRIPTS = [
    "main.py",
    "sensitivity_analysis.py",
    "generate_figures.py",
    "decision_experiment.py",
    "reviewer_fixes.py",
]


@pytest.fixture(scope="session", autouse=True)
def run_all_scripts():
    """Run the five result scripts once before any test executes."""
    for script in SCRIPTS:
        result = subprocess.run(
            [sys.executable, str(ROOT / script)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, (
            f"{script} failed (exit {result.returncode}):\n"
            f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
    yield


# ---------------------------------------------------------------------------
# Data loaders — each returns the parsed JSON for one manuscript artifact.
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def simulation_results():
    return json.loads((OUTPUTS / "simulation_results.json").read_text())


@pytest.fixture(scope="session")
def sensitivity_results():
    return json.loads((OUTPUTS / "sensitivity_results.json").read_text())


@pytest.fixture(scope="session")
def decision_experiment():
    return json.loads((OUTPUTS / "decision_experiment.json").read_text())


@pytest.fixture(scope="session")
def reviewer_fixes():
    return json.loads((OUTPUTS / "reviewer_fixes.json").read_text())


@pytest.fixture(scope="session")
def roi_statistics():
    import pandas as pd

    return pd.read_csv(OUTPUTS / "roi_statistics.csv")
