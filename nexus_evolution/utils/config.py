"""Evolution pipeline configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class EvolutionConfig:
    """Global configuration for the Self-Evolution Pipeline.

    Manages model settings, optimization parameters, and
    environment-specific configuration.
    """

    model: str = "gpt-4o-mini"
    lm_provider: str = "openai"
    max_iterations: int = 20
    min_improvement: float = 0.01
    min_performance: float = 0.7
    max_gaps: int = 3
    cooldown_hours: int = 24
    cache_dir: Path = Path(".evolution/cache")
    skills_dir: Path = Path(".evolution/skills")
    log_level: str = "INFO"
    verbose: bool = False

    @classmethod
    def from_env(cls) -> EvolutionConfig:
        """Load configuration from environment variables."""
        return cls(
            model=os.getenv("NEXUS_EVOLVE_MODEL", "gpt-4o-mini"),
            lm_provider=os.getenv("NEXUS_EVOLVE_PROVIDER", "openai"),
            max_iterations=int(os.getenv("NEXUS_EVOLVE_MAX_ITER", "20")),
            min_improvement=float(os.getenv("NEXUS_EVOLVE_MIN_IMPROVEMENT", "0.01")),
            verbose=os.getenv("NEXUS_EVOLVE_VERBOSE", "").lower() in ("1", "true", "yes"),
        )

    def ensure_dirs(self) -> None:
        """Create necessary directories."""
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.skills_dir.mkdir(parents=True, exist_ok=True)
