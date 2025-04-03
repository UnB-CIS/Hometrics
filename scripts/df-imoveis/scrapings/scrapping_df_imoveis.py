#' @title: Web Scrapping DFimoveis
#' @author: Luiz Paulo Tavares 

import pandas as pd
import requests
import time
import os
import re
import concurrent.futures
from utils.data_handler import DataHandler
from bs4 import BeautifulSoup

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
            'address': "",
            'type': type_property,
            'price': price,
            'size': size_m2,
            'bedrooms': bedroom,
            'bathrooms': '',
            'parking_spaces': car_spaces
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

    def scrape_all_pages(self, max_pages=None, workers=1):
        
        """Scrapes all pages until no more data is available or an error occurs."""

        all_properties = []
        page = 1
        continue_scraping = True
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            while continue_scraping:
                futures = []
                
                # Submit batch of pages to the executor
                for i in range(workers):
                    if max_pages and page > max_pages:
                        break
                    print(f"Raspando a página {page}...")
                    futures.append(executor.submit(self.scrape_page, page))
                    page += 1
                
                # Process results as they complete
                for future in concurrent.futures.as_completed(futures):
                    properties, status_code = future.result()
                    if status_code != 200 or not properties:
                        print(f"Parando a raspagem. Status code: {status_code}")
                        continue_scraping = False
                    else:
                        all_properties.extend(properties)
                
                # If we've hit max_pages or encountered an error, stop
                if max_pages and page > max_pages:
                    print(f"Atingido o número máximo de páginas: {max_pages}")
                    break
                
                if not continue_scraping:
                    print("Parando a raspagem devido a erro ou sem mais propriedades")
                    break
                    
                time.sleep(1)  # Pausa pequena entre lotes para não sobrecarregar o servidor

        return all_properties

# URL Base constants
BASE_URL_ALUGUEL = "https://www.dfimoveis.com.br/aluguel/df/todos/imoveis?pagina="
BASE_URL_VENDA = "https://www.dfimoveis.com.br/venda/df/todos/imoveis?pagina="

def run_scraper(category='venda', max_pages=500, workers=5, output_dir=None, append=False, custom_output_files=None):
    """Run the DF Imoveis scraper with the specified parameters.
    
    Args:
        category (str): Type of properties to scrape ('venda' or 'aluguel')
        max_pages (int): Maximum number of pages to scrape
        workers (int): Number of concurrent workers for threading
        output_dir (str): Directory to save output files
        append (bool): Whether to append to existing files
        custom_output_files (dict): Custom file paths for output (excel_path, csv_path)
    """
    # Select the base URL based on the scraping mode
    base_url = BASE_URL_ALUGUEL if category == 'aluguel' else BASE_URL_VENDA
    
    # Initialize scraper and perform scraping
    scraper = PropertyScraper(base_url=base_url)
    properties_data = scraper.scrape_all_pages(max_pages=max_pages, workers=workers)
    
    # Process scraped data
    
    data_handler = DataHandler(properties_data)
    df = data_handler.create_dataframe(category)
    
    # Save the data to files if output_dir is provided
    if output_dir is not None:
        # Check if custom output files are specified
        if custom_output_files and 'excel_path' in custom_output_files and 'csv_path' in custom_output_files:
            # Use the standardized file paths from the orchestrator
            excel_path = custom_output_files['excel_path']
            csv_path = custom_output_files['csv_path']
            
            # Save directly to specified paths
            data_handler.save_to_excel(df, excel_path, append=append)
            data_handler.save_to_csv(df, csv_path, append=append)
            
            print(f"Excel data saved to {excel_path}")
            print(f"CSV data saved to {csv_path}")
        else:
            # Use the default file naming scheme
            excel_filename = f'imoveis_df_{category}.xlsx'
            csv_filename = f'imoveis_df_{category}.csv'
            
            data_handler.save_to_excel(df, excel_filename, output_dir=output_dir, append=append)
            data_handler.save_to_csv(df, csv_filename, output_dir=output_dir, append=append)
            
            print(f"Excel data saved to {output_dir}/{excel_filename}")
            print(f"CSV data saved to {output_dir}/{csv_filename}")
    
    return df

# This allows the script to be run directly for testing
if __name__ == "__main__":
    # Example usage when running the script directly
    df = run_scraper(
        category='venda',
        max_pages=500,
        workers=5,
        output_dir="scripts/df-imoveis/data/scraped",
        append=True
    )
