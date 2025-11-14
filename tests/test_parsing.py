from renomeador_chandra.parsing import parse_document


def test_parse_contrato_completo():
    texto = """
    Contrato celebrado em 18/10/2023 com número 232853.
    Tipo CCV título CONTR.
    Fazenda Contendas parceiro Radial Eucalypt.
    """
    parsed = parse_document(texto, context_hint="mercado")
    assert parsed.data_assinatura == "20231018"
    assert parsed.numero_contrato == "232853"
    assert parsed.tipo_contrato == "CCV"
    assert parsed.titulo_documento == "CONTR"
    assert parsed.fazenda == "CONTENDAS"
    assert parsed.parceiro == "RADIALEUCALYPT"


def test_parse_aditivo():
    texto = """
    23/10/2023 - Aditivo 1ADT do contrato 232853.
    CPA (CPR) parceria agrícola com Fazenda Contendas.
    """
    parsed = parse_document(texto, context_hint="mercado")
    assert parsed.data_assinatura == "20231023"
    assert parsed.titulo_documento == "1ADT"
    assert parsed.tipo_contrato == "CPA"


def test_parse_documento_ambiental():
    texto = """
    CCIR 2024 referente à Fazenda Contendas e parceiro Radial Eucalypt.
    """
    parsed = parse_document(texto, context_hint="mercado")
    assert parsed.nome_documento == "CCIR"
    assert parsed.ano_emissao == "2024"
    assert parsed.fazenda == "CONTENDAS"
    assert parsed.parceiro == "RADIALEUCALYPT"


def test_parse_fundos():
    texto = """
    Contrato de 08/05/2024 número 232853 para fundo Manulife e SPE Trim.
    Título TIP.
    """
    parsed = parse_document(texto, context_hint="fundos")
    assert parsed.fundo == "MANULIFE"
    assert parsed.spe == "TRIM"
    assert parsed.titulo_documento == "TIP"
