"""NEXUS Self-Evolution Pipeline — Autonomous skill improvement framework.

Uses DSPy + GEPA for programmatic prompt optimization, knowledge gap
detection, and self-directed agent refinement without human intervention.
"""

__version__ = "1.0.0"
__author__ = "NEXUS"

from nexus_evolution.core.optimizer import PromptOptimizer
from nexus_evolution.core.evaluator import PerformanceEvaluator
from nexus_evolution.core.gap_detector import KnowledgeGapDetector

__all__ = ["PromptOptimizer", "PerformanceEvaluator", "KnowledgeGapDetector"]
