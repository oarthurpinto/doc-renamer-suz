"""Submódulo simplificado ``rich.table``."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List


@dataclass
class Table:
    title: str | None = None
    rows: List[tuple[Any, ...]] = field(default_factory=list)

    def add_row(self, *columns: Any) -> None:
        self.rows.append(columns)

    def __str__(self) -> str:  # pragma: no cover - representação básica
        header = f"Tabela: {self.title}" if self.title else "Tabela"
        lines = [header]
        for row in self.rows:
            lines.append(" | ".join(str(col) for col in row))
        return "\n".join(lines)


__all__ = ["Table"]
