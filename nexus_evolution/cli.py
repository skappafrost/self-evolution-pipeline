"""NEXUS Self-Evolution Pipeline — CLI entry point."""

from __future__ import annotations

import json
from pathlib import Path

import click

from nexus_evolution import __version__


@click.group()
@click.version_option(version=__version__, prog_name="nexus-evolve")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output.")
@click.pass_context
def main(ctx: click.Context, verbose: bool) -> None:
    """NEXUS Self-Evolution Pipeline — Autonomous agent improvement.

    Uses DSPy + GEPA for programmatic prompt optimization
    and self-directed skill refinement.
    """
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose


@main.command()
@click.option("--model", "-m", default="gpt-4o-mini", help="Language model to use.")
@click.option("--iterations", "-n", default=20, type=int, help="Max optimization iterations.")
@click.option("--output", "-o", default=None, help="Output file for optimization result.")
def optimize(model: str, iterations: int, output: str | None) -> None:
    """Run prompt optimization on a skill."""
    from nexus_evolution.core.optimizer import PromptOptimizer

    click.echo(f"🔍 Optimizing prompts with {model} for {iterations} iterations...")

    optimizer = PromptOptimizer(model=model)
    train_data = [
        ("What is the capital of France?", "Paris"),
        ("What is 2+2?", "4"),
        ("Who wrote 1984?", "George Orwell"),
    ]
    metric = lambda pred, ref: 1.0 if pred.strip().lower() == ref.lower() else 0.0
    result = optimizer.optimize(
        initial_prompt="Answer the following question accurately:",
        train_data=train_data,
        metric=metric,
        max_iterations=iterations,
    )

    click.echo(f"  Iterations: {result.iterations}")
    click.echo(f"  Best score: {result.best_score:.2%}")
    click.echo(f"  Improvement: {result.improvement:.2%}")

    if output:
        Path(output).write_text(json.dumps(result.to_dict(), indent=2))
        click.echo(f"  Saved to {output}")


@main.command()
@click.option("--min-performance", "-p", default=0.7, type=float, help="Minimum performance threshold.")
@click.option("--max-gaps", "-g", default=3, type=int, help="Maximum knowledge gaps.")
def check(min_performance: float, max_gaps: int) -> None:
    """Check if evolution should be triggered."""
    from nexus_evolution.core.evaluator import PerformanceEvaluator
    from nexus_evolution.core.gap_detector import KnowledgeGapDetector
    from nexus_evolution.modules.evolution_trigger import EvolutionTrigger

    evaluator = PerformanceEvaluator()
    gap_detector = KnowledgeGapDetector()

    stats = evaluator.get_statistics()
    click.echo(f"  Average performance: {stats['mean']:.2%}")
    click.echo(f"  Total tasks: {stats['total_tasks']}")
    click.echo(f"  Trend: {stats['trend']}")

    trigger = EvolutionTrigger(min_performance=min_performance, max_gaps=max_gaps)
    result = trigger.evaluate(evaluator, gap_detector, [], [])

    if result["should_evolve"]:
        click.echo(f"\n⚠️  Evolution triggered!")
        click.echo(f"  Conditions: {', '.join(result['triggered_conditions'])}")
    else:
        click.echo(f"\n✓ No evolution needed.")


@main.command("skills")
@click.option("--list", "-l", is_flag=True, help="List all skills.")
@click.option("--name", "-n", default=None, help="Skill name to inspect.")
def skills_cmd(list: bool, name: str | None) -> None:
    """Manage skill library."""
    from nexus_evolution.modules.skill_library import SkillLibrary

    library = SkillLibrary()

    if list:
        skills = library.list_skills()
        for skill in skills:
            latest = library.get_latest(skill)
            if latest:
                click.echo(f"  {skill} (v{latest.version}, score: {latest.score:.2%})")
    elif name:
        history = library.get_history(name)
        for v in history:
            click.echo(f"  v{v.version}: score={v.score:.2%}, {v.timestamp}")


if __name__ == "__main__":
    main()
