"""Integração com o modelo Chandra OCR."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Optional

try:  # pragma: no cover - import opcional
    from PIL import Image
except Exception:  # pragma: no cover - fallback quando Pillow indisponível
    Image = None  # type: ignore

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class OcrPage:
    """Representa o OCR de uma página."""

    number: int
    text: str
    raw_structured: Optional[dict] = None


@dataclass(slots=True)
class OcrResult:
    """Resultado consolidado do OCR."""

    source: Path
    text: str
    pages: List[OcrPage] = field(default_factory=list)
    tables: List[dict] = field(default_factory=list)
    images: List[Path] = field(default_factory=list)
    raw_structured: Optional[str] = None

    def to_json(self) -> str:
        """Serializa o resultado em JSON."""

        payload = {
            "source": str(self.source),
            "text": self.text,
            "pages": [
                {"number": page.number, "text": page.text, "raw_structured": page.raw_structured}
                for page in self.pages
            ],
            "tables": self.tables,
            "images": [str(path) for path in self.images],
            "raw_structured": self.raw_structured,
        }
        return json.dumps(payload, ensure_ascii=False, indent=2)


SUPPORTED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "tiff", "bmp", "gif", "txt"}


def _run_dummy_ocr(image) -> str:
    """Fallback extremamente simples quando OCR não está disponível."""

    try:
        import pytesseract  # type: ignore
    except Exception:  # pragma: no cover - pytesseract não é obrigatório
        logger.debug("pytesseract indisponível; OCR fictício retornará vazio")
        return ""
    return pytesseract.image_to_string(image, lang="por+eng")


def _extract_text_from_pdf(pdf_path: Path, out_dir: Optional[Path] = None) -> Iterable[str]:
    """Converte PDF em imagens e extrai texto."""

    try:
        from pdf2image import convert_from_path
    except Exception as exc:  # pragma: no cover - dependência opcional
        logger.warning("pdf2image indisponível: %s", exc)
        return []

    images = convert_from_path(str(pdf_path), dpi=300) if Image else []
    if out_dir:
        out_dir.mkdir(parents=True, exist_ok=True)

    for idx, image in enumerate(images, start=1):
        if out_dir:
            image_path = out_dir / f"{pdf_path.stem}_page{idx:03d}.png"
            image.save(image_path)
            logger.debug("Imagem da página salva em %s", image_path)
        text = _run_dummy_ocr(image)
        yield text


def run_ocr(input_path: str | Path, provider: str = "hf", out_dir: str | Path | None = None) -> OcrResult:
    """Executa OCR no arquivo informado.

    Atualmente tenta utilizar o pacote ``chandra-ocr`` se estiver disponível,
    caso contrário realiza um fallback simples baseado em ``pytesseract`` ou,
    para arquivos de texto, apenas lê o conteúdo diretamente.
    """

    path = Path(input_path).resolve()
    output_dir = Path(out_dir).resolve() if out_dir else None

    if path.suffix.lower().lstrip(".") not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Extensão não suportada: {path.suffix}")

    logger.info("Executando OCR em %s usando provider %s", path, provider)

    if path.suffix.lower() == ".txt":
        text = path.read_text(encoding="utf-8")
        page = OcrPage(number=1, text=text)
        return OcrResult(source=path, text=text, pages=[page], raw_structured=None)

    try:  # pragma: no cover - integração real não coberta por testes unitários
        from chandra_ocr import ChandraOCR  # type: ignore

        logger.debug("chandra-ocr disponível; executando modelo real")
        model = ChandraOCR(provider=provider)
        result = model.process_document(path)
        pages = [
            OcrPage(number=page["page"] if isinstance(page, dict) else idx + 1, text=page["text"])
            for idx, page in enumerate(result.get("pages", []))
        ]
        return OcrResult(
            source=path,
            text=result.get("text", ""),
            pages=pages,
            tables=result.get("tables", []),
            images=[Path(img) for img in result.get("images", [])],
            raw_structured=result.get("raw", ""),
        )
    except ModuleNotFoundError:
        logger.warning(
            "Pacote chandra-ocr não encontrado; utilizando implementação simplificada"
        )
    except Exception as exc:
        logger.exception("Falha ao executar chandra-ocr: %s", exc)

    if path.suffix.lower() == ".pdf":
        texts = list(_extract_text_from_pdf(path, output_dir))
    else:
        if Image is None:
            logger.warning("Pillow não disponível; retorno vazio para %s", path)
            texts = [""]
        else:
            image = Image.open(path)
            texts = [_run_dummy_ocr(image)]

    pages = [OcrPage(number=idx, text=txt) for idx, txt in enumerate(texts, start=1)]
    text = "\n".join(texts)
    return OcrResult(source=path, text=text, pages=pages)


__all__ = ["OcrResult", "OcrPage", "run_ocr"]
