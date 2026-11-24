# SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0
"""Command line: smoke, run, report, test.

  python -m memory_research smoke [--out DIR] [--pdf]
  python -m memory_research run --config PATH [--out DIR] [--report] [--pdf]
  python -m memory_research report --results PATH [--out DIR] [--pdf]
  python -m memory_research test [pytest args...]

`run` refuses a confirmatory configuration unless its protocol is frozen
(see guard.py). Exploratory outputs are written only under a path that
contains an `exploratory` component.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from .environment import repo_root
from .guard import ProtocolNotFrozenError
from .report import build_report
from .runner import load_matrix_config, run_matrix, write_outputs
from .schema import SchemaError

EXIT_REFUSED = 3


def _default_out(root: Path, matrix: dict) -> Path:
    sub = "exploratory" if matrix["kind"] == "exploratory" else "confirmatory"
    return root / "results" / sub / matrix["experiment_id"]


def _check_out(out: Path, kind: str) -> None:
    parts = {p.lower() for p in out.resolve().parts}
    if kind == "exploratory" and "exploratory" not in parts:
        raise SystemExit(f"exploratory outputs must go under a path containing 'exploratory'; got {out}")
    if kind == "confirmatory" and "exploratory" in parts:
        raise SystemExit("confirmatory outputs must not be written under an 'exploratory' path")


def _run(config: Path, out: Path | None, report: bool, pdf: bool) -> int:
    root = repo_root()
    try:
        matrix = load_matrix_config(config)
    except (SchemaError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    out = out or _default_out(root, matrix)
    _check_out(out, matrix["kind"])
    try:
        doc = run_matrix(matrix, root, allow_confirmatory=True)
    except ProtocolNotFrozenError as exc:
        print(f"refused: {exc}", file=sys.stderr)
        return EXIT_REFUSED
    res, man = write_outputs(doc, out, root)
    s = doc["summary"]
    print(f"{doc['experiment_id']} [{doc['kind']}]: {s['n_runs']} runs, {s['n_ok']} ok, {s['n_excluded']} excluded, "
          f"{s['n_failed']} failed, wall clock {s['wall_clock_s']:.3f} s")
    print(f"results: {res}\nmanifest: {man}")
    if report:
        outputs = build_report(res, out / "report", pdf=pdf)
        for k, v in outputs.items():
            print(f"{k}: {v}")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="memory_research", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    ps = sub.add_parser("smoke", help="run the exploratory smoke matrix (protocol section 9) and its report")
    ps.add_argument("--out", type=Path)
    ps.add_argument("--pdf", action="store_true")
    pr = sub.add_parser("run", help="run a matrix configuration")
    pr.add_argument("--config", type=Path, required=True)
    pr.add_argument("--out", type=Path)
    pr.add_argument("--report", action="store_true")
    pr.add_argument("--pdf", action="store_true")
    pe = sub.add_parser("report", help="build tables, figures and a report from a result file")
    pe.add_argument("--results", type=Path, required=True)
    pe.add_argument("--out", type=Path)
    pe.add_argument("--pdf", action="store_true")
    pt = sub.add_parser("test", help="run the test suite (pytest)")
    pt.add_argument("pytest_args", nargs=argparse.REMAINDER)
    a = p.parse_args(argv)

    if a.cmd == "smoke":
        cfg = repo_root() / "experiments" / "configs" / "smoke.json"
        return _run(cfg, a.out, report=True, pdf=a.pdf)
    if a.cmd == "run":
        return _run(a.config, a.out, a.report, a.pdf)
    if a.cmd == "report":
        try:
            outputs = build_report(a.results, a.out or a.results.parent / "report", pdf=a.pdf)
        except (SchemaError, ValueError) as exc:
            print(f"error: refusing malformed result file: {exc}", file=sys.stderr)
            return 2
        for k, v in outputs.items():
            print(f"{k}: {v}")
        return 0
    if a.cmd == "test":
        return subprocess.call([sys.executable, "-m", "pytest", *a.pytest_args], cwd=repo_root())
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
