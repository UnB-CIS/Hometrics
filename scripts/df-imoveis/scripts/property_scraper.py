import re
import time
import random
import requests
import concurrent.futures
from bs4 import BeautifulSoup
from utils.data_handler import DataHandler

PROPERTY_TYPES = [
    "apartamento",
    "casa",
    "casa-condominio",
    "galpao",
    "garagem", 
    "hotel-flat",
    "kitnet",
    "loja",
    "lote",
    "loteamento",
    "ponto-comercial",
    "predio",
    "rural",
    "sala"
]

class PropertyScraper:
    def __init__(self, base_url, headers, property_type="imoveis"):
        self.base_url = base_url.format(property_type=property_type)
        self.headers = headers
        self.property_type = property_type

    def extract_property_data(self, property_soup):

        """Extrai dados relevantes de um elemento HTML de listagem de propriedade."""
        # Importa re no nível da função para que esteja disponível para todas as funções aninhadas
        
        def get_text_or_none(element, selector):
            selected_element = element.select_one(selector)
            return selected_element.get_text(strip=True) if selected_element else None
        
        def get_link_or_none(element, selector):
            selected_element = element.select_one(selector)
            if selected_element:
                # Verifica se o próprio elemento é um link
                if selected_element.name == 'a':
                    return selected_element.get('href')
                # Verifica se o elemento está dentro de um link
                parent_link = selected_element.find_parent('a')
                if parent_link:
                    return parent_link.get('href')
                # Verifica se há um link dentro do elemento
                child_link = selected_element.find('a')
                if child_link:
                    return child_link.get('href')
            return None

        # Endereço e seu link
        address = get_text_or_none(property_soup, 'h2.new-title.phrase')
        property_link = "https://www.dfimoveis.com.br" + get_link_or_none(property_soup, 'h2.new-title.phrase')
        
        # Tipo de imóvel 
        type_property_full = get_text_or_none(property_soup, 'h3.new-desc.phrase')
        
        # Extrai o tipo de propriedade limpo da descrição completa
        property_type = self.property_type  # Usa como padrão o property_type usado na URL
        
        # Se tivermos type_property_full, tenta extrair um valor mais limpo
        if type_property_full and isinstance(type_property_full, str):
            type_property_full = type_property_full.lower()
            # Verifica cada tipo de propriedade e vê se está na descrição
            for p_type in PROPERTY_TYPES:
                if p_type.lower() in type_property_full:
                    property_type = p_type
                    break
        
        # Preço do imóvel 
        price_raw = get_text_or_none(property_soup, 'div.new-price span')
        
        # Limpa o valor do preço (extrai a parte numérica)
        price = None
        if price_raw:
            if 'Sob Consulta' in price_raw:
                price = ''
            else:
                numeric_match = re.search(r'(\d+(?:[.,]\d+)?)', price_raw)
                if numeric_match:
                    price_value = numeric_match.group(1)
                    price_value = price_value.replace('.', '').replace(',', '.')
                    try:
                        price = float(price_value)
                    except:
                        price = price_raw
                else:
                    price = ''
        
        # Tamanho do imóvel em m² 
        size_m2_element = property_soup.find('span', string = lambda x: x and "m²" in x)
        size_m2_raw = size_m2_element.get_text(strip = True) if size_m2_element else None
        
        # Limpa o valor do tamanho (remove 'm²' e converte para numérico)
        size_m2 = None
        if size_m2_raw:
            # Trata intervalos como "64 a 219 m²" - pega o primeiro número
            if 'a' in size_m2_raw:
                size_m2_raw = size_m2_raw.split('a')[0].strip()
            
            # Extract numeric part
            numeric_match = re.search(r'(\d+(?:[.,]\d+)?)', size_m2_raw)
            if numeric_match:
                size_value = numeric_match.group(1)
                # Substitui vírgula por ponto para valores decimais
                size_value = size_value.replace(',', '.')
                try:
                    size_m2 = float(size_value)
                except:
                    size_m2 = size_value
        
        # Nº de quartos 
        bedroom_element = property_soup.find('span', string = lambda x: x and re.search(r'\b(quartos?|Quartos?)\b', x))
        bedroom_raw = bedroom_element.get_text(strip = True) if bedroom_element else None
        
        # Limpa o valor de quartos (extrai a parte numérica)
        bedroom = None
        if bedroom_raw:
            # Handle ranges like "2 a 3 quartos" - take the first number
            if 'a' in bedroom_raw:
                bedroom_raw = bedroom_raw.split('a')[0].strip()
            
            # Extract numeric part
            numeric_match = re.search(r'(\d+)', bedroom_raw)
            if numeric_match:
                try:
                    bedroom = int(numeric_match.group(1))
                except:
                    bedroom = bedroom_raw
        
        # Nº de vagas de carragem 
        car_spaces_element = property_soup.find('span', string = lambda x: x and re.search(r'\b(Vaga?|Vagas?)\b', x))
        car_spaces_raw = car_spaces_element.get_text(strip = True) if car_spaces_element else None
        
        # Clean parking spaces value (extract numeric part)
        car_spaces = None
        if car_spaces_raw:
            # Extract numeric part
            numeric_match = re.search(r'(\d+)', car_spaces_raw)
            if numeric_match:
                try:
                    car_spaces = int(numeric_match.group(1))
                except:
                    car_spaces = car_spaces_raw
        
        return {
            'address': address,
            'property_type': property_type,
            'price': price,
            'size': size_m2,
            'bedrooms': bedroom,
            'parking_spaces': car_spaces,
            'link': property_link,
        }

    def scrape_page(self, page_number, max_retries=3):
        """Raspa uma única página para listagens de propriedades com lógica de novas tentativas."""

        retries = 0
        backoff_factor = 2
        base_wait_time = 2  # Inicia com um atraso de 2 segundos

        while retries <= max_retries:
            try:
                url = f"{self.base_url}{page_number}"
                
                # Adiciona variação para parecer mais humano
                jitter = random.uniform(0.5, 1.5)
                wait_time = base_wait_time * (backoff_factor ** retries) * jitter
                
                if retries > 0:
                    print(f"Tentativa #{retries} para página {page_number} - aguardando {wait_time:.2f} segundos...")
                    time.sleep(wait_time)
                
                response = requests.get(url, headers=self.headers)
                
                if response.status_code == 200:
                    site = BeautifulSoup(response.text, "html.parser")
                    properties = site.find_all('div', class_='new-info')
                    print(properties)
                    # Verifica se obtivemos propriedades ou resultados vazios
                    if properties:
                        return [self.extract_property_data(property_soup) for property_soup in properties], 200
                    else:
                        # Esta pode ser a última página sem mais resultados
                        print(f"Página {page_number} não contém propriedades.")
                        return [], 204  # Usando 204 para indicar sem conteúdo, mas requisição bem-sucedida
                
                # Trata códigos de erro específicos
                if response.status_code == 429:  # Muitas Requisições
                    print(f"Limite de taxa atingido na página {page_number}. Aguardando antes de tentar novamente...")
                    retries += 1
                    continue
                    
                if response.status_code >= 500:  # Erros de servidor
                    print(f"Erro de servidor na página {page_number}. Tentando novamente...")
                    retries += 1
                    continue
                    
                # Outros erros de cliente que não vale a pena tentar novamente
                if response.status_code >= 400 and response.status_code < 500:
                    print(f"Erro de cliente na página {page_number}. Status code: {response.status_code}")
                    return [], response.status_code
                    
            except requests.RequestException as e:
                print(f"Erro de conexão na página {page_number}: {str(e)}")
                retries += 1
                continue
                
        print(f"Número máximo de tentativas atingido para a página {page_number}")
        return [], 503  # Serviço Indisponível após tentativas

    def scrape_all_pages(self, max_pages=None, workers=1, batch_size=10, batch_delay=30, save_each_batch=True, category='venda', property_type='imoveis', output_dir=None, append=True):
        """Raspa todas as páginas até que não haja mais dados disponíveis ou ocorra um erro."""

        all_properties = []
        empty_page_count = 0
        page = 1
        current_batch = 1
        consecutive_empty_pages_threshold = 2  
        
        # Calculate batches if max_pages is specified
        total_batches = None
        if max_pages:
            total_batches = (max_pages + batch_size - 1) // batch_size
            print(f"Scraping will be performed in {total_batches} batches of {batch_size} pages each.")
        
        while True:
            batch_properties = []
            batch_start_page = page
            print(f"\n--- Starting batch {current_batch} (pages {batch_start_page} to {batch_start_page + batch_size - 1}) ---")
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
                # Process one batch of pages
                batch_page_count = 0
                futures = []
                
                # Submit batch of pages to the executor
                for i in range(min(batch_size, workers)):
                    if max_pages and page > max_pages:
                        break
                        
                    print(f"Raspando a página {page}...")
                    futures.append(executor.submit(self.scrape_page, page))
                    page += 1
                    batch_page_count += 1
                
                # Process initial results
                empty_in_batch = 0
                for future in concurrent.futures.as_completed(futures):
                    properties, status_code = future.result()
                    
                    # Handle different status codes
                    if status_code == 204:  # Sem conteúdo, mas sucesso
                        empty_in_batch += 1
                        empty_page_count += 1
                        if empty_page_count >= consecutive_empty_pages_threshold:
                            print(f"Encontradas {consecutive_empty_pages_threshold} páginas vazias consecutivas. Assumindo fim dos resultados.")
                            return all_properties
                    elif status_code != 200:
                        print(f"Erro ao acessar página. Status code: {status_code}")
                        # Não pare completamente em erros, apenas pule esta página
                    else:  # 200 with properties
                        empty_page_count = 0  # Reinicia o contador quando encontramos propriedades
                        batch_properties.extend(properties)
                
                # Envia as páginas restantes para este lote, se necessário
                while batch_page_count < batch_size:
                    if max_pages and page > max_pages:
                        break# Tipos de propriedades disponíveis no site DF Imóveis

                        
                    print(f"Raspando a página {page}...")
                    future = executor.submit(self.scrape_page, page)
                    page += 1
                    batch_page_count += 1
                    
                    properties, status_code = future.result()
                    if status_code == 204:  # Sem conteúdo, mas sucesso
                        empty_in_batch += 1
                        empty_page_count += 1
                        if empty_page_count >= consecutive_empty_pages_threshold:
                            print(f"Encontradas {consecutive_empty_pages_threshold} páginas vazias consecutivas. Assumindo fim dos resultados.")
                            return all_properties
                    elif status_code != 200:
                        print(f"Erro ao acessar página. Status code: {status_code}")
                    else:  # 200 with properties
                        empty_page_count = 0  # Reset counter
                        batch_properties.extend(properties)
            
            # Adiciona propriedades do lote ao total
            batch_property_count = len(batch_properties)
            all_properties.extend(batch_properties)
            
            # Relatório de status para este lote
            print(f"\n--- Batch {current_batch} completed ---")
            print(f"Pages processed: {batch_page_count}")
            print(f"Empty pages: {empty_in_batch}")
            print(f"Properties found: {batch_property_count}")
            print(f"Total properties so far: {len(all_properties)}")
            
            # Se atingimos max_pages, pare
            if max_pages and page > max_pages:
                print(f"Atingido o número máximo de páginas: {max_pages}")
                break
            
            # Salva dados após cada lote concluído, se solicitado
            if save_each_batch and batch_properties and output_dir:
                print(f"Saving data from batch {current_batch}...")
                # Processa dados do lote
                batch_data_handler = DataHandler(batch_properties)
                batch_df = batch_data_handler.create_dataframe(category)
                
                # Usa nomenclatura de arquivo simplificada - um arquivo por tipo de contrato (venda/aluguel)
                excel_filename = f'imoveis_df_{category}.xlsx'
                tsv_filename = f'imoveis_df_{category}.tsv'
                
                # Salva com append=True para continuar adicionando aos mesmos arquivos
                batch_data_handler.save_to_excel(batch_df, excel_filename, output_dir=output_dir, append=append)
                batch_data_handler.save_to_tsv(batch_df, tsv_filename, output_dir=output_dir, append=append)
                
                print(f"Batch {current_batch} data for {property_type} saved to {output_dir}/{excel_filename} and {output_dir}/{tsv_filename}")
            
            # Faz uma pausa mais longa entre lotes
            actual_delay = batch_delay + random.uniform(-5, 5)  # Adiciona alguma aleatoriedade
            print(f"Pausando por {actual_delay:.1f} segundos antes do próximo lote...")
            time.sleep(actual_delay)
            current_batch += 1
            
        print(f"\nRaspagem concluída. Total de propriedades coletadas: {len(all_properties)}")
        return all_properties
