"""Submódulo simplificado ``rich.console``."""

from __future__ import annotations

from typing import Any


class Console:
    def print(self, *objects: Any) -> None:  # pragma: no cover - comportamento trivial
        print(*objects)

    def log(self, *objects: Any) -> None:  # pragma: no cover - comportamento trivial
        print(*objects)


__all__ = ["Console"]
