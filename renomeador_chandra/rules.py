"""Regras para montagem dos nomes de arquivo."""

from __future__ import annotations

import logging
from typing import Callable

from .parsing import ParsedFields
logger = logging.getLogger(__name__)


class RuleError(ValueError):
    """Erro levantado quando não é possível montar o nome."""


Validator = Callable[[ParsedFields], str]


def _require(value: str | None, field: str) -> str:
    if not value:
        raise RuleError(f"Campo obrigatório ausente: {field}")
    return value


def _build_contrato_mercado(parsed: ParsedFields) -> str:
    data = _require(parsed.data_assinatura, "data_assinatura")
    tipo = _require(parsed.tipo_contrato, "tipo_contrato")
    numero = _require(parsed.numero_contrato, "numero_contrato")
    titulo = _require(parsed.titulo_documento, "titulo_documento")
    fazenda = _require(parsed.fazenda, "fazenda")
    return "_".join([data, tipo, numero, titulo, fazenda])


def _build_contrato_fundos(parsed: ParsedFields) -> str:
    data = _require(parsed.data_assinatura, "data_assinatura")
    tipo = _require(parsed.tipo_contrato, "tipo_contrato")
    numero = _require(parsed.numero_contrato, "numero_contrato")
    titulo = _require(parsed.titulo_documento, "titulo_documento")
    fundo = _require(parsed.fundo, "fundo")
    spe = _require(parsed.spe, "spe")
    return "_".join([data, tipo, numero, titulo, fundo, spe])


def _build_documento_mercado(parsed: ParsedFields) -> str:
    ano = _require(parsed.ano_emissao, "ano_emissao")
    nome = _require(parsed.nome_documento, "nome_documento")
    fazenda = _require(parsed.fazenda, "fazenda")
    parceiro = _require(parsed.parceiro, "parceiro")
    return "_".join([ano, nome, fazenda, parceiro])


def _build_documento_fundos(parsed: ParsedFields) -> str:
    ano = _require(parsed.ano_emissao, "ano_emissao")
    nome = _require(parsed.nome_documento, "nome_documento")
    fundo = _require(parsed.fundo, "fundo")
    spe = _require(parsed.spe, "spe")
    return "_".join([ano, nome, fundo, spe])


def _build_pessoa(parsed: ParsedFields) -> str:
    proprietario = _require(parsed.proprietario, "proprietario")
    documento = _require(parsed.documento_pf_pj, "documento_pf_pj")
    return "_".join([proprietario, documento])


def build_filename(parsed: ParsedFields) -> str:
    """Resolve a regra adequada e monta o nome do arquivo."""

    logger.debug("Iniciando montagem de nome para campos: %s", parsed)

    if parsed.documento_pf_pj and parsed.proprietario:
        logger.debug("Aplicando regra de documento PF/PJ")
        return _build_pessoa(parsed)

    if parsed.nome_documento:
        contexto = parsed.contexto or "auto"
        if contexto == "fundos" or (parsed.fundo and parsed.spe):
            logger.debug("Aplicando regra de documento ambiental fundos")
            return _build_documento_fundos(parsed)
        logger.debug("Aplicando regra de documento ambiental mercado")
        return _build_documento_mercado(parsed)

    contexto = parsed.contexto or "auto"
    if contexto == "fundos" or (parsed.fundo and parsed.spe):
        logger.debug("Aplicando regra de contrato fundos")
        return _build_contrato_fundos(parsed)

    logger.debug("Aplicando regra de contrato mercado")
    return _build_contrato_mercado(parsed)


__all__ = ["build_filename", "RuleError"]
