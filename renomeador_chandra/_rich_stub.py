"""Fallbacks minimalistas para o pacote Rich."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List


class Console:
    """Implementação simples com ``print``/``log`` para ambientes offline."""

    def print(self, *objects: Any) -> None:  # pragma: no cover - comportamento trivial
        print(*objects)

    def log(self, *objects: Any) -> None:  # pragma: no cover - comportamento trivial
        print(*objects)


@dataclass
class Table:
    """Tabela básica apenas para fins de testes."""

    title: str | None = None
    rows: List[tuple[Any, ...]] = field(default_factory=list)

    def add_row(self, *columns: Any) -> None:
        self.rows.append(columns)

    def __str__(self) -> str:  # pragma: no cover - representação simplificada
        header = f"Tabela: {self.title}" if self.title else "Tabela"
        lines = [header]
        for row in self.rows:
            lines.append(" | ".join(str(col) for col in row))
        return "\n".join(lines)


__all__ = ["Console", "Table"]
