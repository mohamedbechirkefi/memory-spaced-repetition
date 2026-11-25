# SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0
"""Evidence audit (master prompt 11.5): every decimal number in the manuscript,
supplement, experiment reports and claims register must equal, at its printed
precision, a value in a committed result or record file.

Integers (counts, seeds, section numbers) are not matched automatically; they
are mapped by hand in research/publication/artifact_manifest.json.

  .venv/bin/python scripts/audit_numbers.py
Writes research/publication/number_audit.json and prints the unmatched numbers.
Exit status 1 if any number is unmatched and not listed in ALLOWED.
"""

from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TARGETS = [
    "research/paper/manuscript.md",
    "research/paper/supplementary.md",
    "research/experiments/EXP-001/report.md",
    "research/experiments/EXP-002/report.md",
    "research/experiments/EXP-003/report.md",
    "research/claims_register.csv",
]

SOURCES = [
    "results/confirmatory/EXP-001/analysis/frozen_analysis.json",
    "results/confirmatory/EXP-002/analysis/frozen_analysis.json",
    "results/confirmatory/EXP-003/analysis/frozen_analysis.json",
    "results/confirmatory/EXP-001/run_manifest.json",
    "results/confirmatory/EXP-002/run_manifest.json",
    "results/confirmatory/EXP-003/run_manifest.json",
    "research/experiments/EXP-001/results_tables.md",
    "research/experiments/EXP-002/results_tables.md",
    "research/experiments/EXP-003/results_tables.md",
    "results/exploratory/SENS-001/sensitivity.json",
    "results/exploratory/CAL-001/calibration.json",
    "results/exploratory/CAL-002/model_comparison.json",
    "results/exploratory/RI-001/selection.json",
    "research/experiment_journal.jsonl",
    "research/freeze.json",
    "research/protocol.md",
    "research/experiments/EXP-001/config.json",
]

# Numbers that are definitions, not results (protocol constants, versions, thresholds).
ALLOWED = {
    "0.02": "practical-equivalence margin (protocol section 4)",
    "0.05": "test level (protocol section 7, D-015)",
    "0.07": "seed-adequacy threshold (protocol section 6)",
    "0.9": "mastery threshold (protocol section 5)",
    "0.95": "post hoc ceiling threshold of SENS-001 (stated as such)",
    "0.4": "alpha (protocol 2.5) or the target band [0.4, 0.7] (protocol 16.2)",
    "0.6": "beta (protocol 2.5)",
    "0.7": "upper end of the target band (protocol 16.2)",
    "0.3": "omega check level (EXP-002 protocol section 16)",
    "0.55": "midpoint of the target band (protocol 16.2)",
    "54.0": "h0 (protocol 15.3)",
    "0.759": "sigma (protocol 15.3)",
    "1.0": "omega (configuration)",
    "3.12.1": "Python version",
    "2.5.4": "NumPy version",
    "15.3.1": "macOS version",
    "1.0.0": "result schema version",
    "1.1": "protocol version",
    "1.0": "protocol version",
    "3.3": "section reference (Settles and Meeder 2016, sections 1 to 3.3)",
    "3.1": "section reference",
    "1e-12": "numerical constant",
    "1e-14": "bound statement",
    "15.5": "EXP-003 raw file size in MB (EXP-003 report section 7, progress.md)",
    "0.0000": "exact zero (oracle calibration error, mastery share or underflowed p-value)",
    "8.0000": "peak load",
}

NUM = re.compile(r"(?<![\w.])-?\d+\.\d+(?:e-?\d+)?(?![\w.]*\d)|(?<![\w.])-?\d+e-\d+")


def source_values_by_file() -> dict[str, list[float]]:
    out = {}
    for rel in SOURCES:
        if (ROOT / rel).exists():
            out[rel] = _values(rel)
    return out


def _values(rel: str) -> list[float]:
    vals: list[float] = []
    text = []

    def walk(x):
        if isinstance(x, bool):
            return
        if isinstance(x, (int, float)):
            vals.append(float(x))
        elif isinstance(x, dict):
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
        elif isinstance(x, str):
            text.append(x)

    raw = (ROOT / rel).read_text()
    text.append(raw)
    if rel.endswith(".json"):
        walk(json.loads(raw))
    elif rel.endswith(".jsonl"):
        for ln in raw.splitlines():
            if ln.strip():
                walk(json.loads(ln))
    for tok in NUM.findall("\n".join(text)):
        try:
            vals.append(float(tok))
        except ValueError:
            pass
    return vals


def matches(tok: str, vals: list[float]) -> bool:
    x = float(tok)
    if "e" in tok:
        return any(v != 0 and abs(v - x) <= 0.0051 * abs(x) for v in vals)
    d = len(tok.split(".")[1])
    tol = 0.5 * 10 ** (-d) + 1e-12
    for v in vals:
        if abs(v - x) <= tol:
            return True
        # percentages and relative values printed as fractions or percent
    return False


def main() -> int:
    by_file = source_values_by_file()
    report = {"targets": {}, "sources": SOURCES, "allowed": ALLOWED}
    bad = 0
    for rel in TARGETS:
        text = (ROOT / rel).read_text()
        if rel.endswith(".csv"):
            # the manuscript_section column holds section numbers, not results
            import csv
            import io
            rd = list(csv.DictReader(io.StringIO(text)))
            text = "\n".join([""] + [" | ".join(v for k, v in r.items() if k != "manuscript_section") for r in rd])
        rows = []
        for ln_no, line in enumerate(text.splitlines(), 1):
            if "sha256" in line.lower() or "SHA-256" in line:
                continue
            if line.lstrip().startswith("#"):
                continue  # headings carry section numbers, not results
            for m in NUM.finditer(line):
                tok = m.group(0)
                before = line[max(0, m.start() - 10):m.start()].lower()
                if before.endswith(("section ", "sections ", "arxiv:", "abs/", "sections 1 to ", " to ")) and "." in tok and "e" not in tok and float(tok) > 1:
                    rows.append({"line": ln_no, "number": tok, "status": "reference"})
                    continue
                if tok.lstrip("-") in ALLOWED:
                    status = "definition"
                else:
                    found = [f for f, vals in by_file.items() if matches(tok, vals)]
                    if found:
                        rows.append({"line": ln_no, "number": tok, "status": "matched", "sources": found})
                        continue
                    status = "UNMATCHED"
                    bad += 1
                rows.append({"line": ln_no, "number": tok, "status": status})
        report["targets"][rel] = {
            "numbers": len(rows),
            "matched": sum(r["status"] == "matched" for r in rows),
            "definitions": sum(r["status"] == "definition" for r in rows),
            "references": sum(r["status"] == "reference" for r in rows),
            "unmatched": [r for r in rows if r["status"] == "UNMATCHED"],
            "rows": rows,
        }
    report["total_unmatched"] = bad
    out = ROOT / "research" / "publication" / "number_audit.json"
    out.write_text(json.dumps(report, indent=1) + "\n")
    for rel, r in report["targets"].items():
        print(f"{rel}: {r['numbers']} numbers, {r['matched']} matched, {r['definitions']} definitions, "
              f"{len(r['unmatched'])} unmatched")
        for u in r["unmatched"]:
            print(f"   line {u['line']}: {u['number']}")
    print(f"AUDIT: {bad} unmatched")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
