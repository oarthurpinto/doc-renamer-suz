"""Geração de relatórios em CSV."""

from __future__ import annotations

import csv
import logging
from pathlib import Path
from typing import Iterable

from .parsing import ParsedFields
from .renamer import RenameResult

logger = logging.getLogger(__name__)


def _row_from_result(result: RenameResult, parsed: ParsedFields | None) -> dict[str, object]:
    row = {
        "orig_path": str(result.original_path),
        "new_name": str(result.new_path.name),
        "status": result.status,
        "msg": result.message,
    }
    if parsed:
        row.update({
            "data_assinatura": parsed.data_assinatura,
            "numero_contrato": parsed.numero_contrato,
            "tipo_contrato": parsed.tipo_contrato,
            "titulo_documento": parsed.titulo_documento,
            "contexto": parsed.contexto,
            "fazenda": parsed.fazenda,
            "parceiro": parsed.parceiro,
            "fundo": parsed.fundo,
            "spe": parsed.spe,
            "ano_emissao": parsed.ano_emissao,
            "nome_documento": parsed.nome_documento,
            "proprietario": parsed.proprietario,
            "documento_pf_pj": parsed.documento_pf_pj,
        })
        for field, confidence in parsed.confidences.items():
            row[f"confidence_{field}"] = confidence
    return row


def generate_report(results: Iterable[RenameResult], parsed_map: dict[Path, ParsedFields], output_path: str | Path) -> Path:
    """Gera um CSV com os resultados da renomeação."""

    output = Path(output_path).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    rows = [_row_from_result(result, parsed_map.get(result.original_path)) for result in results]

    fieldnames = sorted({key for row in rows for key in row.keys()}) if rows else ["orig_path", "new_name", "status", "msg"]
    with output.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    logger.info("Relatório salvo em %s", output)
    return output


__all__ = ["generate_report"]
