# renomeador_chandra

Utilitário em Python para renomear documentos de contratos e ambientais a partir de OCR com o modelo Chandra.

## Instalação

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Para utilizar OCR real, instale também as dependências opcionais:

```bash
pip install renomeador-chandra[ocr]
```

## Uso básico

Processar uma pasta inteira:

```bash
renomeador-chandra process ./entrada --out ./saida --context auto
```

Executar apenas uma auditoria de OCR:

```bash
renomeador-chandra audit ./entrada/Contrato1.pdf --out ./audit
```

Validar um único arquivo sem renomear:

```bash
renomeador-chandra validate ./entrada/Contrato1.pdf
```

## Testes

```bash
pytest
```

## Estrutura do projeto

- `renomeador_chandra/` – código-fonte principal.
- `tests/` – testes automatizados.
- `pyproject.toml` – metadados e dependências do pacote.

## Limitações

- A integração com o modelo Chandra OCR só é executada quando o pacote `chandra-ocr` está disponível.
- Em ambientes sem OCR real, é utilizado um fallback baseado em `pytesseract` (opcional) ou leitura direta de arquivos `.txt`.
