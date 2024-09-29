#' @title: Web Scrapping DFimoveis
#' @author: Luiz Paulo Tavares 

import pandas as pd
import requests
import time
import os
import re

from bs4 import BeautifulSoup

# Constants \* 

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'
}

BASE_URL = "https://www.dfimoveis.com.br/venda/df/todos/imoveis?pagina="
NUM_PAGES = 1413 # A dinâmica de raspagem entre as pages está estática, precisa ser passado o número de paǵinas disponíveis
# \* possível automação: deixar automático o NUM_PAGES \* 
REQUEST_DELAY = 2  

# Function for extracting data from a single property

def extract_property_data(property_soup):
    def get_text_or_none(element, selector):
        selected_element = element.select_one(selector)
        return selected_element.get_text(strip = True) if selected_element else None

    # Descrição do imóvel \* 

    description = get_text_or_none(property_soup, 'h2.new-title.phrase')

    # Tipo do imóvel \* 

    type_property = get_text_or_none(property_soup, 'h3.new-desc.phrase')

    # Preço total do imóvel \* 

    price = get_text_or_none(property_soup, 'div.new-price span')

    # Preço por m² \* 

    price_per_m2 = get_text_or_none(property_soup, 'h4:contains("Valor m² R$") span')

    # Tamanho em m² \* 

    size_m2_element = property_soup.find('span', string = lambda x: x and "m²" in x)
    size_m2 = size_m2_element.get_text(strip = True) if size_m2_element else None

    # Nº de quartos \* 

    bedroom_element = property_soup.find('span', string = lambda x: x and re.search(r'\b(quartos?|Quartos?)\b', x))
    bedroom = bedroom_element.get_text(strip = True) if bedroom_element else None

    # Número de Vagas para carros \* 

    car_spaces_element = property_soup.find('span', string = lambda x: x and re.search(r'\b(Vaga?|Vagas?)\b', x))
    car_spaces = car_spaces_element.get_text(strip = True) if car_spaces_element else None


    return {
        
        'description': description,
        'type': type_property,
        'price': price,
        'price_per_m2': price_per_m2,
        'size': size_m2,
        'bedrooms': bedroom, 
        'car_spaces': car_spaces
    }

# Function for scraping a single page \* 

def scrape_page(page_number):
    url = f"{BASE_URL}{page_number}"
    response = requests.get(url, headers = HEADERS)
    
    if response.status_code != 200:
        print(f"Erro ao acessar a página {page_number}. Status code: {response.status_code}")
        return []

    site = BeautifulSoup(response.text, "html.parser")
    current_page = site.find('span', class_='active')
    
    if current_page:
        print(f"Raspando dados da página {current_page.get_text(strip=True)}...")

    properties = site.find_all('div', class_='new-info')
    return [extract_property_data(property_soup) for property_soup in properties]

# Function to scrape multiple pages \* 

def scrape_multiple_pages(num_pages):
    all_properties = []

    for page in range(1, num_pages + 1):
        print(f"Raspando a página {page}...")
        properties = scrape_page(page)
        all_properties.extend(properties)

        time.sleep(REQUEST_DELAY)

    return all_properties

# Function to save data to a DataFrame

def create_dataframe(properties_data):
    return pd.DataFrame(properties_data)

# Save xlsx \* 

def save_to_excel(df, filename):
    df.to_excel(filename, index=False) 

# Main script \* 

if __name__ == "__main__":
    properties_data = scrape_multiple_pages(NUM_PAGES)
    df = create_dataframe(properties_data)
    print(df)
    print(os.getcwd())
    
    # Save DataFrame to an Excel file
    save_to_excel(df, 'imoveis_df.xlsx')