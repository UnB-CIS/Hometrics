# Documentação da Pasta `scripts`

A pasta `scripts` contém os arquivos responsáveis pela execução de web scraping, onde cada arquivo é responsável por realizar a coleta de dados de um site específico. O arquivo `data-scraping.py` funciona como orquestrador, coordenando a execução dos diversos scrapers e coletando os dados extraídos. Abaixo estão as descrições dos arquivos e suas respectivas funções dentro da pasta.

## Estrutura da Pasta

- **`data-scraping.py`**: Arquivo principal que orquestra a execução dos scrapers, coletando os dados de todos os sites configurados.
- **`data-cleaning.py`**: Script responsável por realizar o tratamento dos dados coletados, como a remoção de inconsistências e duplicações.
- **`data-transform.py`**: Script responsável pela transformação e normalização dos dados, preparando-os para a análise ou armazenamento.
- **`site_a/scraper.py`**: Script responsável pelo scraping dos dados do site A.
- **`site_b/scraper.py`**: Script responsável pelo scraping dos dados do site B.
- **`site_c/scraper.py`**: Script responsável pelo scraping dos dados do site C.

### `data-scraping.py`

Este arquivo funciona como orquestrador para a execução de todos os scrapers nas subpastas `scripts.site_a`, `scripts.site_b`, etc. Ele importa dinamicamente os scrapers, executa a função de scraping de cada um e coleta todos os dados extraídos em uma lista única.

### Estrutura do `scraper_info`

O `scraper_info` é uma lista de dicionários, onde cada dicionário possui as seguintes chaves:

- **`path`**: Caminho para o módulo do scraper.
- **`data`**: Nome da variável no módulo do scraper que contém os dados extraídos.

#### Exemplo de `scraper_info`

```python
scraper_info = [
    {"path": "scripts.site_a.scraper", "data": "site_a_data"},
    {"path": "scripts.site_b.scraper", "data": "site_b_data"},
    {"path": "scripts.site_c.scraper", "data": "site_c_data"}
]
```
