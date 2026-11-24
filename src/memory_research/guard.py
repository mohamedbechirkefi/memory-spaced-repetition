# SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0
"""Freeze guard: a confirmatory configuration runs only against a frozen protocol.

A protocol counts as frozen only if (1) the study protocol `research/protocol.md`
no longer carries the "NOT FROZEN" status marker, and (2) the experiment's row
in `research/experiment_registry.csv` records a SHA-256 protocol hash that
matches the current bytes of the experiment protocol file. Freezing itself is
the owner's decision (G-FREEZE); this module only checks it.
"""

from __future__ import annotations

import csv
import hashlib
import re
from dataclasses import dataclass
from pathlib import Path


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


def freeze_status(root: Path, experiment_id: str, protocol_path: str | None) -> FreezeStatus:
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
    return FreezeStatus(not reasons, protocol_path, sha, tuple(reasons))


def require_frozen(root: Path, experiment_id: str, protocol_path: str | None) -> FreezeStatus:
    status = freeze_status(root, experiment_id, protocol_path)
    if not status.frozen:
        raise ProtocolNotFrozenError(
            f"refusing confirmatory run of {experiment_id}: " + "; ".join(status.reasons)
        )
    return status
