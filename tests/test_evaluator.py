"""Tests for core.evaluator."""

from __future__ import annotations


from nexus_evolution.core.evaluator import PerformanceEvaluator, PerformanceMetric


class TestPerformanceMetric:
    """Test PerformanceMetric dataclass."""

    def test_to_dict(self) -> None:
        """to_dict should return all fields."""
        metric = PerformanceMetric(task_id="task-001", score=0.85)
        d = metric.to_dict()
        assert d["task_id"] == "task-001"
        assert d["score"] == 0.85


class TestPerformanceEvaluator:
    """Test performance evaluation and tracking."""

    def test_record_and_retrieve(self, tmp_path) -> None:
        """Recording metrics should persist and be retrievable."""
        evaluator = PerformanceEvaluator(history_file=str(tmp_path / "perf.json"))
        evaluator.record("task-001", 0.85, {"model": "gpt-4"})
        evaluator.record("task-002", 0.90, {"model": "gpt-4"})

        stats = evaluator.get_statistics()
        assert stats["mean"] == 0.875
        assert stats["total_tasks"] == 2

    def test_recent(self, tmp_path) -> None:
        """get_recent should return latest entries."""
        evaluator = PerformanceEvaluator(history_file=str(tmp_path / "perf.json"))
        for i in range(15):
            evaluator.record(f"task-{i:03d}", 0.5 + i * 0.01)

        recent = evaluator.get_recent(5)
        assert len(recent) == 5
        assert recent[-1].task_id == "task-014"

    def test_clear(self, tmp_path) -> None:
        """clear should remove all metrics."""
        evaluator = PerformanceEvaluator(history_file=str(tmp_path / "perf.json"))
        evaluator.record("task-001", 0.85)
        evaluator.clear()
        assert evaluator.get_statistics()["total_tasks"] == 0

    def test_trend_improving(self, tmp_path) -> None:
        """Trend should detect improvement."""
        evaluator = PerformanceEvaluator(history_file=str(tmp_path / "perf.json"))
        for i in range(10):
            evaluator.record(f"task-{i:03d}", 0.5 + i * 0.05)

        stats = evaluator.get_statistics()
        assert stats["trend"] == "improving"
