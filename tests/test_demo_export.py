# SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0
"""M5 consistency (master prompt 11.6): the demo shows the manuscript's numbers.

1. A fresh in-memory export equals the committed ``demo/public/data/results.json``.
2. Every ``display`` and ``interval_display`` string appears verbatim in the
   manuscript, except the EXP-003 per-cell strings of the ``sweep`` extension,
   which must appear verbatim in the generated EXP-003 results tables (the
   documented exception: the manuscript prints only selected cells).
3. Every decimal number in the free text of the export appears in the manuscript.
4. The engine fixture used by the browser port's vitest regenerates identically.
"""

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

import pytest

from memory_research.environment import repo_root

ROOT = repo_root()
MANUSCRIPT = (ROOT / "research/paper/manuscript.md").read_text(encoding="utf-8")
EXP003_TABLES = (ROOT / "research/experiments/EXP-003/results_tables.md").read_text(encoding="utf-8")


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def export():
    return _load("export_demo_data")


@pytest.fixture(scope="module")
def data(export):
    return export.build()


def test_committed_export_is_identical(export, data):
    committed = (ROOT / export.OUT).read_text(encoding="utf-8")
    assert committed == export.render(data)


def test_no_timestamp_and_revision_is_the_run_commit(data):
    text = json.dumps(data)
    assert not re.search(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}", text)
    assert data["code_revision"] == "d4a793df271ec2dc1963d00715e3a6525a07863f"


def test_sources_hashes_are_current(data):
    import hashlib

    for s in data["sources"]:
        assert hashlib.sha256((ROOT / s["path"]).read_bytes()).hexdigest() == s["sha256"]


def test_every_display_string_is_in_the_manuscript(data):
    missing = []
    for e in data["experiments"]:
        for x in e["estimates"]:
            for key in ("display", "interval_display"):
                v = x[key]
                if v is not None and v not in MANUSCRIPT:
                    missing.append((e["id"], x["label"], key, v))
    assert missing == []


def test_every_interval_is_printed_next_to_its_estimate(data):
    """Stronger than presence: estimate and interval appear together on one manuscript line."""
    lines = MANUSCRIPT.splitlines()
    alone = []
    for e in data["experiments"]:
        for x in e["estimates"]:
            if x["interval_display"] is None:
                continue
            iv = x["interval_display"]
            if not any(x["display"].lstrip("-") in ln and (iv in ln or iv.replace("[", "").replace("]", "").replace(", ", " to ") in ln) for ln in lines):
                alone.append((e["id"], x["label"]))
    assert alone == []


def test_sweep_strings_are_in_the_exp003_tables(data):
    """Documented exception: per-cell values are printed in the generated EXP-003 tables, not the manuscript."""
    rows = {ln.split("|")[1].strip(): ln for ln in EXP003_TABLES.splitlines() if re.match(r"\| C\d{3} ", ln)}
    assert len(data["sweep"]) == 72
    for c in data["sweep"]:
        row = rows[c["cell_id"]]
        cells = [s.strip() for s in row.split("|")[1:-1]]
        assert cells[5:10] == [c["means_display"][a] for a in ("expanding", "greedy", "leitner", "massed", "uniform")]
        assert cells[10] == c["greedy_minus_uniform"]["display"]
        assert cells[11] == c["greedy_minus_uniform"]["interval_display"]
        assert cells[12] == " > ".join(c["rank_order"])


def test_calendar_measured_strings_are_in_the_exp001_tables(data):
    """Documented exception: per-arm mean R intervals are printed in the generated EXP-001 tables."""
    tables = (ROOT / "research/experiments/EXP-001/results_tables.md").read_text(encoding="utf-8")
    for arm, m in data["calendar"]["measured"].items():
        row = next(ln for ln in tables.splitlines() if ln.startswith(f"| {arm} | 50 |"))
        cells = [s.strip() for s in row.split("|")[1:-1]]
        assert cells[2] == m["mean_R_display"] and cells[4] == m["mean_R_interval_display"]
        assert m["mean_R_display"] in MANUSCRIPT


def _strings(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from _strings(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _strings(v)


def test_free_text_numbers_are_in_the_manuscript(data):
    texts = []
    for e in data["experiments"]:
        texts += [e["verdict"], e["status"], *e["notes"]]
    texts += list(_strings(data["assumptions"])) + data["limitations"] + [data["calendar"]["note"]]
    bad = [n for t in texts for n in re.findall(r"\d+\.\d+", t) if n not in MANUSCRIPT]
    assert bad == []


def test_omega_check_is_shown_as_not_run(data):
    e = next(x for x in data["experiments"] if x["id"] == "EXP-002 ω check")
    assert e["status"].startswith("not run") and e["estimates"] == []


def test_every_registered_experiment_is_exported(data):
    import csv

    with (ROOT / "research/experiment_registry.csv").open(encoding="utf-8", newline="") as fh:
        reg = {r["exp_id"] for r in csv.DictReader(fh)}
    assert reg <= {e["id"] for e in data["experiments"]}


def test_engine_fixture_regenerates_identically():
    fx = _load("export_engine_fixture")
    assert (ROOT / fx.OUT).read_text() == fx.render(fx.build())


PUBLIC_TEXTS = ("README.md", "CITATION.cff", "articles/medium.md", "articles/linkedin.md", "demo/README.md")


@pytest.mark.parametrize("rel", PUBLIC_TEXTS)
def test_public_texts_use_only_manuscript_numbers(rel):
    """M5 (11.6): README, citation, articles and demo README use the manuscript's numbers."""
    text = (ROOT / rel).read_text(encoding="utf-8")
    text = re.sub(r"`[^`]*`", "", text)  # code spans: paths, commands, placeholders
    text = re.sub(r"sections? \d+(\.\d+)*", "", text)  # section references are not results
    bad = [n for n in re.findall(r"(?<![\w.])-?\d+\.\d+(?![\w.])", text) if n.lstrip("-") not in MANUSCRIPT]
    assert bad == []


@pytest.mark.parametrize("rel", PUBLIC_TEXTS[2:])
def test_public_texts_keep_url_placeholders(rel):
    text = (ROOT / rel).read_text(encoding="utf-8")
    assert "http://" not in text and "https://" not in text
    if rel.startswith("articles/"):
        assert "<REPOSITORY URL: unpublished>" in text and "<DEMO URL: unpublished>" in text
