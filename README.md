# Self-Evolution Pipeline

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Beta-orange)
![DSPy](https://img.shields.io/badge/Engine-DSPy%2BGPEA-blue)

**Autonomous skill improvement pipeline** using DSPy + GEPA for programmatic prompt optimization, knowledge gap detection, and self-directed agent refinement without human intervention.

Built by [NEXUS](https://skappafrost.github.io/nexus-website/) — an autonomous cybersecurity intelligence system.

---

## ⚠️ Legal Disclaimer

This tool is designed for **authorized AI research and development**. Ensure compliance with your AI provider's terms of service when using automated optimization. By using this software, you agree that:

1. You will use this tool responsibly and in compliance with applicable AI usage policies.
2. You accept full responsibility for any costs incurred from automated LLM API calls.
3. The authors bear **no liability** for unintended API usage or costs.

---

## Features

| # | Module | Description |
|---|--------|-------------|
| 1 | **PromptOptimizer** | DSPy/GEPA-based prompt refinement with iterative scoring |
| 2 | **PerformanceEvaluator** | Task outcome tracking, statistics, and trend detection |
| 3 | **KnowledgeGapDetector** | Automatic gap identification from failure patterns |
| 4 | **SkillLibrary** | Versioned skill storage with performance tracking |
| 5 | **EvolutionTrigger** | Automatic evolution cycle activation based on conditions |
| 6 | **FeedbackLoop** | Continuous improvement from task outcomes |
| 7 | **MetricAggregator** | Multi-dimensional performance metrics |
| 8 | **PromptRewriter** | Automatic prompt mutation strategies |
| 9 | **TrainingDataBuilder** | Training set generation from interactions |
| 10 | **VersionManager** | Semantic version control for skills |
| 11 | **TrendAnalyzer** | Performance trend detection (improving/declining/stable) |
| 12 | **SuggestionEngine** | Actionable improvement recommendations |

---

## Installation

```bash
git clone https://github.com/skappafrost/self-evolution-pipeline.git
cd self-evolution-pipeline
pip install -e .

# With dev dependencies
pip install -e ".[dev]"
```

### Prerequisites

- **Python 3.11+**
- **OpenAI API key** (or other DSPy-supported provider)

```bash
export OPENAI_API_KEY=sk-...
# Or for custom endpoints:
export OPENAI_API_KEY=...
export OPENAI_BASE_URL=https://your-api-endpoint/v1
```

---

## Quick Start

```bash
# Check if evolution is needed
nexus-evolve check

# Run prompt optimization
nexus-evolve optimize --model gpt-4o-mini --iterations 20

# Manage skills
nexus-evolve skills --list
nexus-evolve skills --name wifi-scanner
```

---

## Architecture

```
nexus_evolution/
├── __init__.py          # Package metadata
├── __main__.py          # python -m nexus_evolution entry
├── cli.py               # Click CLI (optimize, check, skills)
├── core/
│   ├── optimizer.py     # PromptOptimizer — DSPy/GEPA prompt refinement
│   ├── evaluator.py     # PerformanceEvaluator — metrics and trends
│   └── gap_detector.py  # KnowledgeGapDetector — gap identification
├── modules/
│   ├── skill_library.py  # SkillLibrary — versioned skill storage
│   ├── evolution_trigger.py  # EvolutionTrigger — auto-activation
│   └── feedback_loop.py  # FeedbackLoop — continuous improvement
└── utils/
    ├── config.py         # EvolutionConfig — env-based settings
    └── logger.py         # Structured logging
```

---

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `NEXUS_EVOLVE_MODEL` | `gpt-4o-mini` | Language model for optimization |
| `NEXUS_EVOLVE_PROVIDER` | `openai` | LLM provider (openai, anthropic) |
| `NEXUS_EVOLVE_MAX_ITER` | `20` | Max optimization iterations |
| `NEXUS_EVOLVE_MIN_IMPROVEMENT` | `0.01` | Minimum improvement to continue |
| `NEXUS_EVOLVE_VERBOSE` | `false` | Verbose mode |

---

## Development

```bash
pip install -e ".[dev]"
pytest
ruff check nexus_evolution/ tests/
mypy nexus_evolution/ --ignore-missing-imports
```

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

⭐ **Star this repo** if you find it useful. For questions or collaboration, reach out via [GitHub](https://github.com/skappafrost).
