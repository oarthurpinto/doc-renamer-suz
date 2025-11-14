from pathlib import Path

from renomeador_chandra import cli


def test_process_contract(tmp_path: Path):
    entrada = tmp_path / "entrada"
    saida = tmp_path / "saida"
    entrada.mkdir()
    saida.mkdir()

    arquivo = entrada / "contrato.txt"
    arquivo.write_text(
        "Contrato celebrado em 18/10/2023 com número 232853. Tipo CCV título CONTR. Fazenda Contendas parceiro Radial Eucalypt.",
        encoding="utf-8",
    )

    cli.process(path_in=entrada, out=saida, context="mercado", dry_run=False, provider="hf", page_range=None)

    arquivos_saida = list(saida.iterdir())
    assert any("20231018_CCV_232853_CONTR_CONTENDAS" in arquivo.name for arquivo in arquivos_saida)
    relatorio = saida / "renomeacoes.csv"
    assert relatorio.exists()
