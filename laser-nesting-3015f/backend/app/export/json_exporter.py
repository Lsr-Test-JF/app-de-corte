"""JSON export helpers."""

from __future__ import annotations

import json
from pathlib import Path

from ..schemas import PlanResponse


def export_plan_to_json(plan: PlanResponse, file_path: str | Path) -> Path:
    """Persist plan output as UTF-8 pretty JSON."""
    target = Path(file_path)
    target.write_text(plan.model_dump_json(indent=2), encoding="utf-8")
    return target


def response_to_json_string(plan: PlanResponse) -> str:
    """Serialize plan response to json string."""
    return json.dumps(plan.model_dump(mode="json"), ensure_ascii=False, indent=2)
