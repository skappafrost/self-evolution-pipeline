"""Skill library — manage learned skills and their versions.

Tracks skill definitions, performance metrics, and version history
for the self-evolution pipeline.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class SkillVersion:
    """A versioned skill entry.

    Attributes:
        name: Skill name.
        version: Semantic version string.
        content: Skill definition content.
        score: Performance score at this version.
        timestamp: When this version was created.
    """

    name: str
    version: str
    content: str
    score: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "version": self.version,
            "content": self.content,
            "score": self.score,
            "timestamp": self.timestamp,
        }


class SkillLibrary:
    """Manage a versioned library of skills.

    Tracks skill definitions, performance metrics, and version
    history for the self-evolution pipeline.

    Usage:
        library = SkillLibrary(storage_dir="skills")
        library.add("wifi-scanner", "1.0.0", "Scan for WiFi APs...", score=0.85)
        versions = library.get_history("wifi-scanner")
    """

    def __init__(self, storage_dir: str = ".evolution/skills") -> None:
        """Initialize skill library.

        Args:
            storage_dir: Directory for skill storage.
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._skills: dict[str, list[SkillVersion]] = self._load()

    def _load(self) -> dict[str, list[SkillVersion]]:
        """Load skills from storage."""
        index_file = self.storage_dir / "index.json"
        if index_file.exists():
            try:
                data = json.loads(index_file.read_text())
                return {
                    name: [SkillVersion(**v) for v in versions]
                    for name, versions in data.items()
                }
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}

    def _save(self) -> None:
        """Save skills to storage."""
        index_file = self.storage_dir / "index.json"
        data = {
            name: [v.to_dict() for v in versions]
            for name, versions in self._skills.items()
        }
        index_file.write_text(json.dumps(data, indent=2))

    def add(self, name: str, version: str, content: str, score: float = 0.0) -> None:
        """Add a new skill version.

        Args:
            name: Skill name.
            version: Semantic version.
            content: Skill definition.
            score: Performance score.
        """
        entry = SkillVersion(name=name, version=version, content=content, score=score)
        if name not in self._skills:
            self._skills[name] = []
        self._skills[name].append(entry)
        self._save()

    def get_latest(self, name: str) -> Optional[SkillVersion]:
        """Get the latest version of a skill.

        Args:
            name: Skill name.

        Returns:
            Latest SkillVersion or None.
        """
        versions = self._skills.get(name, [])
        return versions[-1] if versions else None

    def get_history(self, name: str) -> list[SkillVersion]:
        """Get all versions of a skill.

        Args:
            name: Skill name.

        Returns:
            List of all versions.
        """
        return self._skills.get(name, [])

    def list_skills(self) -> list[str]:
        """List all skill names."""
        return sorted(self._skills.keys())

    def get_best(self, name: str) -> Optional[SkillVersion]:
        """Get the highest-scoring version of a skill.

        Args:
            name: Skill name.

        Returns:
            Best-scoring SkillVersion or None.
        """
        versions = self._skills.get(name, [])
        if not versions:
            return None
        return max(versions, key=lambda v: v.score)
