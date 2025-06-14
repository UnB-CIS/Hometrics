import random
import time
from datetime import datetime

import pandas as pd
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


class ScrapingNetImoveis:
    def __init__(self, tipo):
        self.tipo = tipo
        self.num_dados_raspados = 0
        self.data = []
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
        ]

    def config_driver(self):
        """Configura o WebDriver com opções específicas."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        user_agent = random.choice(self.user_agents)
        chrome_options.add_argument(f"user-agent={user_agent}")
        return chrome_options, user_agent

    def create_page_soup(self, num, time_navigation=1):
        """Cria o BeautifulSoup da página."""
        chrome_options, user_agent = self.config_driver()
        print(f"----USER AGENT ESCOLHIDO: {user_agent}")

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        url = f"https://www.netimoveis.com/{self.tipo}/distrito-federal/brasilia?transacao={self.tipo}&localizacao=BR-DF-brasilia---&pagina={num}"
        driver.get(url)
        time.sleep(time_navigation)

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
        except Exception as e:
            print(f"Falha ao carregar a página {num}: {e}")
            driver.quit()
            return None

        soup = bs(driver.page_source, "html.parser")
        driver.quit()
        return soup

    def find_imoveis(self, soup):
        """Busca os imóveis na página HTML."""
        try:
            lista_imoveis = soup.find_all("section", class_="imovel-info")
            if not lista_imoveis:
                print("Nenhum imóvel encontrado na página.")
                return None
            return lista_imoveis
        except Exception as e:
            print(f"Erro ao buscar imóveis: {e}")
            return None

    def process_imovel(self, imovel):
        """Processa um único imóvel e retorna seus dados."""
        try:
            address = imovel.select_one("div.endereco").text.strip()
            if "{{ nomeBairro }}" in address:
                return None

            price = imovel.select_one("div.valor").text.split()[1].replace(".", "")

            features = {
                "type": imovel.select_one("div.mb-2.tipo h2"),
                "area": imovel.select_one("div.caracteristica.area"),
                "quartos": imovel.select_one("div.caracteristica.quartos"),
                "banheiros": imovel.select_one("div.caracteristica.banheiros"),
                "vagas": imovel.select_one("div.caracteristica.vagas"),
            }

            data = {
                "description": address,
                "type": features["type"].text.split()[0] if features["type"] else None,
                "price": price,
                "size_m2": (
                    features["area"].text.split()[0] if features["area"] else None
                ),
                "bedrooms": (
                    features["quartos"].text.split()[0] if features["quartos"] else None
                ),
                "bathrooms": (
                    features["banheiros"].text.split()[0]
                    if features["banheiros"]
                    else None
                ),
                "parking_spaces": (
                    features["vagas"].text.split()[0] if features["vagas"] else None
                ),
            }

            self.num_dados_raspados += 1
            return data

        except Exception as e:
            print(f"Erro ao processar imóvel: {e}")
            return None

    def scrape_all_pages(self):
        """Executa o scraping completo de todas as páginas disponíveis."""
        num_page = 1
        while True:
            print(f"Processando página {num_page}...")
            soup = self.create_page_soup(num_page)

            if not soup:
                break

            lista_imoveis = self.find_imoveis(soup)

            if not lista_imoveis or len(lista_imoveis) < 5:
                print("Fim das páginas disponíveis.")
                break

            for imovel in lista_imoveis:
                imovel_data = self.process_imovel(imovel)
                if imovel_data:
                    self.data.append(imovel_data)

            num_page += 1

        print(
            f"Scraping completo! Total de {self.num_dados_raspados} imóveis coletados."
        )
        return self.data


class DataHandler:
    def __init__(self, data):
        self.data = data

    def create_dataframe(self, modo):
        """Cria DataFrame com os dados e adiciona coluna de modo."""
        df = pd.DataFrame(self.data)
        df["modo"] = modo
        df["price"] = pd.to_numeric(df["price"], errors="coerce")
        return df.dropna(subset=["price"])

    def save_to_excel(self, df, filename):
        """Salva os dados em um arquivo Excel."""
        df.to_excel(filename, index=False)
        print(f"Dados salvos em {filename} ({len(df)} registros)")


def main():
    # Configurações
    TIPOS = ["locacao", "venda"]
    DATA_SCAPING = datetime.now().strftime("%Y%m%d_%H%M%S")

    for tipo in TIPOS:
        # Executa scraping
        scraper = ScrapingNetImoveis(tipo)
        dados = scraper.scrape_all_pages()

        # Processa e salva dados
        if dados:
            handler = DataHandler(dados)
            df = handler.create_dataframe(tipo)
            filename = f"netimoveis_{tipo}_{DATA_SCAPING}.xlsx"
            handler.save_to_excel(df, filename)


if __name__ == "__main__":
    main()
