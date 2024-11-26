#' @title: Web Scrapping DFimoveis
#' @author: Luiz Paulo Tavares 

import pandas as pd
import requests
import time
import os
import re

from bs4 import BeautifulSoup

# Constants

HEADERS = {
    # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:92.0) Gecko/20100101 Firefox/92.0'
}

class PropertyScraper:
    def __init__(self, base_url, headers = HEADERS):
        self.base_url = base_url
        self.headers = headers

    def extract_property_data(self, property_soup):

        """Extracts relevant data from a property listing HTML element."""

        def get_text_or_none(element, selector):
            selected_element = element.select_one(selector)
            return selected_element.get_text(strip=True) if selected_element else None

        # Descrição \* 

        description = get_text_or_none(property_soup, 'h2.new-title.phrase')
        
        # Tipo de imóvel \* 
        
        type_property = get_text_or_none(property_soup, 'h3.new-desc.phrase')
        
        # Preço do imóvel \* 
        
        price = get_text_or_none(property_soup, 'div.new-price span')
        
        # Tamanho do imóvel em m² \* 

        size_m2_element = property_soup.find('span', string = lambda x: x and "m²" in x)
        size_m2 = size_m2_element.get_text(strip = True) if size_m2_element else None
        
        # Nº de quartos \* 

        bedroom_element = property_soup.find('span', string = lambda x: x and re.search(r'\b(quartos?|Quartos?)\b', x))
        bedroom = bedroom_element.get_text(strip = True) if bedroom_element else None
        
        # Nº de vagas de carragem \* 

        car_spaces_element = property_soup.find('span', string = lambda x: x and re.search(r'\b(Vaga?|Vagas?)\b', x))
        car_spaces = car_spaces_element.get_text(strip = True) if car_spaces_element else None

        return {
            'description': description,
            'type': type_property,
            'price': price,
            'size': size_m2,
            'bedrooms': bedroom,
            'car_spaces': car_spaces
        }

    def scrape_page(self, page_number):

        """Scrapes a single page for property listings."""

        url = f"{self.base_url}{page_number}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code != 200:
            print(f"Erro ao acessar a página {page_number}. Status code: {response.status_code}")
            return [], response.status_code

        site = BeautifulSoup(response.text, "html.parser")
        properties = site.find_all('div', class_='new-info')
        
        return [self.extract_property_data(property_soup) for property_soup in properties], response.status_code

    def scrape_all_pages(self):
        
        """Scrapes all pages until no more data is available or an error occurs."""

        all_properties = []
        page = 1

        for i in range(1):
            print(f"Raspando a página {page}...")
            properties, status_code = self.scrape_page(page)
            
            if status_code != 200 or not properties:
                print(f"Parando a raspagem. Status code: {status_code}")
                break
            
            all_properties.extend(properties)
            page += 1
            time.sleep(2)

        return all_properties

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


# Inicializa o scraper com a URL base para aluguel ou vendas

BASE_URL_ALUGUEL = "https://www.dfimoveis.com.br/aluguel/df/todos/imoveis?pagina="
BASE_URL_VENDA = "https://www.dfimoveis.com.br/venda/df/todos/imoveis?pagina="

# Selecione o tipo de raspagem ('aluguel' ou 'venda')

tipo_modo = 'venda'  # Ou altere para 'venda' conforme necessário
base_url = BASE_URL_ALUGUEL if tipo_modo == 'aluguel' else BASE_URL_VENDA

scraper = PropertyScraper(base_url=base_url)

# Scrape all properties

properties_data = scraper.scrape_all_pages()
print(properties_data)

# data_handler = DataHandler(properties_data)
# df = data_handler.create_dataframe(tipo_modo)  

# print(df)
# print(os.getcwd())

# Save the DataFrame to an Excel file

# filename = f'imoveis_df_{tipo_modo}.xlsx'  
# data_handler.save_to_excel(df, filename)
