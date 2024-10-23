# Projeto: Projeto de Avaliação e Predição de Preços de Imóveis (Housing Prices Prediction)

Este projeto, desenvolvido pelo grupo IEEE-CIS, tem como objetivo a predição de valores de venda e de aluguel de imóveis. Através da coleta de dados de diversos sites de imóveis, criamos um pipeline automatizado que organiza, processa e armazena esses dados para análise e modelagem preditiva.

A ideia central é utilizar técnicas de machine learning em dados de imóveis para oferecer estimativas mais precisas de preços de mercado.

## Estrutura do projeto

```
.
├── db
│   └── mongodb.py                 # Scripts de configuração e conexão ao banco de dados MongoDB
├── docs
│   ├── Project_documentation.docx # Documentação do projeto em formato Word
│   └── Project_documentation.pdf  # Documentação do projeto em formato PDF
├── pipeline
│   ├── config                     # Arquivos de configuração relacionados ao pipeline
│   ├── dags                       # Diretório onde ficam os DAGs do Apache Airflow
│   ├── logs                       # Logs gerados pelo Airflow durante a execução dos DAGs
│   └── plugins                    # Plugins customizados para o Airflow, se necessário
├── scripts
│   ├── df-imoveis                 # Scripts de scraping para o site 'df-imoveis'
│   ├── net-imoveis                # Scripts de scraping para o site 'net-imoveis'
│   ├── w-imoveis                  # Scripts de scraping para o site 'w-imoveis'
│   └── zap-imoveis                # Scripts de scraping para o site 'zap-imoveis'
├── .env.example                   # Exemplo de arquivo de variáveis de ambiente para configuração do projeto
├── .gitignore                     # Arquivo para especificar quais arquivos e diretórios devem ser ignorados pelo Git
├── docker-compose.yaml            # Arquivo de configuração do Docker Compose para orquestrar os serviços do projeto
├── README.md                      # Documentação principal do projeto
├── requirements.txt               # Lista de dependências Python necessárias para o projeto
├── db
```

## Instalação e Configuração

### Clonar repositório

```
git clone <URL-do-repositório>
cd <nome-do-repositório>
```

### Configuração do ambiente Docker

```
docker-compose up -d

```

### Instalação das Dependências

Todas as dependências de pacotes Python necessários para o projeto estão listadas no arquivo requirements.txt para usuários que optem por não usar o docker. Para instalar os pacotes, siga os seguintes passos:

Certifique-se de estar no diretório raiz do projeto.

Execute o comando abaixo para instalar as dependências:

```
pip install -r requirements.txt
```
