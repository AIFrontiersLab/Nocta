from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Callable

from app.evaluation.baselines import BASELINE_IDEAS
from app.scoring.obvious import is_obvious


@dataclass
class EvaluationCase:
    name: str
    passed: bool
    detail: str = ""


@dataclass
class EvaluationReport:
    suite: str
    passed: int = 0
    failed: int = 0
    cases: list[EvaluationCase] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.failed == 0

    def to_dict(self) -> dict:
        return {
            "suite": self.suite,
            "passed": self.passed,
            "failed": self.failed,
            "ok": self.ok,
            "cases": [asdict(c) for c in self.cases],
        }


def evaluate_filters(
    obvious_fn: Callable[[str], tuple[bool, str]] | None = None,
) -> EvaluationReport:
    checker = obvious_fn or (lambda text: is_obvious(text))
    report = EvaluationReport(suite="obvious_filter_baselines")
    for item in BASELINE_IDEAS:
        text = f"{item['name']} {item['one_liner']}"
        hit, reason = checker(text)
        expected = bool(item["should_reject_obvious"])
        ok = hit is expected
        case = EvaluationCase(
            name=str(item["name"]),
            passed=ok,
            detail=f"expected_reject={expected} got={hit} reason={reason}",
        )
        report.cases.append(case)
        if ok:
            report.passed += 1
        else:
            report.failed += 1
    return report
