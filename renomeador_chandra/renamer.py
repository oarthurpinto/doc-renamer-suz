"""Lógica de renomeação de arquivos."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class RenameResult:
    """Representa o resultado de uma tentativa de renomeação."""

    original_path: Path
    new_path: Path
    status: str
    message: str = ""


def _resolve_collision(target_path: Path) -> Path:
    if not target_path.exists():
        return target_path
    counter = 2
    base = target_path.stem
    suffix = target_path.suffix
    while True:
        candidate = target_path.with_name(f"{base}_v{counter}{suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


def rename_file(src_path: str | Path, new_name: str, out_dir: str | Path, *, dry_run: bool = False) -> RenameResult:
    """Renomeia o arquivo para ``new_name`` dentro de ``out_dir``.

    Se ``dry_run`` for verdadeiro, apenas simula a operação.
    """

    source = Path(src_path).resolve()
    out_directory = Path(out_dir).resolve()
    out_directory.mkdir(parents=True, exist_ok=True)

    final_name = f"{new_name}{source.suffix}"
    target_path = _resolve_collision(out_directory / final_name)

    if dry_run:
        logger.info("Dry run: %s seria renomeado para %s", source, target_path)
        return RenameResult(source, target_path, status="dry_run", message="Simulação")

    try:
        logger.info("Renomeando %s para %s", source, target_path)
        source.rename(target_path)
        return RenameResult(source, target_path, status="renamed")
    except Exception as exc:  # pragma: no cover - erros inesperados
        logger.exception("Falha ao renomear arquivo: %s", exc)
        return RenameResult(source, target_path, status="error", message=str(exc))


__all__ = ["RenameResult", "rename_file"]
