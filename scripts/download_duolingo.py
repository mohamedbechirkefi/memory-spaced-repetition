# SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0
"""Download the Duolingo spaced-repetition traces (DS01) into data/raw/.

Deterministic: one fixed Dataverse file id, a fixed expected size and the MD5
published by Dataverse. The script verifies both, computes SHA-256, and writes
data/raw/DS01.download.json (URL, access time, size, MD5, SHA-256). The data
file itself is git-ignored (379,004,009 bytes, above the 20 MB commit limit of
the owner's rules, and row-level with pseudonymous learner identifiers).

Licence: CC BY-NC 4.0 (https://creativecommons.org/licenses/by-nc/4.0/),
per the Dataverse terms of use of doi:10.7910/DVN/N8XJME, read 2026-11-24.

Usage: python scripts/download_duolingo.py [--force]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
FILENAME = "settles.acl16.learning_traces.13m.csv.gz"
DATAVERSE_FILE_ID = 3091087
URL = f"https://dataverse.harvard.edu/api/access/datafile/{DATAVERSE_FILE_ID}"
LANDING = "https://doi.org/10.7910/DVN/N8XJME"
EXPECTED_SIZE = 379_004_009
EXPECTED_MD5 = "0a1cae5eb7ad4b0bd9c0de91d74fcced"
LICENCE = "CC BY-NC 4.0 (https://creativecommons.org/licenses/by-nc/4.0/)"


def digests(path: Path) -> tuple[str, str, int]:
    sha, md5, n = hashlib.sha256(), hashlib.md5(), 0
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            sha.update(chunk)
            md5.update(chunk)
            n += len(chunk)
    return sha.hexdigest(), md5.hexdigest(), n


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--force", action="store_true", help="download again even if a verified file exists")
    a = ap.parse_args(argv)
    RAW.mkdir(parents=True, exist_ok=True)
    dest = RAW / FILENAME
    if a.force or not dest.is_file():
        tmp = dest.with_suffix(dest.suffix + ".part")
        # curl, not urllib: urllib re-encodes the signed S3 redirect URL and gets HTTP 403.
        subprocess.run(["curl", "-fsSL", "--retry", "3", "-o", str(tmp), URL], check=True)
        tmp.replace(dest)
        accessed = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    else:
        accessed = None
    sha, md5, size = digests(dest)
    if size != EXPECTED_SIZE or md5 != EXPECTED_MD5:
        print(f"error: {dest} has size {size} and MD5 {md5}; expected {EXPECTED_SIZE} and {EXPECTED_MD5}", file=sys.stderr)
        return 1
    rec_path = RAW / "DS01.download.json"
    previous = json.loads(rec_path.read_text()) if rec_path.is_file() else {}
    record = {
        "dataset_id": "DS01",
        "file": f"data/raw/{FILENAME}",
        "url": URL,
        "landing_page": LANDING,
        "licence": LICENCE,
        "accessed_utc": accessed or previous.get("accessed_utc"),
        "size_bytes": size,
        "md5": md5,
        "sha256": sha,
    }
    rec_path.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
