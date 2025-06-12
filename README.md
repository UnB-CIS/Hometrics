# Projeto: Projeto de Avaliação e Predição de Preços de Imóveis (Housing Prices Prediction)

Este projeto, desenvolvido pelo grupo IEEE-CIS, tem como objetivo a predição de valores de venda e de aluguel de imóveis. Através da coleta de dados de diversos sites de imóveis, criamos um pipeline automatizado que organiza, processa e armazena esses dados para análise e modelagem preditiva.

A ideia central é utilizar técnicas de machine learning em dados de imóveis para oferecer estimativas mais precisas de preços de mercado.

## Estrutura do projeto

```markdown
├── database
│   ├── config.py                  # Configurações de conexão com o MongoDB
│   ├── connection.py              # Classe para gerenciar a conexão com o MongoDB
│   ├── repository.py              # Funções para manipulação de dados de imóveis (CRUD)
├── docs
│   ├── Project_documentation.docx # Documentação do projeto em formato Word
│   └── Project_documentation.pdf  # Documentação do projeto em formato PDF
├── pipeline
│   ├── data_cleaning.py           # Responsável por realizar o tratamento dos dados coletados
│   ├── data_scraping.py           # Orquestra a execução dos scrapers
│   ├── data_transform.py          # Responsável pela transformação e normalização dos dados
│   └── main.py                    # Gerencia a interação com o banco de dados
├── scripts
│   ├── df-imoveis                 # Scripts de scraping para o site 'df-imoveis'
│   ├── net-imoveis                # Scripts de scraping para o site 'net-imoveis'
│   ├── quinta-andar               # Scripts de scraping para o site 'quinta-andar'
│   ├── viva-real                  # Scripts de scraping para o site 'viva-real'
│   ├── w-imoveis                  # Scripts de scraping para o site 'w-imoveis'
│   ├── zap-imoveis                # Scripts de scraping para o site 'zap-imoveis'
├── utils
│   └── data_handler.py            # Classe para manipulação e salvamento de dados
```

## Funcionalidades Principais

### Web Scraping Multi-site

- Suporte para múltiplos sites de imóveis: DF-Imóveis, Net-Imóveis, Quinto Andar, Viva Real, W-Imóveis e Zap-Imóveis
- Coleta automatizada de dados de imóveis com suporte para diferentes tipos de contratos (venda/aluguel)
- Suporte para diferentes tipos de propriedades: apartamentos, casas, flats, etc.

### Processamento de Dados

- Limpeza e normalização de dados de imóveis
- Geocodificação de endereços para obtenção de coordenadas geográficas
- Suporte para múltiplos serviços de geocodificação:
  - Nominatim (serviço gratuito, padrão)
  - Google Maps API (requer chave de API)

### Armazenamento de Dados

- Salvamento incremental de dados (modo append)
- Suporte para formatos Excel e CSV
- Processamento em lotes com salvamento automático para evitar perda de dados
- Tratamento robusto para arquivos corrompidos com funcionalidade de backup

## Instalação e Configuração

### Clonar repositório

```bash
git clone <URL-do-repositório>
cd <nome-do-repositório>
```

### Configurando as variáveis de ambiente

Crie um arquivo `.env` a partir do `.env.example`.

```bash
cp .env.example .env
```

Então, preencha o arquivo `.env` com as devidas variáveis de ambiente do projeto:

- `MONGODB_URI`: URI de conexão com o MongoDB
- `GOOGLE_MAPS_API_KEY`: Chave de API do Google Maps (opcional, para geocodificação)

### Utilizando o Docker

#### Configuração do ambiente Docker

```bash
docker-compose up -d
```

## Utilizando o ambiente virtual

### Instalação das Dependências

Todas as dependências de pacotes Python necessários para o projeto estão listadas no arquivo requirements.txt para usuários que optem por não usar o docker. Para instalar os pacotes, siga os seguintes passos:

Certifique-se de estar no diretório raiz do projeto.

Execute o comando abaixo para instalar as dependências:

```bash
pip install -r requirements.txt
```

Verifique o python PATH local e execute o arquivo desejado.

## Branches principais

### Main

Branch principal do repositório e representa o ambiente de produção do projeto.

## Boas Práticas de GitHub

### Nomenclatura de novas branchs

Ao criar a nova branch, procure trazer significado a ela desde a sua nomeação, e aqui seguem algumas boas práticas:

#### Prefixo

Coloque um prefixo na branch, a fim de esclarecer sua intenção. Alguns exemplos abaixo:

- `feat/`: implementação de uma nova funcionalidade do software;
- `fix/`: implementação de uma correção no software;
- `docs/`: documentação de parte ou trecho do software;
- `refactor/`: refatoração de parte ou trecho do software.

#### Nome

Após o prefixo, coloque um nome declarativo ou explicativo do objetivo da branch, ou seja, um nome que diga
o que será implementado na branch. Procure escrever na convenção "kebab-case".

#### Sufixo

Após o nome, adicione um sufixo numérico, explicitando qual a issue do projeto a que se refere a nova branch.

#### Exemplo

- `feat/data-scraping-21`
- `fix/data_transformation-bug-13`
- `refactor/api-fetch-refactor-4`

### Novas issues no Project

É necessário tomar algumas atenções quanto às issues do GitHub.

#### Integração Contínua

Focando-se na boa prática de integração contínua, faz-se necessário particionar pendências e novas funcionalidades
o máximo possível, enquanto houver sentido, afim de se criar issues com menores responsabilidades, promovendo
branchs menores, PRs menores, merges mais frequentes e um código-fonte com atualizações constantes.
