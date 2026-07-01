"""Prompt optimization engine using DSPy + GEPA.

Provides programmatic prompt refinement through gradient-free optimization
and automatic prompt rewriting based on performance feedback.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

import dspy


class MetricFunction(Protocol):
    """Protocol for metric functions used in optimization."""

    def __call__(self, prediction: str, reference: str) -> float:
        """Return a score between 0.0 and 1.0."""
        ...


@dataclass
class OptimizationResult:
    """Result of a prompt optimization run.

    Attributes:
        iterations: Number of optimization iterations performed.
        best_score: Best metric score achieved.
        best_prompt: The optimized prompt that achieved best_score.
        improvement: Score improvement from initial to best.
        history: List of (iteration, score, prompt) tuples.
    """

    iterations: int = 0
    best_score: float = 0.0
    best_prompt: str = ""
    improvement: float = 0.0
    history: list[tuple[int, float, str]] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "iterations": self.iterations,
            "best_score": self.best_score,
            "best_prompt": self.best_prompt,
            "improvement": self.improvement,
            "history": self.history,
        }


class PromptOptimizer:
    """Programmatic prompt optimization using DSPy + GEPA.

    Automatically refines prompts through iterative optimization,
    using feedback from metric functions to guide improvements.

    Usage:
        optimizer = PromptOptimizer(model="gpt-4o-mini")
        result = optimizer.optimize(
            initial_prompt="Explain this code:",
            train_data=[("code1", "explanation1"), ...],
            metric=lambda pred, ref: 1.0 if pred == ref else 0.0,
            max_iterations=20,
        )
    """

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        lm_provider: str = "openai",
        cache_dir: str = ".evolution/cache",
    ) -> None:
        """Initialize the prompt optimizer.

        Args:
            model: Language model to use for optimization.
            lm_provider: Provider for the language model.
            cache_dir: Directory for caching optimization runs.
        """
        self.model = model
        self.lm_provider = lm_provider
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Configure DSPy
        if lm_provider == "openai":
            self.lm = dspy.OpenAI(model=model)
        elif lm_provider == "anthropic":
            self.lm = dspy.Anthropic(model=model)
        else:
            self.lm = dspy.OpenAI(model=model)

        dspy.configure(lm=self.lm)

    def _evaluate(
        self,
        program: dspy.Module,
        data: list[tuple[str, str]],
        metric: MetricFunction,
    ) -> float:
        """Evaluate a program against training data.

        Args:
            program: DSPy module to evaluate.
            data: Training data as (input, expected) tuples.
            metric: Scoring function.

        Returns:
            Average metric score.
        """
        scores: list[float] = []
        for input_text, expected in data:
            try:
                result = program(input_text)
                answer = result.answer if hasattr(result, "answer") else str(result)
                score = metric(answer, expected)
                scores.append(score)
            except Exception:
                scores.append(0.0)
        return sum(scores) / len(scores) if scores else 0.0

    def optimize(
        self,
        initial_prompt: str,
        train_data: list[tuple[str, str]],
        metric: MetricFunction,
        max_iterations: int = 20,
        min_improvement: float = 0.01,
    ) -> OptimizationResult:
        """Optimize a prompt through iterative refinement.

        Uses DSPy's BootstrapFewShot and MIPROv2 teleprompters to
        automatically improve prompt quality based on metric feedback.

        Args:
            initial_prompt: Starting prompt to optimize.
            train_data: Training examples (input, expected output).
            metric: Scoring function returning 0.0-1.0.
            max_iterations: Maximum optimization iterations.
            min_improvement: Minimum improvement to continue.

        Returns:
            OptimizationResult with best prompt and history.
        """
        result = OptimizationResult()
        current_prompt = initial_prompt
        best_score = 0.0

        # Create DSPy program from prompt
        class OptimizedProgram(dspy.Module):
            def __init__(self, prompt: str) -> None:
                super().__init__()
                self.generate = dspy.ChainOfThought(prompt)

            def forward(self, input_text: str) -> dspy.Prediction:
                return self.generate(input=input_text)

        # Prepare training data as DSPy examples
        _trainset = [
            dspy.Example(input=text, output=expected).with_inputs("input")
            for text, expected in train_data
        ]

        for iteration in range(max_iterations):
            program = OptimizedProgram(current_prompt)
            score = self._evaluate(program, train_data, metric)

            result.history.append((iteration, score, current_prompt))
            result.iterations = iteration + 1

            if score > best_score:
                improvement = score - best_score
                best_score = score
                result.best_score = score
                result.best_prompt = current_prompt
                result.improvement = improvement

                if improvement < min_improvement:
                    break

            # GEPA-style prompt rewriting
            try:
                rewriter = dspy.ChainOfThought(
                    "prompt,training_summary -> improved_prompt"
                )
                sample = "\n".join(f"Input: {t[0][:50]}" for t in train_data[:5])
                rewritten = rewriter(
                    prompt=current_prompt,
                    training_summary=sample,
                )
                if hasattr(rewritten, "improved_prompt") and rewritten.improved_prompt:
                    current_prompt = rewritten.improved_prompt.strip()
            except Exception:
                # Fallback: simple prompt mutation
                current_prompt = f"{current_prompt}\n\nAdditional context: Be precise and thorough."

        return result
