"""Implementação simplificada de Typer para ambientes sem dependências externas."""

from __future__ import annotations

from typing import Any, Callable


class Exit(SystemExit):
    """Equivalente simplificado a ``typer.Exit``."""

    def __init__(self, code: int = 0) -> None:
        super().__init__(code)


def Argument(*args: Any, **_: Any) -> Any:  # pragma: no cover - comportamento trivial
    if args:
        return args[0]
    return None


def Option(*args: Any, **_: Any) -> Any:  # pragma: no cover - comportamento trivial
    if args:
        return args[0]
    return None


class Typer:
    """Versão mínima da classe :class:`typer.Typer`."""

    def __init__(self, add_completion: bool = False) -> None:  # noqa: ARG002 - compatibilidade
        self._commands: dict[str, Callable[..., Any]] = {}

    def command(self, *_, **__) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            name = func.__name__
            self._commands[name] = func
            return func

        return decorator

    def __call__(self, *args: Any, **kwargs: Any) -> None:  # pragma: no cover - execução direta não usada
        raise NotImplementedError(
            "Executar o CLI diretamente requer a instalação do pacote Typer real."
        )


__all__ = ["Typer", "Argument", "Option", "Exit"]
