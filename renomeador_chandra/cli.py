"""Interface de linha de comando baseada em Typer."""

from __future__ import annotations

import json
import logging
import shutil
from dataclasses import asdict
from pathlib import Path
from typing import Optional

try:  # pragma: no cover - fluxo exercitado apenas quando Typer não está disponível
    import typer
except ImportError:  # pragma: no cover - ambiente offline sem Typer
    from ._typer_stub import typer

try:  # pragma: no cover - fluxo alternativo apenas em ambientes sem Rich
    from rich.console import Console
    from rich.table import Table
except ImportError:  # pragma: no cover - ambiente offline sem Rich
    from ._rich_stub import Console, Table
import typer
from rich.console import Console
from rich.table import Table

from .config import AppConfig, ContextType
from .ocr_chandra import run_ocr
from .parsing import parse_document
from .renamer import RenameResult, rename_file
from .report import generate_report
from .rules import RuleError, build_filename
from .utils import iter_files

app = typer.Typer(add_completion=False)
console = Console()
logging.basicConfig(level=logging.INFO)

SUPPORTED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "tiff", "bmp", "gif", "txt"}


def _required_fields(parsed) -> list[str]:
    if parsed.documento_pf_pj and parsed.proprietario:
        return ["proprietario", "documento_pf_pj"]
    if parsed.nome_documento:
        if parsed.contexto == "fundos" or (parsed.fundo and parsed.spe):
            return ["ano_emissao", "nome_documento", "fundo", "spe"]
        return ["ano_emissao", "nome_documento", "fazenda", "parceiro"]
    if parsed.contexto == "fundos" or (parsed.fundo and parsed.spe):
        return [
            "data_assinatura",
            "tipo_contrato",
            "numero_contrato",
            "titulo_documento",
            "fundo",
            "spe",
        ]
    return ["data_assinatura", "tipo_contrato", "numero_contrato", "titulo_documento", "fazenda"]


def _confidence_ok(parsed, required: list[str], threshold: float) -> bool:
    for field in required:
        if parsed.get_confidence(field) < threshold:
            return False
    return True


def _save_pending(src: Path, pendentes_dir: Path, reason: str, parsed) -> Path:
    pendentes_dir.mkdir(parents=True, exist_ok=True)
    destino = pendentes_dir / src.name
    try:
        shutil.copy2(src, destino)
    except Exception as exc:  # pragma: no cover
        console.print(f"[red]Falha ao copiar para pendentes: {exc}")
    md_path = pendentes_dir / f"{src.stem}.md"
    with md_path.open("w", encoding="utf-8") as md_file:
        md_file.write(f"# Pendência para {src.name}\n\n")
        md_file.write(f"Motivo: {reason}\n\n")
        md_file.write("## Campos extraídos\n")
        md_file.write(json.dumps(asdict(parsed), ensure_ascii=False, indent=2))
    return destino


@app.command()
def process(
    path_in: Path = typer.Argument(..., exists=True, readable=True, help="Pasta de entrada"),
    out: Path = typer.Option(..., "--out", help="Pasta de saída"),
    context: ContextType = typer.Option("auto", "--context", help="Contexto forçado"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Não renomeia arquivos"),
    provider: str = typer.Option("hf", "--provider", help="Provider do OCR"),
    page_range: Optional[str] = typer.Option(None, "--page-range", help="Não utilizado no fallback"),
) -> None:
    """Processa arquivos de uma pasta, renomeando-os conforme regras."""

    del page_range  # não utilizado no momento

    config = AppConfig.from_env(path_in, out, context=context, dry_run=dry_run, provider=provider)
    console.log(f"Processando arquivos de {config.input_dir}")

    files = list(iter_files([config.input_dir], SUPPORTED_EXTENSIONS))
    if not files:
        console.print("[yellow]Nenhum arquivo elegível encontrado")
        raise typer.Exit(code=0)

    results: list[RenameResult] = []
    parsed_map = {}

    for file_path in files:
        console.print(f"[bold]Arquivo: {file_path.name}")
        try:
            ocr_result = run_ocr(file_path, provider=config.provider, out_dir=config.output_dir)
        except Exception as exc:  # pragma: no cover - erros de OCR inesperados
            console.print(f"[red]Falha no OCR: {exc}")
            results.append(RenameResult(file_path, file_path, status="ocr_error", message=str(exc)))
            continue

        parsed = parse_document(ocr_result.text, context_hint=config.context)
        parsed_map[file_path.resolve()] = parsed
        required = _required_fields(parsed)
        if not _confidence_ok(parsed, required, config.confidence_threshold):
            console.print("[yellow]Confiança insuficiente, enviando para pendentes")
            _save_pending(file_path, config.pendentes_dir, "Confiança insuficiente", parsed)
            results.append(
                RenameResult(
                    file_path,
                    config.pendentes_dir / file_path.name,
                    status="pending",
                    message="Confiança insuficiente",
                )
            )
            continue
        try:
            new_name = build_filename(parsed)
        except RuleError as exc:
            console.print(f"[red]Regra não satisfeita: {exc}")
            _save_pending(file_path, config.pendentes_dir, str(exc), parsed)
            results.append(
                RenameResult(
                    file_path,
                    config.pendentes_dir / file_path.name,
                    status="pending",
                    message=str(exc),
                )
            )
            continue

        rename_result = rename_file(file_path, new_name, config.output_dir, dry_run=config.dry_run)
        results.append(rename_result)

    report_path = generate_report(results, parsed_map, config.report_path)
    console.print(f"[green]Relatório gerado em {report_path}")


@app.command()
def audit(file: Path = typer.Argument(..., exists=True), out: Path = typer.Option(..., "--out")) -> None:
    """Gera arquivos auxiliares para auditoria de OCR."""

    out.mkdir(parents=True, exist_ok=True)
    ocr_result = run_ocr(file)
    parsed = parse_document(ocr_result.text)

    json_path = out / f"{file.stem}_ocr.json"
    md_path = out / f"{file.stem}_ocr.md"
    json_path.write_text(ocr_result.to_json(), encoding="utf-8")
    md_path.write_text(ocr_result.text, encoding="utf-8")

    table = Table(title=f"Campos extraídos de {file.name}")
    for field, value in parsed.__dict__.items():
        if field == "confidences" or field == "raw_text":
            continue
        table.add_row(field, str(value))
    console.print(table)


@app.command()
def validate(file: Path = typer.Argument(..., exists=True)) -> None:
    """Mostra o nome proposto para um arquivo sem renomear."""

    ocr_result = run_ocr(file)
    parsed = parse_document(ocr_result.text)
    try:
        new_name = build_filename(parsed)
    except RuleError as exc:
        console.print(f"[red]Não foi possível montar o nome: {exc}")
        raise typer.Exit(code=1)
    console.print(f"[green]Nome sugerido: {new_name}{file.suffix}")


if __name__ == "__main__":
    app()
