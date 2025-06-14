import concurrent.futures
import random
import time

import requests
from bs4 import BeautifulSoup
from property_data_extractor import PropertyDataExtractor

from scripts.utils.data_handler import DataHandler


class PropertyScraper:
    """Classe responsável por raspar listagens de propriedades de websites"""

    def __init__(self, base_url, headers, property_type="imoveis"):
        """Inicializa o raspador com URL base, headers e tipo de propriedade."""
        self.base_url = base_url.format(property_type=property_type)
        self.headers = headers
        self.property_type = property_type
        self.data_extractor = PropertyDataExtractor(property_type=property_type)

    def extract_property_data(self, property_soup):
        """Delega a extração de dados de propriedade para a instância de PropertyDataExtractor."""
        property_data = self.data_extractor.extract_property_data(property_soup)

        if "size_m2" in property_data and "size" not in property_data:
            property_data["size"] = property_data["size_m2"]

        if "bedroom" in property_data and "bedrooms" not in property_data:
            property_data["bedrooms"] = property_data["bedroom"]

        if "parking" in property_data and "parking_spaces" not in property_data:
            property_data["parking_spaces"] = property_data["parking"]

        return property_data

    def scrape_page(self, page_number, max_retries=3):
        """Raspa uma única página de listagens de propriedades com lógica de novas tentativas."""

        retries = 0
        backoff_factor = 2
        base_wait_time = 2

        while retries <= max_retries:
            try:
                url = f"{self.base_url}{page_number}"

                jitter = random.uniform(0.5, 1.5)
                wait_time = base_wait_time * (backoff_factor**retries) * jitter

                if retries > 0:
                    print(
                        f"Tentativa #{retries} para página {page_number} - aguardando {wait_time:.2f} segundos..."
                    )
                    time.sleep(wait_time)

                response = requests.get(url, headers=self.headers)

                if response.status_code == 200:
                    site = BeautifulSoup(response.text, "html.parser")
                    properties = site.find_all("div", class_="new-info")

                    if properties:
                        return [
                            self.extract_property_data(property_soup)
                            for property_soup in properties
                        ], 200
                    else:
                        # Esta pode ser a última página sem mais resultados
                        print(f"Página {page_number} não contém propriedades.")
                        return (
                            [],
                            204,
                        )  # Usando 204 para indicar sem conteúdo, mas requisição bem-sucedida

                if response.status_code == 429:
                    print(
                        f"Limite de taxa atingido na página {page_number}. Aguardando antes de tentar novamente..."
                    )
                    retries += 1
                    continue

                if response.status_code >= 500:
                    print(
                        f"Erro de servidor na página {page_number}. Tentando novamente..."
                    )
                    retries += 1
                    continue

                if response.status_code >= 400 and response.status_code < 500:
                    print(
                        f"Erro de cliente na página {page_number}. Status code: {response.status_code}"
                    )
                    return [], response.status_code

            except requests.RequestException as e:
                print(f"Erro de conexão na página {page_number}: {str(e)}")
                retries += 1
                continue

        print(f"Número máximo de tentativas atingido para a página {page_number}")
        return [], 503

    def scrape_all_pages(
        self,
        max_pages=None,
        workers=1,
        batch_size=10,
        batch_delay=30,
        save_each_batch=True,
        category="venda",
        property_type="imoveis",
        output_dir=None,
        append=True,
    ):
        """# Raspa todas as páginas até que não haja mais dados disponíveis ou max_pages seja atingido."""

        all_properties = []
        empty_page_count = 0
        page = 1
        current_batch = 1
        consecutive_empty_pages_threshold = 2

        total_batches = None
        if max_pages:
            total_batches = (max_pages + batch_size - 1) // batch_size
            print(
                f"Scraping will be performed in {total_batches} batches of {batch_size} pages each."
            )

        while True:
            batch_properties = []
            batch_start_page = page
            print(
                f"\n--- Starting batch {current_batch} (pages {batch_start_page} to {batch_start_page + batch_size - 1}) ---"
            )

            with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
                batch_page_count = 0
                futures = []

                for i in range(min(batch_size, workers)):
                    if max_pages and page > max_pages:
                        break

                    print(f"Raspando a página {page}...")
                    futures.append(executor.submit(self.scrape_page, page))
                    page += 1
                    batch_page_count += 1

                empty_in_batch = 0
                for future in concurrent.futures.as_completed(futures):
                    properties, status_code = future.result()

                    if status_code == 204:
                        empty_in_batch += 1
                        empty_page_count += 1
                        if empty_page_count >= consecutive_empty_pages_threshold:
                            print(
                                f"Encontradas {consecutive_empty_pages_threshold} páginas vazias consecutivas. Assumindo fim dos resultados."
                            )
                            return all_properties
                    elif status_code != 200:
                        print(f"Erro ao acessar página. Status code: {status_code}")
                    else:
                        empty_page_count = 0
                        batch_properties.extend(properties)

                while batch_page_count < batch_size:
                    if max_pages and page > max_pages:
                        break

                    print(f"Raspando a página {page}...")
                    future = executor.submit(self.scrape_page, page)
                    page += 1
                    batch_page_count += 1

                    properties, status_code = future.result()
                    if status_code == 204:
                        empty_in_batch += 1
                        empty_page_count += 1
                        if empty_page_count >= consecutive_empty_pages_threshold:
                            print(
                                f"Encontradas {consecutive_empty_pages_threshold} páginas vazias consecutivas. Assumindo fim dos resultados."
                            )
                            return all_properties
                    elif status_code != 200:
                        print(f"Erro ao acessar página. Status code: {status_code}")
                    else:
                        empty_page_count = 0
                        batch_properties.extend(properties)

            batch_property_count = len(batch_properties)
            all_properties.extend(batch_properties)

            print(f"\n--- Batch {current_batch} completed ---")
            print(f"Pages processed: {batch_page_count}")
            print(f"Empty pages: {empty_in_batch}")
            print(f"Properties found: {batch_property_count}")
            print(f"Total properties so far: {len(all_properties)}")

            if max_pages and page > max_pages:
                print(f"Atingido o número máximo de páginas: {max_pages}")
                break

            if save_each_batch and batch_properties and output_dir:
                print(f"Saving data from batch {current_batch}...")
                batch_data_handler = DataHandler(batch_properties)
                batch_df = batch_data_handler.create_dataframe(category)

                excel_filename = f"imoveis_df_{category}.xlsx"
                tsv_filename = f"imoveis_df_{category}.tsv"

                batch_data_handler.save_to_excel(
                    batch_df, excel_filename, output_dir=output_dir, append=append
                )
                batch_data_handler.save_to_tsv(
                    batch_df, tsv_filename, output_dir=output_dir, append=append
                )

                print(
                    f"Batch {current_batch} data for {property_type} saved to {output_dir}/{excel_filename} and {output_dir}/{tsv_filename}"
                )

            actual_delay = batch_delay + random.uniform(
                -5, 5
            )  # Adiciona alguma aleatoriedade
            print(f"Pausando por {actual_delay:.1f} segundos antes do próximo lote...")
            time.sleep(actual_delay)
            current_batch += 1

        print(
            f"\nRaspagem concluída. Total de propriedades coletadas: {len(all_properties)}"
        )
        return all_properties
