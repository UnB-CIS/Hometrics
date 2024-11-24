from datetime import datetime
import os
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

from bs4 import BeautifulSoup as bs
import pandas as pd
import time

class ScrapingNetImoveis:
    def __init__(self, tipo):
        self.tipo = tipo
        self.num_dados_rapasdos = 0

    def config_driver(self):
        """Configura o WebDriver com opções específicas."""
        ...

    def create_page_soup(self, num, time_navigation):
        """Cria o BeautifulSoup da página."""
        ...
    
    def find_imoveis(self, soup):
        """Busca os imóveis na página HTML."""
        ...


    def scrapper(self, lista_imoveis):
        """Processa as informações dos imóveis encontrados."""
        # Implementação aqui...
    


class DataHandler:
    def __init__(self, data):
        self.data = data

    def create_dataframe(self, modo):

        """Creates a Pandas DataFrame from the property data and adds a 'modo' column."""

        df = pd.DataFrame(self.data)
        df['modo'] = modo  
        return df

    def save_to_excel(self, df, filename):

        """Saves the DataFrame to an Excel file."""

        df.to_excel(filename, index = False)
        
        

def config_driver():
    """
    Configura driver de do navegador.

    Args:
          Nenhum.
    Returns:
          String: Contendo o valor aletório de user agents.
          Options: Valor de configuracao do chrome_driver
          Retorna valores para user agentes.

    Exemplo:
          >>>
          Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36, Options() -> opcoes de configuracoes.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
    ]

    user_agent = random.choice(user_agents)
    chrome_options.add_argument(f"user-agent={user_agent}")
    
    return chrome_options, user_agent

def create_page_soup(num, time_navagation, tipo):
    """
    Cria Page Source da pagina e cria o Soup!

    Args:
          Argumentos da funcao
    Returns:
          Type: descricão o que ela realmente
          -> Retorno final
    Exemplo:
          >>> - entrada
          - saida.
    """

    chrome_options, user_agent = config_driver()

    print("----USER ESCOLHIDO: ", user_agent)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    num_page = str(num)
    URL = f"https://www.netimoveis.com/{tipo}/distrito-federal/brasilia?transacao={tipo}&localizacao=BR-DF-brasilia---&pagina={num_page}"

    driver.get(URL)
    time.sleep(time_navagation)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
    except:
        print(f"Falha ao carregar a página {num_page}. Tentando a próxima...")
        return None

    page_source = driver.page_source

    soup = bs(page_source, "html.parser")

    return page_source, soup, driver

def scrapper(lista_imoveis, num_dados_raspados):
    
    data_frame = list()
    for imovel in lista_imoveis:
        
        try:
            print("Iniciando novo scraping!")

            """Buscando caracteristicas de imoveis"""

            address = (
                imovel.select_one("div.endereco").text
                if imovel.select_one("div.endereco")
                else None
            )
            if address and "{{ nomeBairro }}" in address:
                print("Endereço inválido encontrado. Pulando este item...")
                continue

            m2 = (
                imovel.select_one("div.caracteristica.area").text.split()
                if imovel.select_one("div.caracteristica.area")
                else None
            )
            bedroom = (
                imovel.select_one("div.caracteristica.quartos").text.split()
                if imovel.select_one("div.caracteristica.quartos")
                else None
            )
            vagas_estacionameto = (
                imovel.select_one("div.caracteristica.vagas").text.split()
                if imovel.select_one("div.caracteristica.vagas")
                else None
            )
            bathroom = (
                imovel.select_one("div.caracteristica.banheiros").text.split()
                if imovel.select_one("div.caracteristica.banheiros")
                else None
            )
            price = (
                imovel.select_one("div.valor").text.split()
                if imovel.select_one("div.valor")
                else None
            )

            data = {
                "description": address,
                "price": price[1],
                "size_m2": m2[0],
                "bedrooms": bedroom[0],
                "bathrooms": bathroom[0],
                "parking_spaces": vagas_estacionameto[0],
            }

            data_frame.append(data)
         
        except Exception as e:
            print(f"Erro na operacao de scraping!\nError:{e}")
            print("Nao iremos contabilizar essa contagem nos dados rapados!")
            print()

        else:
            num_dados_raspados += 1
            print(f"Operacao OK!\n")

        finally:
            print(f"Numero de raspagens: {num_dados_raspados}")
            continue
        
    return data_frame, num_dados_raspados

def find_imoveis(soup):        
    """
    Localiza todos os imóveis em uma página HTML, utilizando BeautifulSoup.

    Args:
        soup (BeautifulSoup): Objeto BeautifulSoup representando a página HTML.

    Returns:
        list: Lista de elementos HTML representando imóveis encontrados.
        None: Caso ocorra um erro ou nenhum imóvel seja encontrado.
    """
    try:
        # Busca todos os elementos <section> com a classe "imovel-info"
        lista_imoveis = soup.find_all("section", class_="imovel-info")
    except Exception as e:
        print(f"Erro ao buscar imóveis na página: {e}")
        return None

    if not lista_imoveis:
        print("Nenhum imóvel encontrado na página.")
        return None

    return lista_imoveis

def exportar_data_csv(dados: pd.DataFrame, tipo: str) -> None:
    data_scraping = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f"{'scraping_netimoveis_{tipo}'}_{data_scraping}.csv"
    df = pd.DataFrame(dados)
    df_limpo = df.drop_duplicates()
    df_limpo.to_csv(nome_arquivo, index=False)
    print(f"Dados exportados! Numero de dados: {df_limpo.shape[0]}")

def processamento(num_page, tipo):
    
    lista_dados = list()
    time_navagation = 2
    comando = "cls" if os.name == "nt" else "clear"
    total_data_scraper = 0
    while True:
        
        page_source, soup, driver = create_page_soup(num_page, time_navagation, tipo)
        imoveis = find_imoveis(soup) 
        if not imoveis or len(imoveis) < 5:
            print("Chegamos ao fim das páginas.")
            break
        
        dados_rapasdos, total_data_scraper = scrapper(imoveis, total_data_scraper) 
        driver.quit()
        num_page += 1
        lista_dados.extend(dados_rapasdos)

    print(f'###SUCESS### Numero de dados raspados ({tipo.upper()}): ', len(lista_dados))
    return lista_dados

def main():
    
    # Variaveis usadas no sistema!
    num_page = 1  # contador para paginas
    dados_raspados_aluguel = list()
    dados_raspados_vendas = list()
    aluguel = "locacao"
    venda = "venda"
    
    dados_raspados_aluguel = processamento(num_page, aluguel)
    dados_raspados_vendas = processamento(num_page, venda)
    exportar_data_csv(dados_raspados_aluguel, aluguel)
    exportar_data_csv(dados_raspados_vendas, venda)
        
if __name__ == "__main__":
    main()
