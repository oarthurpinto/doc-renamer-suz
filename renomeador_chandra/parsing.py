"""Parsing e extração de campos a partir do OCR."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, Optional

import re

from .config import ContextType
from .utils import normalize_text, slugify_safe

logger = logging.getLogger(__name__)

DATE_PATTERN = re.compile(r"(\d{2})[\/\-.](\d{2})[\/\-.](\d{4})")
YEAR_PATTERN = re.compile(r"\b(20\d{2})\b")
CONTRACT_NUMBER_PATTERN = re.compile(r"\b(\d{5,8})(?:[\/-]\d+)?\b")
CONTRACT_TYPES = {"CCV", "CPA", "CPR", "CCO", "CCE", "CDC"}
DOCUMENT_TITLES = {
    "PROM",
    "CONTR",
    "ADT",
    "1ADT",
    "2ADT",
    "3ADT",
    "CMDT",
    "TIP",
    "NOT",
    "RAS",
    "FAS",
    "CANI",
    "TAQ",
    "TAPI",
}
ENVIRONMENTAL_DOCS = {
    "MAT",
    "CARF",
    "CARE",
    "CTF",
    "ITR",
    "CCIR",
    "IE",
    "CND",
    "ADA",
    "CNE",
    "SISLA",
    "ICR",
    "IPR",
    "DARF",
}
DOCUMENTO_PF_PJ = {"RG", "CPF", "CNPJ", "CNH", "CERTIDAO", "CERTCASAMENTO", "CERTNASC"}
KEYWORDS_FUNDOS = {"FUNDO", "FIP", "FIAGRO", "SPE", "COTISTA"}
KEYWORDS_MERCADO = {"PARCEIRO", "FAZENDA", "PROPRIEDADE"}


@dataclass(slots=True)
class ParsedFields:
    """Armazena campos extraídos do documento."""

    data_assinatura: Optional[str] = None
    numero_contrato: Optional[str] = None
    tipo_contrato: Optional[str] = None
    titulo_documento: Optional[str] = None
    contexto: Optional[str] = None
    fazenda: Optional[str] = None
    parceiro: Optional[str] = None
    fundo: Optional[str] = None
    spe: Optional[str] = None
    ano_emissao: Optional[str] = None
    nome_documento: Optional[str] = None
    proprietario: Optional[str] = None
    documento_pf_pj: Optional[str] = None
    confidences: Dict[str, float] = field(default_factory=dict)
    raw_text: str = ""

    def set_value(self, field: str, value: Optional[str], confidence: float) -> None:
        if value:
            setattr(self, field, value)
            self.confidences[field] = confidence
            logger.debug("Campo %s definido para %s (%.2f)", field, value, confidence)

    def get_confidence(self, field: str) -> float:
        return self.confidences.get(field, 0.0)


def _detect_context(text_upper: str) -> ContextType:
    if any(keyword in text_upper for keyword in KEYWORDS_FUNDOS):
        return "fundos"
    if any(keyword in text_upper for keyword in KEYWORDS_MERCADO):
        return "mercado"
    return "auto"


def _extract_date(text: str) -> tuple[Optional[str], float]:
    match = DATE_PATTERN.search(text)
    if match:
        day, month, year = match.groups()
        formatted = f"{year}{month}{day}"
        return formatted, 0.95
    match_year = YEAR_PATTERN.search(text)
    if match_year:
        return match_year.group(1), 0.7
    return None, 0.0


def _extract_contract_number(text: str) -> tuple[Optional[str], float]:
    match = CONTRACT_NUMBER_PATTERN.search(text)
    if match:
        number = re.sub(r"\D", "", match.group(0))
        return number, 0.9
    return None, 0.0


def _extract_contract_type(text_upper: str) -> tuple[Optional[str], float]:
    for contract_type in CONTRACT_TYPES:
        if re.search(rf"\b{contract_type}\b", text_upper):
            if contract_type == "CPA" and "CPR" in text_upper:
                return "CPA", 0.85
            return contract_type, 0.85
    return None, 0.0


def _extract_title(text_upper: str) -> tuple[Optional[str], float]:
    for title in sorted(DOCUMENT_TITLES, key=len, reverse=True):
        if re.search(rf"\b{title}\b", text_upper):
            return title, 0.8
    return None, 0.0


def _extract_environmental(text_upper: str) -> tuple[Optional[str], float]:
    for doc in ENVIRONMENTAL_DOCS:
        if re.search(rf"\b{doc}\b", text_upper):
            return doc, 0.85
    return None, 0.0


STOP_WORDS = {
    "PARCEIRO",
    "FAZENDA",
    "FUNDO",
    "SPE",
    "CONTRATO",
    "NUMERO",
    "TIPO",
    "TITULO",
    "DOCUMENTO",
    "E",
    "DE",
    "DA",
    "DO",
    "PARA",
}


def _extract_entity(text: str, keyword: str) -> Optional[str]:
    position = text.find(keyword)
    if position == -1:
        return None
    remainder = text[position + len(keyword) :]
    remainder = remainder.lstrip(" :")
    tokens = remainder.split()
    collected: list[str] = []
    for token in tokens:
        if token in STOP_WORDS:
            break
        collected.append(token)
        if len(collected) >= 3:
            break
    if not collected:
        return None
    value = " ".join(collected)
    return slugify_safe(value)


def _extract_person(text: str) -> tuple[Optional[str], Optional[str], float]:
    pattern = re.compile(r"(?:PROPRIETARIO|PARCEIRO|CPF\s+DE)[:\s]+([A-Z\s]{3,50})")
    match = pattern.search(text)
    if match:
        name = normalize_text(match.group(1)).replace(" ", "")
        doc_match = re.search(rf"({'|'.join(DOCUMENTO_PF_PJ)})", text)
        doc_name = doc_match.group(1) if doc_match else None
        return name, doc_name, 0.8
    return None, None, 0.0


def parse_document(text: str, *, context_hint: ContextType = "auto") -> ParsedFields:
    """Analisa o texto e extrai campos estruturados."""

    text_clean = normalize_text(text).upper()
    result = ParsedFields(raw_text=text)

    date_value, date_conf = _extract_date(text_clean)
    result.set_value("data_assinatura", date_value, date_conf)

    number_value, number_conf = _extract_contract_number(text_clean)
    result.set_value("numero_contrato", number_value, number_conf)

    contract_type, type_conf = _extract_contract_type(text_clean)
    if contract_type == "CPR":
        contract_type = "CPA"
    result.set_value("tipo_contrato", contract_type, type_conf)

    title_value, title_conf = _extract_title(text_clean)
    result.set_value("titulo_documento", title_value, title_conf)

    env_value, env_conf = _extract_environmental(text_clean)
    if env_value:
        result.set_value("nome_documento", env_value, env_conf)
        if not result.ano_emissao:
            year_value, year_conf = _extract_date(text_clean)
            if year_value and len(year_value) == 4:
                result.set_value("ano_emissao", year_value, year_conf)
            else:
                year_match = YEAR_PATTERN.search(text_clean)
                if year_match:
                    result.set_value("ano_emissao", year_match.group(1), 0.7)

    context_value = context_hint if context_hint != "auto" else _detect_context(text_clean)
    result.set_value("contexto", context_value, 0.6 if context_hint == "auto" else 1.0)

    if context_value in {"mercado", "auto"}:
        fazenda_value = _extract_entity(text_clean, "FAZENDA")
        parceiro_value = _extract_entity(text_clean, "PARCEIRO")
        if fazenda_value:
            result.set_value("fazenda", fazenda_value, 0.75)
        if parceiro_value:
            result.set_value("parceiro", parceiro_value, 0.75)

    if context_value in {"fundos", "auto"}:
        fundo_value = _extract_entity(text_clean, "FUNDO")
        spe_value = _extract_entity(text_clean, "SPE")
        if fundo_value:
            result.set_value("fundo", fundo_value, 0.8)
        if spe_value:
            result.set_value("spe", spe_value, 0.8)

    person_name, doc_name, person_conf = _extract_person(text_clean)
    if person_name:
        result.set_value("proprietario", person_name, person_conf)
    if doc_name:
        result.set_value("documento_pf_pj", doc_name, 0.7)

    if result.tipo_contrato == "CPA" and "CPR" in text_clean:
        result.confidences["tipo_contrato"] = max(result.get_confidence("tipo_contrato"), 0.9)

    return result


__all__ = ["ParsedFields", "parse_document"]
