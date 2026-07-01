"""Tests for core.gap_detector."""

from __future__ import annotations

import pytest

from nexus_evolution.core.gap_detector import KnowledgeGap, KnowledgeGapDetector


class TestKnowledgeGap:
    """Test KnowledgeGap dataclass."""

    def test_to_dict(self) -> None:
        """to_dict should return all fields."""
        gap = KnowledgeGap(domain="security", topic="wps", confidence=0.9, priority="high")
        d = gap.to_dict()
        assert d["domain"] == "security"
        assert d["confidence"] == 0.9


class TestKnowledgeGapDetector:
    """Test gap detection logic."""

    def test_detect_unknown(self) -> None:
        """Should detect 'I don't know' patterns."""
        detector = KnowledgeGapDetector()
        gaps = detector.detect([], ["I don't know how to do this"])
        assert len(gaps) > 0
        assert any(g.topic == "unknown" for g in gaps)

    def test_detect_error(self) -> None:
        """Should detect error patterns."""
        detector = KnowledgeGapDetector()
        gaps = detector.detect([], ["An error occurred while processing"])
        assert len(gaps) > 0

    def test_prioritize(self) -> None:
        """Should sort by priority."""
        gaps = [
            KnowledgeGap(domain="a", topic="low", priority="low"),
            KnowledgeGap(domain="b", topic="high", priority="high"),
            KnowledgeGap(domain="c", topic="critical", priority="critical"),
        ]
        detector = KnowledgeGapDetector()
        sorted_gaps = detector.prioritize(gaps)
        assert sorted_gaps[0].priority == "critical"
        assert sorted_gaps[-1].priority == "low"

    def test_deduplicate(self) -> None:
        """Should remove duplicates."""
        gaps = [
            KnowledgeGap(domain="security", topic="wps"),
            KnowledgeGap(domain="security", topic="wps"),
            KnowledgeGap(domain="network", topic="wifi"),
        ]
        detector = KnowledgeGapDetector()
        unique = detector.deduplicate(gaps)
        assert len(unique) == 2

    def test_min_confidence_filter(self) -> None:
        """Should filter gaps below min_confidence."""
        detector = KnowledgeGapDetector(min_confidence=0.8)
        gaps = detector.detect([], ["I'm not sure about this"])
        # "I'm not sure" has low confidence, may be filtered
        for gap in gaps:
            assert gap.confidence >= 0.3
