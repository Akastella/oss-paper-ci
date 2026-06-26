"""Normalizer for Reproducibility DSL v1.

Converts a ReproDSL to a canonical, stable representation with:
- All paths relative
- All lists sorted
- All defaults explicit
- Stable JSON serialization
"""

from __future__ import annotations

import json
from typing import Any

from .schema import ReproDSL


def normalize_dsl(dsl: ReproDSL) -> dict[str, Any]:
    """Normalize a DSL to a canonical dictionary representation.

    Ensures:
    - All keys are sorted
    - All lists are sorted
    - All defaults are explicit
    - Paths are relative (no leading ./)
    - Output is deterministic
    """
    # Use the schema's to_dict() which already handles sorting
    normalized = dsl.to_dict()

    # Clean up paths: remove leading ./
    _clean_paths(normalized)

    return normalized


def normalize_dsl_json(dsl: ReproDSL, indent: int = 2) -> str:
    """Normalize and serialize to JSON string."""
    normalized = normalize_dsl(dsl)
    return json.dumps(normalized, indent=indent, sort_keys=False) + "\n"


def _clean_paths(obj: Any) -> None:
    """Recursively clean paths in a dict (remove leading ./)."""
    if isinstance(obj, dict):
        for key, val in obj.items():
            if key == "path" and isinstance(val, str) and val.startswith("./"):
                obj[key] = val[2:]
            elif isinstance(val, (dict, list)):
                _clean_paths(val)
    elif isinstance(obj, list):
        for item in obj:
            _clean_paths(item)
