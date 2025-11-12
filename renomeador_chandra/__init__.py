"""Pacote para renomeação de documentos com OCR Chandra."""

from .config import AppConfig
from .ocr_chandra import OcrResult, run_ocr
from .parsing import ParsedFields, parse_document
from .renamer import RenameResult, rename_file
from .rules import build_filename
from .report import generate_report

__all__ = [
    "AppConfig",
    "OcrResult",
    "ParsedFields",
    "RenameResult",
    "build_filename",
    "generate_report",
    "parse_document",
    "rename_file",
    "run_ocr",
]
