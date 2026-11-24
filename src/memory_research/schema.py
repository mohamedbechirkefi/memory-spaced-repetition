# SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0
"""Versioned JSON schemas for matrix configurations, results and run manifests.

Every export is validated before it is written, and every import is
validated before it is used (fail closed).
"""

from __future__ import annotations

from typing import Any

import jsonschema

RESULT_SCHEMA_VERSION = "memory-result/1.0.0"
MANIFEST_SCHEMA_VERSION = "memory-run-manifest/1.0.0"
MATRIX_CONFIG_VERSION = "memory-matrix-config/1.0.0"

_SHA256 = {"type": "string", "pattern": "^[0-9a-f]{64}$"}
_PROB = {"type": "number", "minimum": 0, "maximum": 1}
_PROB_OR_NULL = {"type": ["number", "null"], "minimum": 0, "maximum": 1}
_KIND = {"enum": ["exploratory", "confirmatory"]}

SIM_CONFIG_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "n_items": {"type": "integer", "minimum": 1},
        "window_days": {"type": "integer", "minimum": 2},
        "retention_interval_days": {"type": "integer", "minimum": 0},
        "reviews_per_item": {"type": "integer", "minimum": 1},
        "h0_days": {"type": "number", "exclusiveMinimum": 0},
        "alpha": {"type": "number", "exclusiveMinimum": 0, "exclusiveMaximum": 1},
        "beta": {"type": "number", "minimum": 0},
        "omega_per_day": {"type": "number", "exclusiveMinimum": 0},
        "true_model": {"enum": ["exponential", "power"]},
        "item_distribution": {"enum": ["homogeneous", "lognormal", "bimodal"]},
        "lognormal_sigma": {"type": "number", "exclusiveMinimum": 0},
        "bimodal_factor": {"type": "number", "exclusiveMinimum": 0},
    },
}

_ARM = {"enum": ["uniform", "expanding", "massed", "leitner", "greedy", "greedy-exp", "greedy-power"]}

MATRIX_CONFIG_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "required": ["config_schema", "experiment_id", "kind", "description", "base", "arms", "seeds"],
    "additionalProperties": False,
    "properties": {
        "config_schema": {"const": MATRIX_CONFIG_VERSION},
        "experiment_id": {"type": "string", "pattern": "^(EXP|SMOKE|PROBE)-[0-9]{3}[A-Za-z0-9-]*$"},
        "kind": _KIND,
        "description": {"type": "string", "minLength": 1},
        "protocol_path": {"type": "string"},
        "base": SIM_CONFIG_SCHEMA,
        "factors": {
            "type": "object",
            "additionalProperties": {"type": "array", "minItems": 1},
            "propertyNames": {"enum": list(SIM_CONFIG_SCHEMA["properties"])},
        },
        "arms": {"type": "array", "items": _ARM, "minItems": 1, "uniqueItems": True},
        "baseline": _ARM,
        "seeds": {
            "oneOf": [
                {"type": "array", "items": {"type": "integer", "minimum": 0}, "minItems": 1, "uniqueItems": True},
                {
                    "type": "object",
                    "required": ["start", "count"],
                    "additionalProperties": False,
                    "properties": {
                        "start": {"type": "integer", "minimum": 0},
                        "count": {"type": "integer", "minimum": 1},
                        # Disjoint seed block per level of one factor (amendment A5, EXP-003 RI cells):
                        # cell seeds = start + step * (index of the level in the factor list) + 0..count-1.
                        "block_by": {
                            "type": "object",
                            "required": ["factor", "step"],
                            "additionalProperties": False,
                            "properties": {"factor": {"type": "string"}, "step": {"type": "integer", "minimum": 1}},
                        },
                    },
                },
            ]
        },
        "status_note": {"type": "string"},
    },
}

_METRICS = {
    "type": "object",
    "required": [
        "recall_mean", "observed_recall", "mastery_share", "recall_min", "recall_p10", "recall_mean_at_ri",
        "calibration_mae", "peak_daily_load", "sessions_used", "review_events",
    ],
    "properties": {
        "recall_mean": _PROB,
        "observed_recall": _PROB,
        "mastery_share": _PROB,
        "recall_min": _PROB,
        "recall_p10": _PROB,
        "recall_mean_at_ri": {"type": "object", "additionalProperties": _PROB},
        "calibration_mae": _PROB_OR_NULL,
        "peak_daily_load": {"type": "integer", "minimum": 0},
        "sessions_used": {"type": "integer", "minimum": 0},
        "review_events": {"type": "integer", "minimum": 0},
        "review_success_rate": _PROB_OR_NULL,
        "min_reviews_per_item": {"type": "integer", "minimum": 0},
        "max_reviews_per_item": {"type": "integer", "minimum": 0},
        "items_never_reviewed": {"type": "integer", "minimum": 0},
    },
}

_ENVIRONMENT = {
    "type": "object",
    "required": ["git_revision", "git_dirty", "python", "packages", "os", "cpu", "package_version"],
    "properties": {
        "git_revision": {"type": ["string", "null"]},
        "git_dirty": {"type": ["boolean", "null"]},
        "python": {"type": "string"},
        "packages": {"type": "object", "additionalProperties": {"type": ["string", "null"]}},
        "os": {"type": "string"},
        "cpu": {"type": "string"},
        "package_version": {"type": "string"},
    },
}

RESULT_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "required": [
        "schema_version", "experiment_id", "kind", "label", "created_utc", "matrix_config",
        "matrix_config_hash", "protocol", "environment", "cells", "runs", "summary",
    ],
    "properties": {
        "schema_version": {"const": RESULT_SCHEMA_VERSION},
        "experiment_id": {"type": "string"},
        "kind": _KIND,
        "label": {"type": "string", "minLength": 1},
        "created_utc": {"type": "string"},
        "matrix_config": MATRIX_CONFIG_SCHEMA,
        "matrix_config_hash": _SHA256,
        "protocol": {
            "type": "object",
            "required": ["path", "sha256", "frozen"],
            "properties": {"path": {"type": ["string", "null"]}, "sha256": {"type": ["string", "null"]}, "frozen": {"type": "boolean"}},
        },
        "environment": _ENVIRONMENT,
        "cells": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "required": ["cell_id", "factors", "config", "config_hash"],
                "properties": {
                    "cell_id": {"type": "string"},
                    "factors": {"type": "object"},
                    "config": SIM_CONFIG_SCHEMA,
                    "config_hash": _SHA256,
                },
            },
        },
        "runs": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["run_id", "cell_id", "arm", "seed", "status", "reasons", "metrics", "runtime_s", "peak_rss_bytes"],
                "properties": {
                    "run_id": {"type": "string"},
                    "cell_id": {"type": "string"},
                    "arm": _ARM,
                    "seed": {"type": "integer", "minimum": 0},
                    "status": {"enum": ["ok", "excluded", "failed"]},
                    "reasons": {"type": "array", "items": {"type": "string"}},
                    "metrics": {"oneOf": [_METRICS, {"type": "null"}]},
                    "runtime_s": {"type": "number", "minimum": 0},
                    "peak_rss_bytes": {"type": ["integer", "null"], "minimum": 0},
                },
                "allOf": [
                    {"if": {"properties": {"status": {"const": "ok"}}}, "then": {"properties": {"metrics": _METRICS, "reasons": {"maxItems": 0}}}},
                    {"if": {"properties": {"status": {"enum": ["excluded", "failed"]}}}, "then": {"properties": {"reasons": {"minItems": 1}}}},
                ],
            },
        },
        "summary": {
            "type": "object",
            "required": ["n_runs", "n_ok", "n_excluded", "n_failed", "wall_clock_s"],
            "properties": {
                "n_runs": {"type": "integer", "minimum": 0},
                "n_ok": {"type": "integer", "minimum": 0},
                "n_excluded": {"type": "integer", "minimum": 0},
                "n_failed": {"type": "integer", "minimum": 0},
                "wall_clock_s": {"type": "number", "minimum": 0},
            },
        },
    },
}

MANIFEST_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "required": ["schema_version", "experiment_id", "kind", "matrix_config_hash", "result_path", "result_sha256",
                 "environment", "runs", "wall_clock_s", "peak_rss_bytes"],
    "properties": {
        "schema_version": {"const": MANIFEST_SCHEMA_VERSION},
        "experiment_id": {"type": "string"},
        "kind": _KIND,
        "matrix_config_hash": _SHA256,
        "result_path": {"type": "string"},
        "result_sha256": _SHA256,
        "environment": _ENVIRONMENT,
        "runs": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["run_id", "seed", "arm", "config_hash", "status", "runtime_s", "peak_rss_bytes"],
                "properties": {
                    "run_id": {"type": "string"},
                    "seed": {"type": "integer"},
                    "arm": _ARM,
                    "config_hash": _SHA256,
                    "status": {"enum": ["ok", "excluded", "failed"]},
                    "runtime_s": {"type": "number", "minimum": 0},
                    "peak_rss_bytes": {"type": ["integer", "null"]},
                },
            },
        },
        "wall_clock_s": {"type": "number", "minimum": 0},
        "peak_rss_bytes": {"type": ["integer", "null"]},
    },
}


class SchemaError(ValueError):
    """Raised when a document fails schema validation."""


def _validate(doc: Any, schema: dict[str, Any], what: str) -> None:
    validator = jsonschema.Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(doc), key=lambda e: list(e.absolute_path))
    if errors:
        first = errors[0]
        path = "/".join(str(p) for p in first.absolute_path) or "<root>"
        raise SchemaError(f"{what} invalid at {path}: {first.message} ({len(errors)} error(s))")


def validate_matrix_config(doc: Any) -> None:
    _validate(doc, MATRIX_CONFIG_SCHEMA, "matrix configuration")


def validate_result(doc: Any) -> None:
    _validate(doc, RESULT_SCHEMA, "result document")
    s = doc["summary"]
    counts = {k: sum(1 for r in doc["runs"] if r["status"] == k) for k in ("ok", "excluded", "failed")}
    if s["n_runs"] != len(doc["runs"]) or any(s[f"n_{k}"] != v for k, v in counts.items()):
        raise SchemaError("result document invalid: summary counts do not match the run list")
    cell_ids = {c["cell_id"] for c in doc["cells"]}
    if any(r["cell_id"] not in cell_ids for r in doc["runs"]):
        raise SchemaError("result document invalid: a run refers to an unknown cell")
    if len({r["run_id"] for r in doc["runs"]}) != len(doc["runs"]):
        raise SchemaError("result document invalid: duplicate run_id")


def validate_manifest(doc: Any) -> None:
    _validate(doc, MANIFEST_SCHEMA, "run manifest")
