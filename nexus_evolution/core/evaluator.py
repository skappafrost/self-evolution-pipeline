"""Performance evaluation engine.

Tracks and evaluates agent performance across tasks, providing
metrics and feedback for the evolution pipeline.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class PerformanceMetric:
    """Single performance measurement.

    Attributes:
        task_id: Unique task identifier.
        score: Performance score (0.0-1.0).
        timestamp: When the metric was recorded.
        metadata: Additional context about the task.
    """

    task_id: str
    score: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "task_id": self.task_id,
            "score": self.score,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }


class PerformanceEvaluator:
    """Evaluate agent performance and track improvements.

    Maintains a history of performance metrics and provides
    statistical analysis of improvement trends.

    Usage:
        evaluator = PerformanceEvaluator()
        evaluator.record("task-001", 0.85, {"model": "gpt-4"})
        stats = evaluator.get_statistics()
    """

    def __init__(self, history_file: Optional[str] = None) -> None:
        """Initialize evaluator.

        Args:
            history_file: Path to store performance history.
        """
        self.history_file = Path(history_file or ".evolution/performance.json")
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        self._metrics: list[PerformanceMetric] = self._load_history()

    def _load_history(self) -> list[PerformanceMetric]:
        """Load performance history from file."""
        if self.history_file.exists():
            try:
                data = json.loads(self.history_file.read_text())
                return [PerformanceMetric(**m) for m in data]
            except (json.JSONDecodeError, TypeError):
                return []
        return []

    def _save_history(self) -> None:
        """Save performance history to file."""
        data = [m.to_dict() for m in self._metrics]
        self.history_file.write_text(json.dumps(data, indent=2))

    def record(self, task_id: str, score: float, metadata: Optional[dict] = None) -> None:
        """Record a performance metric.

        Args:
            task_id: Task identifier.
            score: Performance score (0.0-1.0).
            metadata: Optional additional context.
        """
        metric = PerformanceMetric(task_id=task_id, score=score, metadata=metadata or {})
        self._metrics.append(metric)
        self._save_history()

    def get_statistics(self) -> dict:
        """Calculate performance statistics.

        Returns:
            Dict with mean, std, min, max, trend.
        """
        if not self._metrics:
            return {"mean": 0, "std": 0, "min": 0, "max": 0, "trend": "stable", "total_tasks": 0}

        scores = [m.score for m in self._metrics]
        mean = sum(scores) / len(scores)
        variance = sum((s - mean) ** 2 for s in scores) / len(scores)
        std = variance**0.5

        # Calculate trend (last 5 vs previous 5)
        if len(scores) >= 10:
            recent = scores[-5:]
            previous = scores[-10:-5]
            recent_avg = sum(recent) / 5
            previous_avg = sum(previous) / 5
            if recent_avg > previous_avg + 0.05:
                trend = "improving"
            elif recent_avg < previous_avg - 0.05:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"

        return {
            "mean": round(mean, 4),
            "std": round(std, 4),
            "min": min(scores),
            "max": max(scores),
            "trend": trend,
            "total_tasks": len(self._metrics),
        }

    def get_recent(self, n: int = 10) -> list[PerformanceMetric]:
        """Get the n most recent metrics."""
        return self._metrics[-n:]

    def clear(self) -> None:
        """Clear all performance history."""
        self._metrics.clear()
        self._save_history()
