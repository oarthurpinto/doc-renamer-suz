"""Funções utilitárias do projeto."""

from __future__ import annotations

import logging
import re
import unicodedata
from pathlib import Path
from typing import Iterable, Iterator, Sequence

logger = logging.getLogger(__name__)

NORMALIZE_WHITESPACE_RE = re.compile(r"\s+")


def normalize_text(value: str) -> str:
    """Remove acentos e normaliza espaços."""

    normalized = unicodedata.normalize("NFKD", value)
    normalized = "".join(char for char in normalized if not unicodedata.combining(char))
    normalized = NORMALIZE_WHITESPACE_RE.sub(" ", normalized.strip())
    logger.debug("Texto normalizado: %s -> %s", value, normalized)
    return normalized


def slugify_safe(value: str) -> str:
    """Cria uma slug mantendo maiúsculas e substituindo apenas caracteres inválidos."""

    value = normalize_text(value)
    allowed = []
    for char in value:
        if char.isalnum():
            allowed.append(char.upper())
    slug = "".join(allowed)
    logger.debug("Slugify safe: %s -> %s", value, slug)
    return slug


def iter_files(paths: Sequence[Path], extensions: Iterable[str]) -> Iterator[Path]:
    """Itera sobre arquivos com extensões desejadas."""

    extensions_norm = {ext.lower() for ext in extensions}
    for path in paths:
        if path.is_dir():
            yield from iter_files(sorted(path.iterdir()), extensions_norm)
        elif path.suffix.lower().lstrip(".") in extensions_norm:
            logger.debug("Arquivo elegível: %s", path)
            yield path
        else:
            logger.debug("Arquivo ignorado: %s", path)


__all__ = ["normalize_text", "slugify_safe", "iter_files"]
