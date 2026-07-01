"""Evolution trigger — automatic pipeline activation based on conditions.

Monitors performance metrics and knowledge gaps to trigger
automatic evolution cycles when improvement is needed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from nexus_evolution.core.evaluator import PerformanceEvaluator
from nexus_evolution.core.gap_detector import KnowledgeGap, KnowledgeGapDetector


@dataclass
class TriggerCondition:
    """Condition that triggers an evolution cycle.

    Attributes:
        name: Condition name.
        threshold: Threshold value for triggering.
        current: Current value.
        triggered: Whether the condition is met.
    """

    name: str
    threshold: float
    current: float
    triggered: bool = False

    def evaluate(self) -> bool:
        """Check if condition is met."""
        self.triggered = self.current < self.threshold
        return self.triggered


class EvolutionTrigger:
    """Monitor conditions and trigger evolution cycles.

    Evaluates performance metrics and knowledge gaps against
    configurable thresholds to determine when the agent needs
    improvement.

    Usage:
        trigger = EvolutionTrigger(
            min_performance=0.7,
            max_gaps=3,
        )
        should_evolve = trigger.evaluate(evaluator, gap_detector)
    """

    def __init__(
        self,
        min_performance: float = 0.7,
        max_gaps: int = 3,
        min_improvement_rate: float = 0.05,
        cooldown_hours: int = 24,
    ) -> None:
        """Initialize evolution trigger.

        Args:
            min_performance: Minimum acceptable average performance.
            max_gaps: Maximum acceptable number of knowledge gaps.
            min_improvement_rate: Minimum improvement rate per cycle.
            cooldown_hours: Hours between evolution cycles.
        """
        self.min_performance = min_performance
        self.max_gaps = max_gaps
        self.min_improvement_rate = min_improvement_rate
        self.cooldown_hours = cooldown_hours

    def evaluate(
        self,
        evaluator: PerformanceEvaluator,
        gap_detector: KnowledgeGapDetector,
        performance_history: list[dict],
        interactions: list[str],
    ) -> dict:
        """Evaluate whether an evolution cycle should be triggered.

        Args:
            evaluator: Performance evaluator instance.
            gap_detector: Knowledge gap detector instance.
            performance_history: Historical performance data.
            interactions: Recent interaction logs.

        Returns:
            Dict with trigger decision, conditions, and gaps.
        """
        stats = evaluator.get_statistics()
        gaps = gap_detector.detect(performance_history, interactions)
        prioritized_gaps = gap_detector.prioritize(gaps)

        conditions = [
            TriggerCondition(
                name="performance_below_threshold",
                threshold=self.min_performance,
                current=stats.get("mean", 0),
            ),
            TriggerCondition(
                name="too_many_knowledge_gaps",
                threshold=self.max_gaps,
                current=len(prioritized_gaps),
            ),
            TriggerCondition(
                name="declining_trend",
                threshold=0,
                current=0 if stats.get("trend") != "declining" else 1,
            ),
        ]

        triggered_conditions = []
        for condition in conditions:
            condition.evaluate()
            if condition.triggered:
                triggered_conditions.append(condition.name)

        should_evolve = len(triggered_conditions) > 0

        return {
            "should_evolve": should_evolve,
            "triggered_conditions": triggered_conditions,
            "performance_stats": stats,
            "knowledge_gaps": [g.to_dict() for g in prioritized_gaps[:5]],
            "gap_count": len(prioritized_gaps),
        }
