import pytest

from renomeador_chandra.parsing import ParsedFields
from renomeador_chandra.rules import RuleError, build_filename


def test_rule_contrato_mercado():
    parsed = ParsedFields(
        data_assinatura="20231018",
        tipo_contrato="CCV",
        numero_contrato="232853",
        titulo_documento="CONTR",
        fazenda="CONTENDAS",
        contexto="mercado",
    )
    assert build_filename(parsed) == "20231018_CCV_232853_CONTR_CONTENDAS"


def test_rule_contrato_fundos():
    parsed = ParsedFields(
        data_assinatura="20240508",
        tipo_contrato="CPA",
        numero_contrato="232853",
        titulo_documento="TIP",
        fundo="MANULIFE",
        spe="TRIM",
        contexto="fundos",
    )
    assert build_filename(parsed) == "20240508_CPA_232853_TIP_MANULIFE_TRIM"


def test_rule_documento_ambiental():
    parsed = ParsedFields(
        ano_emissao="2024",
        nome_documento="CCIR",
        fazenda="CONTENDAS",
        parceiro="RADIALEUCALYPT",
        contexto="mercado",
    )
    assert build_filename(parsed) == "2024_CCIR_CONTENDAS_RADIALEUCALYPT"


def test_rule_pessoa_falta_campo():
    parsed = ParsedFields(proprietario="ODETTELEITE")
    with pytest.raises(RuleError):
        build_filename(parsed)
