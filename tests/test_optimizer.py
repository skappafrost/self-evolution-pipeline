"""Tests for core.optimizer."""

from __future__ import annotations


from nexus_evolution.core.optimizer import OptimizationResult, PromptOptimizer


class TestOptimizationResult:
    """Test OptimizationResult dataclass."""

    def test_to_dict(self) -> None:
        """to_dict should return all fields."""
        result = OptimizationResult(
            iterations=5,
            best_score=0.85,
            best_prompt="Be precise.",
            improvement=0.15,
        )
        d = result.to_dict()
        assert d["iterations"] == 5
        assert d["best_score"] == 0.85
        assert d["improvement"] == 0.15

    def test_default_values(self) -> None:
        """Default values should be zero/empty."""
        result = OptimizationResult()
        assert result.iterations == 0
        assert result.best_score == 0.0
        assert result.best_prompt == ""
        assert result.history == []


class TestPromptOptimizer:
    """Test PromptOptimizer configuration."""

    def test_initialization(self) -> None:
        """Optimizer should initialize with correct defaults."""
        optimizer = PromptOptimizer(model="gpt-4o-mini")
        assert optimizer.model == "gpt-4o-mini"
        assert optimizer.lm_provider == "openai"

    def test_custom_provider(self) -> None:
        """Custom provider should be stored."""
        optimizer = PromptOptimizer(model="claude-3-opus", lm_provider="anthropic")
        assert optimizer.lm_provider == "anthropic"
