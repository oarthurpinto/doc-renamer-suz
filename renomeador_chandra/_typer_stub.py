"""Fallback simples para Typer quando dependência não está disponível."""
from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Callable


class Exit(SystemExit):
    """Equivalente simplificado a :class:`typer.Exit`."""

    def __init__(self, code: int = 0) -> None:
        super().__init__(code)


def Argument(*args: Any, **_: Any) -> Any:  # pragma: no cover - comportamento trivial
    return args[0] if args else None


def Option(*args: Any, **_: Any) -> Any:  # pragma: no cover - comportamento trivial
    return args[0] if args else None


class Typer:
    """Versão mínima da classe :class:`typer.Typer` para testes offline."""

    def __init__(self, add_completion: bool = False) -> None:  # noqa: ARG002 compatibilidade
        self._commands: dict[str, Callable[..., Any]] = {}

    def command(self, *_, **__) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            name = func.__name__
            self._commands[name] = func
            return func

        return decorator

    def __call__(self, *args: Any, **kwargs: Any) -> None:  # pragma: no cover - exec direta não suportada
        raise NotImplementedError(
            "Executar o CLI diretamente requer a instalação do pacote Typer real."
        )


typer = SimpleNamespace(Typer=Typer, Argument=Argument, Option=Option, Exit=Exit)

__all__ = ["typer", "Typer", "Argument", "Option", "Exit"]
