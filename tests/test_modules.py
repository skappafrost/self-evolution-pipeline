"""Tests for modules — skill library, evolution trigger, feedback loop."""

from __future__ import annotations

import pytest

from nexus_evolution.modules.skill_library import SkillLibrary, SkillVersion
from nexus_evolution.modules.evolution_trigger import EvolutionTrigger, TriggerCondition
from nexus_evolution.modules.feedback_loop import FeedbackLoop


class TestSkillLibrary:
    """Test skill library operations."""

    def test_add_and_retrieve(self, tmp_path) -> None:
        """Skills should be addable and retrievable."""
        library = SkillLibrary(storage_dir=str(tmp_path / "skills"))
        library.add("wifi-scan", "1.0.0", "Scan for APs", score=0.85)
        latest = library.get_latest("wifi-scan")
        assert latest is not None
        assert latest.version == "1.0.0"

    def test_history(self, tmp_path) -> None:
        """History should track all versions."""
        library = SkillLibrary(storage_dir=str(tmp_path / "skills"))
        library.add("wifi-scan", "1.0.0", "v1", score=0.8)
        library.add("wifi-scan", "1.1.0", "v2", score=0.85)
        library.add("wifi-scan", "1.2.0", "v3", score=0.9)
        history = library.get_history("wifi-scan")
        assert len(history) == 3

    def test_best(self, tmp_path) -> None:
        """get_best should return highest-scoring version."""
        library = SkillLibrary(storage_dir=str(tmp_path / "skills"))
        library.add("wifi-scan", "1.0.0", "v1", score=0.8)
        library.add("wifi-scan", "1.1.0", "v2", score=0.95)
        library.add("wifi-scan", "1.2.0", "v3", score=0.7)
        best = library.get_best("wifi-scan")
        assert best is not None
        assert best.version == "1.1.0"

    def test_list_skills(self, tmp_path) -> None:
        """list_skills should return sorted names."""
        library = SkillLibrary(storage_dir=str(tmp_path / "skills"))
        library.add("bravo", "1.0.0", "b", score=0.8)
        library.add("alpha", "1.0.0", "a", score=0.9)
        assert library.list_skills() == ["alpha", "bravo"]


class TestEvolutionTrigger:
    """Test evolution trigger logic."""

    def test_condition_evaluate(self) -> None:
        """TriggerCondition should evaluate correctly."""
        cond = TriggerCondition(name="test", threshold=0.7, current=0.5)
        assert cond.evaluate() is True
        assert cond.triggered is True

        cond2 = TriggerCondition(name="test", threshold=0.7, current=0.8)
        assert cond2.evaluate() is False

    def test_evaluate_triggered(self, tmp_path) -> None:
        """evaluate should detect low performance."""
        from nexus_evolution.core.evaluator import PerformanceEvaluator
        from nexus_evolution.core.gap_detector import KnowledgeGapDetector

        evaluator = PerformanceEvaluator(history_file=str(tmp_path / "perf.json"))
        evaluator.record("task-001", 0.5)
        gap_detector = KnowledgeGapDetector()

        trigger = EvolutionTrigger(min_performance=0.7)
        result = trigger.evaluate(evaluator, gap_detector, [], [])
        assert result["should_evolve"] is True


class TestFeedbackLoop:
    """Test feedback loop operations."""

    def test_record_and_average(self) -> None:
        """Recording feedback should calculate average."""
        loop = FeedbackLoop()
        loop.record("task-001", "success", 0.9)
        loop.record("task-002", "success", 0.8)
        loop.record("task-003", "failure", 0.2)
        assert loop.get_average_score() == pytest.approx(0.633, rel=0.01)

    def test_generate_suggestions(self) -> None:
        """Should generate suggestions from failures."""
        loop = FeedbackLoop()
        loop.record("task-001", "failure", 0.2, "I don't know the answer")
        loop.record("task-002", "failure", 0.3, "Error occurred")
        suggestions = loop.generate_suggestions()
        assert len(suggestions) > 0

    def test_get_failures(self) -> None:
        """Should return only failure entries."""
        loop = FeedbackLoop()
        loop.record("task-001", "success", 0.9)
        loop.record("task-002", "failure", 0.2)
        loop.record("task-003", "failure", 0.3)
        assert len(loop.get_failures()) == 2

    def test_clear(self) -> None:
        """clear should remove all entries."""
        loop = FeedbackLoop()
        loop.record("task-001", "success", 0.9)
        loop.clear()
        assert loop.get_average_score() == 0.0
