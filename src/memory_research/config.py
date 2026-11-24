# SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0
"""Simulation configuration with explicit units and validation (protocol 2.1 to 2.5)."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass, fields
from typing import Any, Mapping

from .models import MODELS, ModelError, check_update_params

DISTRIBUTIONS = ("homogeneous", "lognormal", "bimodal")


class ConfigError(ValueError):
    """Raised when a configuration is invalid."""


@dataclass(frozen=True)
class SimConfig:
    """One simulation cell. Units are in the field names."""

    n_items: int = 50
    window_days: int = 28  # D: sessions at days 0..D-1
    retention_interval_days: int = 7  # RI: test at D-1+RI
    reviews_per_item: int = 4  # k: budget B = k * N
    h0_days: float = 1.0
    alpha: float = 0.4
    beta: float = 0.6
    omega_per_day: float = 1.0
    true_model: str = "exponential"
    item_distribution: str = "lognormal"
    lognormal_sigma: float = 0.75
    bimodal_factor: float = 3.0

    def __post_init__(self) -> None:
        validate_config(self)

    @property
    def budget(self) -> int:
        """B, total review events (session 0 encoding excluded)."""
        return self.reviews_per_item * self.n_items

    @property
    def n_review_sessions(self) -> int:
        """Sessions 1..D-1."""
        return self.window_days - 1

    @property
    def test_time_days(self) -> int:
        return self.window_days - 1 + self.retention_interval_days

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "SimConfig":
        known = {f.name for f in fields(cls)}
        unknown = set(data) - known
        if unknown:
            raise ConfigError(f"unknown configuration keys: {sorted(unknown)}")
        return cls(**dict(data))


def _is_int(x: Any) -> bool:
    return isinstance(x, int) and not isinstance(x, bool)


def _is_pos_float(x: Any) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x) and x > 0


def validate_config(c: SimConfig) -> None:
    for name in ("n_items", "window_days", "retention_interval_days", "reviews_per_item"):
        if not _is_int(getattr(c, name)):
            raise ConfigError(f"{name} must be an integer, got {getattr(c, name)!r}")
    if c.n_items < 1:
        raise ConfigError("n_items must be >= 1")
    if c.window_days < 2:
        raise ConfigError("window_days must be >= 2 (at least one review session)")
    if c.retention_interval_days < 0:
        raise ConfigError("retention_interval_days must be >= 0")
    if c.reviews_per_item < 1:
        raise ConfigError("reviews_per_item must be >= 1")
    if c.reviews_per_item > c.window_days - 1:
        raise ConfigError(
            "reviews_per_item cannot exceed the number of review sessions (window_days - 1), "
            "since an item is reviewed at most once per session"
        )
    for name in ("h0_days", "omega_per_day", "lognormal_sigma", "bimodal_factor"):
        if not _is_pos_float(getattr(c, name)):
            raise ConfigError(f"{name} must be finite and > 0, got {getattr(c, name)!r}")
    try:
        check_update_params(c.alpha, c.beta)
    except ModelError as exc:
        raise ConfigError(str(exc)) from exc
    if c.true_model not in MODELS:
        raise ConfigError(f"true_model must be one of {MODELS}, got {c.true_model!r}")
    if c.item_distribution not in DISTRIBUTIONS:
        raise ConfigError(f"item_distribution must be one of {DISTRIBUTIONS}, got {c.item_distribution!r}")


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def config_hash(obj: Any) -> str:
    """SHA-256 of the canonical JSON form (sorted keys, no whitespace)."""
    if isinstance(obj, SimConfig):
        obj = obj.to_dict()
    return hashlib.sha256(canonical_json(obj).encode("ascii")).hexdigest()
