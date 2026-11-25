# SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0
"""M6: every relative link in the tracked Markdown files resolves (scripts/check_links.py)."""

from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load():
    spec = importlib.util.spec_from_file_location("check_links", ROOT / "scripts" / "check_links.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_repository_links_resolve():
    checked, problems = _load().check(ROOT)
    assert checked > 0
    assert problems == []


def test_checker_detects_broken_path_and_anchor(tmp_path):
    mod = _load()
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    (tmp_path / "a.md").write_text(
        "# Title\n\n## Second part\n\n[ok](b.md) [ok anchor](#second-part) [web](https://example.org)\n"
        "[missing](nope.md) [bad anchor](b.md#absent) `[in code](ignored.md)`\n\n```\n[fenced](ignored.md)\n```\n",
        encoding="utf-8",
    )
    (tmp_path / "b.md").write_text("# B\n", encoding="utf-8")
    subprocess.run(["git", "add", "a.md", "b.md"], cwd=tmp_path, check=True)
    checked, problems = mod.check(tmp_path)
    assert checked == 4
    assert len(problems) == 2
    assert any("missing target nope.md" in p for p in problems)
    assert any("missing anchor #absent" in p for p in problems)


def test_slug_matches_github_style():
    mod = _load()
    assert mod.slug("5.2 EXP-002: power-law forgetting (confirmatory)") == "52-exp-002-power-law-forgetting-confirmatory"
