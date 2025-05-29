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

### `data-cleaning.py`

Este arquivo contém a classe `DataCleaner`, responsável por realizar o tratamento dos dados coletados, como a remoção de inconsistências e duplicações.

#### Classe `DataCleaner`

A classe `DataCleaner` inclui métodos para limpar e padronizar os dados, garantindo que os dados estejam consistentes e prontos para a análise ou armazenamento.

##### Métodos

- **`remove_duplicates(self)`**: Remove dicionários duplicados da lista.
- **`remove_empty_values(self)`**: Remove dicionários com valores vazios.
- **`standardize_keys(self, standard_keys)`**: Garante que todos os dicionários tenham as mesmas chaves.
- **`convert_data_types(self)`**: Converte representações de strings de números para tipos numéricos reais.
- **`clean_data(self, standard_keys)`**: Executa todos os métodos de limpeza e retorna os dados limpos.

#### Exemplo de Uso

```python
data = [
    {"name": "Alice", "age": "30", "height": "5.5"},
    {"name": "Bob", "age": "25", "height": "6.0"},
    {"name": "Alice", "age": "30", "height": "5.5"},
    {"name": "Charlie", "age": "", "height": "5.8"}
]

cleaner = DataCleaner(data)
standard_keys = ["name", "age", "height"]
cleaned_data = cleaner.clean_data(standard_keys)

print(cleaned_data)
```

### `data-transform.py`

Este arquivo contém a classe `DataTransformer`, responsável pela transformação e normalização dos dados coletados, preparando-os para a análise ou armazenamento em um banco de dados MongoDB.

#### Classe `DataTransformer`

A classe `DataTransformer` inclui métodos para transformar e normalizar os dados, garantindo que os tipos de dados sejam consistentes e adequados para armazenamento.

- **`transform_price(self)`**: Converte o preço para o tipo float.
- **`transform_size(self)`**: Converte o tamanho para o tipo inteiro.
- **`transform_bedrooms(self)`**: Converte o número de quartos para o tipo inteiro.
- **`transform_car_spaces(self)`**: Converte o número de vagas de carro para o tipo inteiro.
- **`transform_data(self)`**: Executa todos os métodos de transformação e retorna os dados transformados.
- **`normalize_state(self)`**: Normaliza as abreviações dos estados para seus nomes completos.
- **`normalize_city(self)`**: Garante que os nomes das cidades estejam consistentemente capitalizados.
- **`normalize_description(self)`**: Padroniza o formato das descrições.
- **`transform_data(self)`**: Executa todos os métodos de transformação e normalização e retorna os dados transformados.

## Exemplo de uso

```python
data = [
    {
        "state": "RJ",
        "city": "Rio de Janeiro",
        "description": "Rua Barata Ribeiro, Copacabana",
        "type": "Venda Apartamento 80 m²",
        "price": "900",
        "size": "80",
        "bedrooms": "2",
        "car_spaces": "1",
    }
]

transformer = DataTransformer(data)
transformed_data = transformer.transform_data()
print(transformed_data)
```
