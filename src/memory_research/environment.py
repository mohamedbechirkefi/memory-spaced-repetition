# SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0
"""Provenance captured at run time: code revision, versions, OS, CPU, memory."""

from __future__ import annotations

import platform
import resource
import subprocess
import sys
from importlib import metadata
from pathlib import Path
from typing import Any

from . import __version__

PACKAGES = ("numpy", "jsonschema", "matplotlib")


def repo_root() -> Path:
    """Repository root: the directory holding master_prompt.md above this package."""
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "master_prompt.md").is_file():
            return parent
    raise FileNotFoundError("repository root (master_prompt.md) not found above the package")


def _git(args: list[str], cwd: Path) -> str | None:
    try:
        out = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, timeout=10, check=True)
        return out.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None


def cpu_description() -> str:
    if sys.platform == "darwin":
        try:
            out = subprocess.run(["sysctl", "-n", "machdep.cpu.brand_string"], capture_output=True, text=True, timeout=5)
            if out.returncode == 0 and out.stdout.strip():
                return out.stdout.strip()
        except (OSError, subprocess.SubprocessError):
            pass
    return platform.processor() or platform.machine() or "unknown"


def peak_rss_bytes() -> int | None:
    """Process-level resident-set high-water mark (monotone over the process life)."""
    try:
        r = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    except (OSError, ValueError):
        return None
    return int(r if sys.platform == "darwin" else r * 1024)


def environment(root: Path | None = None) -> dict[str, Any]:
    root = root or repo_root()
    rev = _git(["rev-parse", "HEAD"], root)
    status = _git(["status", "--porcelain"], root)
    pkgs: dict[str, str | None] = {}
    for p in PACKAGES:
        try:
            pkgs[p] = metadata.version(p)
        except metadata.PackageNotFoundError:
            pkgs[p] = None
    return {
        "git_revision": rev,
        "git_dirty": None if status is None else bool(status),
        "python": platform.python_version(),
        "packages": pkgs,
        "os": f"{platform.system()} {platform.release()} ({platform.platform()})",
        "cpu": cpu_description(),
        "package_version": __version__,
    }
