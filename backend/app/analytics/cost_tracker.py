from __future__ import annotations

from dataclasses import dataclass, field


# Rough SharedRoute / open-weight proxy estimates (USD per 1K tokens)
TASK_RATES = {
    "FAST": 0.0002,
    "MEDIUM": 0.0008,
    "HEAVY": 0.0030,
}


def estimate_call_cost(*, task: str, prompt_tokens: int, completion_tokens: int) -> float:
    rate = TASK_RATES.get((task or "MEDIUM").upper(), TASK_RATES["MEDIUM"])
    total = max(0, int(prompt_tokens)) + max(0, int(completion_tokens))
    return round((total / 1000.0) * rate, 6)


@dataclass
class CostTracker:
    budget_usd: float = 5.0
    calls: list[dict] = field(default_factory=list)

    def record(self, *, task: str, prompt_tokens: int = 0, completion_tokens: int = 0, model: str = "") -> float:
        cost = estimate_call_cost(task=task, prompt_tokens=prompt_tokens, completion_tokens=completion_tokens)
        self.calls.append(
            {
                "task": task,
                "model": model,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "cost_usd": cost,
            }
        )
        return cost

    @property
    def total_usd(self) -> float:
        return round(sum(float(c.get("cost_usd") or 0) for c in self.calls), 6)

    @property
    def remaining_usd(self) -> float:
        return round(self.budget_usd - self.total_usd, 6)

    def within_budget(self) -> bool:
        return self.total_usd <= self.budget_usd

    def summary(self) -> dict:
        by_task: dict[str, float] = {}
        for call in self.calls:
            task = str(call.get("task") or "UNKNOWN")
            by_task[task] = round(by_task.get(task, 0.0) + float(call.get("cost_usd") or 0), 6)
        return {
            "calls": len(self.calls),
            "total_usd": self.total_usd,
            "budget_usd": self.budget_usd,
            "remaining_usd": self.remaining_usd,
            "by_task": by_task,
        }
