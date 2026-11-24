# SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0
"""CAL-001 (exploratory): calibrate h0 and sigma from the Duolingo traces (protocol 15.2).

Reads data/raw/settles.acl16.learning_traces.13m.csv.gz (run scripts/download_duolingo.py
first), checks its SHA-256 against data/raw/DS01.download.json, ingests it with the pure
function memory_research.duolingo.ingest, writes the processed subset to data/processed/
(git-ignored, row level) and the aggregate calibration to
results/exploratory/CAL-001/calibration.json (committed, no row-level data).

Usage: python scripts/calibrate_duolingo.py
"""

from __future__ import annotations

import gzip
import hashlib
import io
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from memory_research.duolingo import calibrate, ingest
from memory_research.environment import environment

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "settles.acl16.learning_traces.13m.csv.gz"
RECORD = ROOT / "data" / "raw" / "DS01.download.json"
PROCESSED = ROOT / "data" / "processed" / "DS01_first_review_subset.npz"
OUT = ROOT / "results" / "exploratory" / "CAL-001" / "calibration.json"


def main() -> int:
    rec = json.loads(RECORD.read_text())
    sha = hashlib.sha256()
    with RAW.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            sha.update(chunk)
    if sha.hexdigest() != rec["sha256"]:
        raise SystemExit("raw file SHA-256 does not match the download record")
    t0 = time.perf_counter()
    with gzip.open(RAW, "rb") as gz:
        processed, report = ingest(io.TextIOWrapper(gz, encoding="utf-8", newline=""))
    t_ingest = time.perf_counter() - t0
    PROCESSED.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(PROCESSED, lexeme=processed.lexeme, split_c=processed.split_c,
                        delta_days=processed.delta_days, trials=processed.trials,
                        successes=processed.successes, lexemes=np.array(processed.lexemes))
    t1 = time.perf_counter()
    result = calibrate(processed)
    t_fit = time.perf_counter() - t1
    doc = {
        "id": "CAL-001",
        "kind": "exploratory",
        "label": "EXPLORATORY calibration of simulation parameters from DS01; no schedule arm, no contrast.",
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "data": {"dataset_id": "DS01", "file": rec["file"], "sha256": rec["sha256"], "size_bytes": rec["size_bytes"],
                 "url": rec["url"], "licence": rec["licence"], "accessed_utc": rec["accessed_utc"]},
        "ingest_report": report.to_dict(),
        "calibration": result,
        "runtime_s": {"ingest": t_ingest, "fit_and_validation": t_fit},
        "environment": environment(ROOT),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"values": result["values"], "source": result["source"],
                      "flag_unstable": result["validation"]["flag_unstable"]}, indent=1))
    print(f"written: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
