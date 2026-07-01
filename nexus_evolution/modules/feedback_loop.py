"""Feedback loop — continuous improvement from task outcomes.

Implements a feedback collection and processing system that
captures task outcomes and feeds them back into the evolution
pipeline for iterative improvement.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class FeedbackEntry:
    """A single feedback entry from a task outcome.

    Attributes:
        task_id: Task identifier.
        outcome: Task outcome (success, partial, failure).
        score: Performance score (0.0-1.0).
        feedback: Textual feedback about the task.
        timestamp: When the feedback was recorded.
    """

    task_id: str
    outcome: str
    score: float
    feedback: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "task_id": self.task_id,
            "outcome": self.outcome,
            "score": self.score,
            "feedback": self.feedback,
            "timestamp": self.timestamp,
        }


class FeedbackLoop:
    """Collect and process feedback for continuous improvement.

    Captures task outcomes and generates improvement suggestions
    for the evolution pipeline.

    Usage:
        loop = FeedbackLoop()
        loop.record("task-001", "success", 0.95, "Completed successfully")
        loop.record("task-002", "failure", 0.2, "Missing knowledge about X")
        suggestions = loop.generate_suggestions()
    """

    def __init__(self) -> None:
        """Initialize feedback loop."""
        self._entries: list[FeedbackEntry] = []

    def record(
        self,
        task_id: str,
        outcome: str,
        score: float,
        feedback: str = "",
    ) -> None:
        """Record a feedback entry.

        Args:
            task_id: Task identifier.
            outcome: Task outcome (success, partial, failure).
            score: Performance score.
            feedback: Textual feedback.
        """
        entry = FeedbackEntry(
            task_id=task_id,
            outcome=outcome,
            score=score,
            feedback=feedback,
        )
        self._entries.append(entry)

    def get_failures(self) -> list[FeedbackEntry]:
        """Get all failure entries."""
        return [e for e in self._entries if e.outcome == "failure"]

    def get_successes(self) -> list[FeedbackEntry]:
        """Get all success entries."""
        return [e for e in self._entries if e.outcome == "success"]

    def get_average_score(self) -> float:
        """Calculate average score across all entries."""
        if not self._entries:
            return 0.0
        return sum(e.score for e in self._entries) / len(self._entries)

    def generate_suggestions(self) -> list[dict]:
        """Generate improvement suggestions from feedback.

        Analyzes failure patterns and low-score tasks to produce
        actionable improvement suggestions.

        Returns:
            List of suggestion dictionaries.
        """
        suggestions: list[dict] = []

        # Analyze failures
        failures = self.get_failures()
        if failures:
            common_topics: dict[str, int] = {}
            for entry in failures:
                words = entry.feedback.lower().split()
                for word in words:
                    if len(word) > 4:
                        common_topics[word] = common_topics.get(word, 0) + 1

            top_topics = sorted(common_topics.items(), key=lambda x: x[1], reverse=True)[:3]
            for topic, count in top_topics:
                suggestions.append({
                    "type": "knowledge_gap",
                    "topic": topic,
                    "evidence": f"Appeared in {count} failure feedback entries",
                    "priority": "high" if count > 2 else "medium",
                })

        # Analyze low scores
        low_scores = [e for e in self._entries if e.score < 0.5]
        if low_scores:
            suggestions.append({
                "type": "performance_improvement",
                "topic": "general_accuracy",
                "evidence": f"{len(low_scores)} tasks scored below 0.5",
                "priority": "high",
            })

        return suggestions

    def clear(self) -> None:
        """Clear all feedback entries."""
        self._entries.clear()
