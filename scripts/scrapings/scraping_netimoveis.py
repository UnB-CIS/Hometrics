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


def scrapper():
      ...

# Config chrome com webdriver manager
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

num = 1 #contador para paginas
dados_vendas = list()
time_navagation = 2
num_data_scraper = 0
comando = 'cls' if os.name == 'nt' else 'clear'
tipo = 'locacao'

while True:
      
      user_agent = random.choice(user_agents)
      chrome_options.add_argument(f"user-agent={user_agent}")
      
      print('----USER ESCOLHIDO: ', user_agent)
      if num > 15: 
            print('Teste')
            break
      service = Service(ChromeDriverManager().install())
      driver = webdriver.Chrome(service=service, options=chrome_options)

      num_page = str(num)
      URL = f"https://www.netimoveis.com/{tipo}/distrito-federal/brasilia?transacao={tipo}&localizacao=BR-DF-brasilia---&pagina={num_page}"
      """https://www.netimoveis.com/locacao/distrito-federal/brasilia?transacao=locacao&localizacao=BR-DF-brasilia---&pagina=34"""
      
      driver.get(URL)
      time.sleep(time_navagation)
      
      try:
            WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body")))
      except:
            print(f"Falha ao carregar a página {num_page}. Tentando a próxima...")
            continue
      
      page_source = driver.page_source

      soup = bs(page_source, 'html.parser')

      try:
            imoveis = soup.find_all("section", class_='imovel-info')      
      except:
            print('programa parou!')
            break
      
      print(10 * '##')
      print('Numero de imoveis encontrados na pagina: ', len(imoveis))
      print(10 * '##')

      for imovel in imoveis:
            try: 
                  print('Iniciando novo scraping!')

                  '''Buscando caracteristicas de imoveis'''
            
                  address = imovel.select_one("div.endereco").text  if imovel.select_one("div.endereco") else None
                  m2 = imovel.select_one("div.caracteristica.area").text.split() if imovel.select_one("div.caracteristica.area") else None
                  bedroom = imovel.select_one("div.caracteristica.quartos").text.split() if imovel.select_one("div.caracteristica.quartos") else None
                  vagas_estacionameto = imovel.select_one("div.caracteristica.vagas").text.split() if imovel.select_one("div.caracteristica.vagas") else None
                  bathroom = imovel.select_one("div.caracteristica.banheiros").text.split() if imovel.select_one("div.caracteristica.banheiros") else None
                  price = imovel.select_one("div.valor").text.split() if imovel.select_one("div.valor") else None

                  data = { 
                        'description': address,
                        'price': price[1],
                        'size_m2': m2[0],
                        'bedrooms': bedroom[0],
                        'bathrooms':  bathroom[0],
                        'parking_spaces': vagas_estacionameto[0]
                  }

                  dados_vendas.append(data)
                  
            except Exception as e:
                  print(f'Erro na operacao de scraping!\nError:{e}')
                  print('Nao iremos contabilizar essa contagem nos dados rapados!')
                  print()

            else:
                  num_data_scraper +=1
                  print(f'Operacao OK!\n')
            
            finally:
                  print(f'Numero de raspagens: {num_data_scraper}')
                  continue
                        
      driver.quit()
      num+=1
      
      time.sleep(2)
      os.system(comando) 
      



data_scraping = datetime.now().strftime('%Y%m%d_%H%M%S')

nome_arquivo = f"{'scraping_netimoveis'}_{data_scraping}.csv"
df = pd.DataFrame(dados_vendas)
df.to_csv(nome_arquivo, index=False)
print(f'Dados exportados! Numero de dados: {df.shape[0]}')

if __name__ == 'main':
      ...
