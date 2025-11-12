"""Configurações da aplicação."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Optional


ContextType = Literal["mercado", "fundos", "auto"]
ProviderType = Literal["hf", "remote"]


@dataclass(slots=True)
class AppConfig:
    """Configuração principal do utilitário."""

    input_dir: Path
    output_dir: Path
    pendentes_dir: Path
    report_path: Path
    confidence_threshold: float = 0.7
    provider: ProviderType = "hf"
    context: ContextType = "auto"
    aliases_path: Optional[Path] = None
    dry_run: bool = False

    known_fundos: set[str] = field(default_factory=set)
    known_spes: set[str] = field(default_factory=set)
    known_parceiros: set[str] = field(default_factory=set)
    known_fazendas: set[str] = field(default_factory=set)

    @classmethod
    def from_env(
        cls,
        input_dir: str | Path,
        output_dir: str | Path,
        *,
        pendentes_dir: str | Path | None = None,
        report_path: str | Path | None = None,
        confidence_threshold: float | None = None,
        provider: ProviderType | None = None,
        context: ContextType | None = None,
        dry_run: bool = False,
        aliases_path: str | Path | None = None,
    ) -> "AppConfig":
        """Cria uma configuração inferindo caminhos padrão."""

        input_path = Path(input_dir).resolve()
        output_path = Path(output_dir).resolve()
        pendentes_path = (
            Path(pendentes_dir).resolve()
            if pendentes_dir
            else output_path.joinpath("_pendentes")
        )
        report_final = (
            Path(report_path).resolve()
            if report_path
            else output_path.joinpath("renomeacoes.csv")
        )
        return cls(
            input_dir=input_path,
            output_dir=output_path,
            pendentes_dir=pendentes_path,
            report_path=report_final,
            confidence_threshold=confidence_threshold or 0.7,
            provider=provider or "hf",
            context=context or "auto",
            dry_run=dry_run,
            aliases_path=Path(aliases_path).resolve() if aliases_path else None,
        )


__all__ = ["AppConfig", "ContextType", "ProviderType"]
