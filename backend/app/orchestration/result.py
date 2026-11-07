from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.database.models import Run
from app.services.delivery import error_result, success_result


@dataclass
class ExperimentResult:
    run: Run
    deliveries: list[dict[str, Any]] = field(default_factory=list)

    def to_production_dict(self) -> dict[str, Any]:
        if self.run.status == "completed":
            return success_result(deliveries=self.deliveries)
        return error_result(self.run.error or "project execution failed")
