# SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0
"""Freeze guard: a confirmatory configuration runs only against a frozen protocol.

A protocol counts as frozen only if (1) the study protocol `research/protocol.md`
no longer carries the "NOT FROZEN" status marker, and (2) the experiment's row
in `research/experiment_registry.csv` records a SHA-256 protocol hash that
matches the current bytes of the experiment protocol file. When the caller
passes the matrix configuration (every confirmatory run does), (3) the freeze
record `research/freeze.json` must list the experiment, the SHA-256 of the
study protocol must match the record, and the canonical-JSON hash of the
configuration must equal the recorded one, so an edited configuration is
refused. Freezing itself is the owner's decision (G-FREEZE); this module only
checks it.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

FREEZE_RECORD = Path("research") / "freeze.json"


class ProtocolNotFrozenError(RuntimeError):
    """Raised when a confirmatory run is requested against an unfrozen protocol."""


@dataclass(frozen=True)
class FreezeStatus:
    frozen: bool
    protocol_path: str | None
    sha256: str | None
    reasons: tuple[str, ...]


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def freeze_status(
    root: Path, experiment_id: str, protocol_path: str | None, matrix: dict[str, Any] | None = None
) -> FreezeStatus:
    reasons: list[str] = []
    study = root / "research" / "protocol.md"
    if not study.is_file():
        reasons.append("research/protocol.md is missing")
    elif "NOT FROZEN" in study.read_text(encoding="utf-8"):
        reasons.append("research/protocol.md is marked NOT FROZEN")
    sha = None
    if protocol_path is None:
        reasons.append("the configuration names no protocol_path")
    else:
        p = root / protocol_path
        if not p.is_file():
            reasons.append(f"protocol file {protocol_path} is missing")
        else:
            sha = file_sha256(p)
    registry = root / "research" / "experiment_registry.csv"
    recorded = None
    if registry.is_file():
        with registry.open(newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                if row.get("exp_id") == experiment_id:
                    recorded = (row.get("protocol_hash") or "").strip()
    if recorded is None:
        reasons.append(f"{experiment_id} is not in research/experiment_registry.csv")
    elif not re.fullmatch(r"[0-9a-f]{64}", recorded):
        reasons.append(f"registry protocol_hash for {experiment_id} is {recorded!r}, not a SHA-256")
    elif sha is not None and recorded != sha:
        reasons.append(f"registry protocol_hash for {experiment_id} does not match the protocol file")
    if matrix is not None:
        reasons.extend(_config_reasons(root, experiment_id, matrix))
    return FreezeStatus(not reasons, protocol_path, sha, tuple(reasons))


def _config_reasons(root: Path, experiment_id: str, matrix: dict[str, Any]) -> list[str]:
    from .config import config_hash  # local import: config imports models only

    rec_path = root / FREEZE_RECORD
    if not rec_path.is_file():
        return [f"freeze record {FREEZE_RECORD} is missing"]
    try:
        record = json.loads(rec_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"freeze record {FREEZE_RECORD} is not valid JSON: {exc}"]
    reasons = []
    study = root / "research" / "protocol.md"
    if study.is_file() and record.get("study_protocol", {}).get("sha256") != file_sha256(study):
        reasons.append("research/protocol.md does not match the SHA-256 in the freeze record")
    entry = record.get("experiments", {}).get(experiment_id)
    if entry is None:
        reasons.append(f"{experiment_id} is not listed in the freeze record")
    elif entry.get("config_canonical_sha256") != config_hash(matrix):
        reasons.append(f"the {experiment_id} configuration differs from the frozen configuration")
    return reasons


def require_frozen(
    root: Path, experiment_id: str, protocol_path: str | None, matrix: dict[str, Any] | None = None
) -> FreezeStatus:
    status = freeze_status(root, experiment_id, protocol_path, matrix)
    if not status.frozen:
        raise ProtocolNotFrozenError(
            f"refusing confirmatory run of {experiment_id}: " + "; ".join(status.reasons)
        )
    return status
