from __future__ import annotations

import csv
import io
import json
from typing import Any, Iterable


def ideas_to_json(ideas: Iterable[Any]) -> str:
    rows = []
    for idea in ideas:
        if hasattr(idea, "__dict__") and not isinstance(idea, dict):
            rows.append(
                {
                    "id": getattr(idea, "id", None),
                    "name": getattr(idea, "name", None),
                    "one_liner": getattr(idea, "one_liner", None),
                    "score": getattr(idea, "score", None),
                    "score_band": getattr(idea, "score_band", None),
                    "status": getattr(idea, "status", None),
                    "mode": getattr(idea, "mode", None),
                }
            )
        else:
            rows.append(dict(idea))
    return json.dumps(rows, indent=2, default=str)


def ideas_to_csv(ideas: Iterable[Any]) -> str:
    buffer = io.StringIO()
    writer = csv.DictWriter(
        buffer,
        fieldnames=["id", "name", "one_liner", "score", "score_band", "status", "mode"],
        extrasaction="ignore",
    )
    writer.writeheader()
    for idea in ideas:
        if isinstance(idea, dict):
            writer.writerow(idea)
        else:
            writer.writerow(
                {
                    "id": getattr(idea, "id", ""),
                    "name": getattr(idea, "name", ""),
                    "one_liner": getattr(idea, "one_liner", ""),
                    "score": getattr(idea, "score", ""),
                    "score_band": getattr(idea, "score_band", ""),
                    "status": getattr(idea, "status", ""),
                    "mode": getattr(idea, "mode", ""),
                }
            )
    return buffer.getvalue()
