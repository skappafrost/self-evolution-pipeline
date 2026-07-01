"""Knowledge gap detection engine.

Identifies areas where the agent lacks knowledge or performs poorly,
triggering automatic learning and optimization cycles.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class KnowledgeGap:
    """Identified knowledge gap.

    Attributes:
        domain: Knowledge domain (e.g., 'network-security').
        topic: Specific topic within the domain.
        confidence: Confidence score (0.0-1.0).
        evidence: Evidence supporting this gap identification.
        priority: Priority level (critical, high, medium, low).
    """

    domain: str
    topic: str
    confidence: float = 0.0
    evidence: list[str] = field(default_factory=list)
    priority: str = "medium"

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "domain": self.domain,
            "topic": self.topic,
            "confidence": self.confidence,
            "evidence": self.evidence,
            "priority": self.priority,
        }


class KnowledgeGapDetector:
    """Detect knowledge gaps from performance data and interactions.

    Analyzes agent performance to identify areas where additional
    training or optimization is needed.

    Usage:
        detector = KnowledgeGapDetector()
        gaps = detector.detect(
            performance_history=[...],
            interactions=[...],
        )
    """

    # Patterns indicating knowledge gaps
    GAP_PATTERNS: list[tuple[str, str, str]] = [
        (r"I don't know.*", "unknown", "medium"),
        (r"I'm not sure.*", "uncertain", "low"),
        (r"I cannot.*", "capability", "high"),
        (r"error|Error|ERROR", "error-handling", "high"),
        (r"incorrect|wrong|failed", "accuracy", "critical"),
        (r"timeout|timed out", "performance", "medium"),
        (r"permission denied|unauthorized", "access-control", "high"),
    ]

    def __init__(self, min_confidence: float = 0.3) -> None:
        """Initialize gap detector.

        Args:
            min_confidence: Minimum confidence to report a gap.
        """
        self.min_confidence = min_confidence

    def detect(
        self,
        performance_history: list[dict],
        interactions: list[str],
    ) -> list[KnowledgeGap]:
        """Detect knowledge gaps from performance and interaction data.

        Args:
            performance_history: List of performance metrics.
            interactions: List of interaction texts/responses.

        Returns:
            List of identified KnowledgeGap objects.
        """
        gaps: list[KnowledgeGap] = []

        # Analyze interaction text for gap patterns
        for text in interactions:
            for pattern, topic, priority in self.GAP_PATTERNS:
                if re.search(pattern, text, re.IGNORECASE):
                    confidence = 0.9 if priority == "critical" else 0.6 if priority == "high" else 0.4
                    gap = KnowledgeGap(
                        domain="general",
                        topic=topic,
                        confidence=confidence,
                        evidence=[text[:200]],
                        priority=priority,
                    )
                    if gap.confidence >= self.min_confidence:
                        gaps.append(gap)

        # Analyze performance history for low scores
        for metric in performance_history:
            if metric.get("score", 1.0) < 0.5:
                gap = KnowledgeGap(
                    domain=metric.get("domain", "unknown"),
                    topic="performance-low",
                    confidence=0.9,
                    evidence=[f"Score: {metric.get('score')}"],
                    priority="high",
                )
                gaps.append(gap)

        return gaps

    def prioritize(self, gaps: list[KnowledgeGap]) -> list[KnowledgeGap]:
        """Sort gaps by priority level.

        Args:
            gaps: List of knowledge gaps.

        Returns:
            Sorted list (critical first).
        """
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        return sorted(gaps, key=lambda g: priority_order.get(g.priority, 99))

    def deduplicate(self, gaps: list[KnowledgeGap]) -> list[KnowledgeGap]:
        """Remove duplicate gaps (same domain+topic).

        Args:
            gaps: List of knowledge gaps.

        Returns:
            Deduplicated list.
        """
        seen: set[str] = set()
        unique: list[KnowledgeGap] = []
        for gap in gaps:
            key = f"{gap.domain}:{gap.topic}"
            if key not in seen:
                seen.add(key)
                unique.append(gap)
        return unique
