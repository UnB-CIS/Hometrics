from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as bs
import pandas as pd
import time
import concurrent.futures
import threading
from utils.data_handler import DataHandler

def scrape_page(driver, url, tipo_transacao, page_number, property_type=None):
    """
    Raspa dados de imóveis de uma única página.
    """
    try:
        # Construir URL para a página específica
        page_url = url.replace("pagina=1", f"pagina={page_number}")
        
        try:
            # Navegar para a página
            driver.get(page_url)
        except Exception as e:
            print(f"Erro ao acessar a página {page_number}: {str(e)}")
            return [], 500  # Erro de conexão
        
        # Aguardar mais tempo para garantir que os templates JavaScript sejam renderizados
        time.sleep(8)  # Aumentar tempo de espera
        
        # Verificar se a página foi completamente carregada
        page_ready = False
        max_attempts = 3  # Reduzido para 3 tentativas
        attempt = 0
        
        while not page_ready and attempt < max_attempts:
            try:
                # Verificar se ainda existem templates não renderizados no HTML
                page_source = driver.page_source
                if '{{' in page_source and '}}' in page_source:
                    print(f"Página {page_number} ainda tem templates não renderizados. Aguardando...")
                    time.sleep(5)  # Aumentar tempo de espera
                    driver.refresh()  # Tentar recarregar a página
                    time.sleep(3)    # Aguardar após o refresh
                    attempt += 1
                else:
                    page_ready = True
            except Exception as e:
                print(f"Erro ao verificar templates na página {page_number}: {str(e)}")
                attempt += 1
                time.sleep(3)
        
        print(f"Raspando página {page_number} para {tipo_transacao}...")
        
        # Extrair dados da página
        page_source = driver.page_source
        soup = bs(page_source, 'html.parser')
        imoveis = soup.find_all("section", class_='imovel-info')
        
        dados = []
        for imovel in imoveis:
            try:
                # Clean up description text - remove newlines and excess whitespace
                descricao_raw = imovel.select_one("h2").text if imovel.select_one("h2") else ""
                # More thorough cleaning with regex
                if descricao_raw:
                    import re
                    # Replace line breaks and tabs with spaces
                    descricao = re.sub(r'[\n\t\r]+', ' ', descricao_raw)
                    # Replace multiple spaces with a single space
                    descricao = re.sub(r'\s+', ' ', descricao)
                    # Final strip to remove any leading/trailing spaces
                    descricao = descricao.strip()
                else:
                    descricao = ""
                address = imovel.select_one("div.endereco").text.strip() if imovel.select_one("div.endereco") else ""
                m2 = imovel.select_one("div.caracteristica.area").text.split()[0] if imovel.select_one("div.caracteristica.area") else ""
                bedroom = imovel.select_one("div.caracteristica.quartos").text.split()[0] if imovel.select_one("div.caracteristica.quartos") else ""
                vagas_estacionameto = imovel.select_one("div.caracteristica.vagas").text.split()[0] if imovel.select_one("div.caracteristica.vagas") else ""
                bathroom = imovel.select_one("div.caracteristica.banheiros").text.split()[0] if imovel.select_one("div.caracteristica.banheiros") else ""
                price = imovel.select_one("div.valor").text.split()[1] if imovel.select_one("div.valor") else ""
                
                # Verificar se há algum template não renderizado nos dados
                property_data = {
                    "description": descricao,
                    "address": address,
                    "property_type": property_type if property_type else '',
                    "price": price,
                    "size": m2,
                    "bedrooms": bedroom,
                    "bathrooms": bathroom,
                    "parking_spaces": vagas_estacionameto,
                    "contract_type": tipo_transacao
                }
                
                # Verificar por templates não renderizados
                has_template = False
                for key, value in property_data.items():
                    if isinstance(value, str) and ('{{' in value or '}}' in value):
                        has_template = True
                        print(f"Pulando imóvel com templates não renderizados na página {page_number}")
                        break
                
                # Só adicionar dados sem templates
                if not has_template:
                    dados.append(property_data)
            except Exception as e:
                print(f"Erro ao extrair dados do imóvel na página {page_number}: {e}")
        
        return dados, 200  # Status 200 indica sucesso
    
    except Exception as e:
        print(f"Erro ao raspar a página {page_number}: {e}")
        return [], 500  # Status 500 indica erro no scraping


def scrape_netimoveis(url, tipo_transacao, total_pages, workers=5, batch_size=None, batch_delay=None, output_dir=None, append=False, custom_output_files=None, property_type=None):
    """
    Raspa dados de imóveis de múltiplas páginas usando threads paralelas.
    """
    # Thread-local storage para os drivers de cada thread
    thread_local = threading.local()
    
    def get_driver():
        """Retorna um driver para a thread atual ou cria um novo se necessário."""
        if not hasattr(thread_local, 'driver'):
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            # Block analytics and non-essential requests
            chrome_options.add_argument('--block-new-web-contents')
            chrome_options.add_argument('--disable-notifications')
            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
            # Block third-party requests including analytics
            chrome_options.add_argument('--host-resolver-rules=MAP *.plausible.io 127.0.0.1')
            thread_local.driver = webdriver.Chrome(options=chrome_options)
        return thread_local.driver
    
    # Função para scrape com o driver da thread
    def scrape_with_local_driver(page_number):
        driver = get_driver()
        return scrape_page(driver, url, tipo_transacao, page_number, property_type)
    
    # Função para salvar os dados após cada lote
    def save_batch_data(batch_properties):
        if not batch_properties or output_dir is None:
            return None
            
        # Usar o DataHandler para salvar os dados do lote
        data_handler = DataHandler(batch_properties)
        
        # Criar DataFrame com a coluna 'contract_type'
        batch_df = data_handler.create_dataframe(tipo_transacao.lower())
        
        # Verificar se há arquivos personalizados definidos
        if custom_output_files and 'excel_path' in custom_output_files and 'tsv_path' in custom_output_files:
            # Usar caminhos personalizados (orquestrador)
            excel_path = custom_output_files['excel_path']
            tsv_path = custom_output_files['tsv_path']
            
            # Salvar diretamente nos caminhos personalizados
            data_handler.save_to_excel(batch_df, excel_path, append=True)  # Sempre append=True para lotes
            data_handler.save_to_tsv(batch_df, tsv_path, append=True)  # Sempre append=True para lotes
            
            print(f"Batch data saved to {excel_path} and {tsv_path}")
        else:
            # Usar o transaction type e property_type para o prefixo de arquivo
            if property_type:
                file_prefix = f'imoveis_netimoveis_{tipo_transacao.lower()}_{property_type}'
            else:
                file_prefix = f'imoveis_netimoveis_{tipo_transacao.lower()}'
            
            # Salvar em Excel
            excel_filename = f'{file_prefix}.xlsx'
            data_handler.save_to_excel(batch_df, excel_filename, output_dir=output_dir, append=True)  # Sempre append=True para lotes
            
            # Salvar em CSV
            csv_filename = f'{file_prefix}.csv'
            data_handler.save_to_csv(batch_df, csv_filename, output_dir=output_dir, append=True)  # Sempre append=True para lotes
            
            print(f"Batch data saved to {output_dir}/{excel_filename} and {output_dir}/{csv_filename}")
            
        return batch_df
    
    all_properties = []
    page = 1
    continue_scraping = True
    
    # Determinar o tamanho do lote, usar workers como padrão se batch_size não for fornecido
    actual_batch_size = batch_size if batch_size else workers
    
    # Inicializar o DataFrame final
    final_df = None
    
    # Se append=False, limpar os arquivos existentes antes de começar
    if output_dir is not None and not append:
        # Criar um DataHandler vazio apenas para limpar os arquivos
        empty_handler = DataHandler([])
        empty_df = empty_handler.create_dataframe(tipo_transacao.lower())
        
        if custom_output_files and 'excel_path' in custom_output_files and 'tsv_path' in custom_output_files:
            # Limpar arquivos personalizados
            empty_handler.save_to_excel(empty_df, custom_output_files['excel_path'], append=False)
            empty_handler.save_to_tsv(empty_df, custom_output_files['tsv_path'], append=False)
        else:
            # Limpar arquivos padrão
            if property_type:
                file_prefix = f'imoveis_netimoveis_{tipo_transacao.lower()}_{property_type}'
            else:
                file_prefix = f'imoveis_netimoveis_{tipo_transacao.lower()}'
            
            excel_filename = f'{file_prefix}.xlsx'
            csv_filename = f'{file_prefix}.csv'
            
            empty_handler.save_to_excel(empty_df, excel_filename, output_dir=output_dir, append=False)
            empty_handler.save_to_csv(empty_df, csv_filename, output_dir=output_dir, append=False)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        while continue_scraping and page <= total_pages:
            futures = []
            current_batch_start = page
            batch_properties = []
            
            # Submit batch of pages to the executor
            for i in range(min(actual_batch_size, total_pages - page + 1)):
                if page > total_pages:
                    break
                futures.append(executor.submit(scrape_with_local_driver, page))
                page += 1
            
            # Process results as they complete
            for future in concurrent.futures.as_completed(futures):
                properties, status_code = future.result()
                if status_code == 200 and properties:
                    batch_properties.extend(properties)
                    all_properties.extend(properties)
                    print(f"Obtidos {len(properties)} imóveis. Total até agora: {len(all_properties)}")
                else:
                    print(f"Falha ao obter dados. Status code: {status_code}")
            
            # Salvar os dados do lote atual
            if batch_properties and output_dir is not None:
                current_batch_end = page - 1
                print(f"Salvando dados do lote: páginas {current_batch_start}-{current_batch_end}...")
                batch_df = save_batch_data(batch_properties)
                
                # Atualizar o DataFrame final
                if final_df is None:
                    final_df = batch_df
                elif batch_df is not None:
                    final_df = pd.concat([final_df, batch_df], ignore_index=True)
            
            # Se ainda houver mais páginas para processar e batch_delay for especificado, espere entre lotes
            if page <= total_pages and batch_delay:
                current_batch_end = page - 1
                print(f"Lote processado: páginas {current_batch_start}-{current_batch_end}. Aguardando {batch_delay} segundos antes do próximo lote...")
                time.sleep(batch_delay)
            else:
                # Aguardar um pouco entre lotes para não sobrecarregar o servidor
                time.sleep(1)
    
    # Fechar todos os drivers
    for thread in threading.enumerate():
        if hasattr(thread_local, 'driver'):
            thread_local.driver.quit()
    
    # Se não temos um DataFrame final ainda, criar um a partir de all_properties
    if final_df is None and all_properties:
        data_handler = DataHandler(all_properties)
        final_df = data_handler.create_dataframe(tipo_transacao.lower())
    
    # Retornar o DataFrame final ou um DataFrame vazio
    return final_df if final_df is not None else pd.DataFrame(all_properties)

def run_scraper(contract_type='venda', property_type=None, max_pages=None, workers=5, batch_size=None, batch_delay=None, output_dir=None, append=False, custom_output_files=None):
    """
    Run the Net Imoveis scraper with the specified parameters.
    """
    # Inicializar driver temporário para descobrir o número total de páginas
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    # Block analytics and non-essential requests
    chrome_options.add_argument('--block-new-web-contents')
    chrome_options.add_argument('--disable-notifications')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    # Block third-party requests including analytics
    chrome_options.add_argument('--host-resolver-rules=MAP *.plausible.io 127.0.0.1')
    temp_driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Available property types
        PROPERTY_TYPES = [
            "apartamento",
            "casa",
            "flat"
        ]
        
        # Validate property_type if provided
        if property_type and property_type not in PROPERTY_TYPES:
            print(f"Warning: '{property_type}' is not a recognized property type. Using default URL without property type filter.")
            property_type = None
            
        # URL base de acordo com o tipo de contrato e tipo de propriedade
        if contract_type.lower() == 'aluguel':
            # For rental properties, the URL uses "locacao" instead of "aluguel"
            url_transacao = "locacao"
            param_transacao = "locacao"
            transacao = "aluguel"  # Keep this as aluguel for consistency with the rest of the code
        else:  # venda por padrão
            url_transacao = "venda"
            param_transacao = "venda"
            transacao = "venda"
            
        # Construct the URL based on whether property_type is provided
        if property_type:
            url = f"https://www.netimoveis.com/{url_transacao}/distrito-federal/brasilia/{property_type}?transacao={param_transacao}&localizacao=BR-DF-brasilia---&tipo={property_type}&pagina=1"
        else:
            url = f"https://www.netimoveis.com/{url_transacao}/distrito-federal/brasilia?transacao={param_transacao}&localizacao=BR-DF-brasilia---&pagina=1"
        
        # Detectar o número total de páginas
        temp_driver.get(url)
        time.sleep(3)
        soup = bs(temp_driver.page_source, 'html.parser')
        try:
            total_pages = int(soup.find_all("a", class_="page-link")[-2].text)
            print(f"Total de páginas detectadas para {transacao}: {total_pages}")
        except Exception as e:
            print(f"Erro ao detectar o número total de páginas: {e}")
            total_pages = 10  # Valor padrão se não conseguir detectar
            
        # Limitar o número de páginas se max_pages for especificado
        if max_pages and max_pages < total_pages:
            total_pages = max_pages
            print(f"Limitando a {total_pages} páginas.")
            
        # Executar scraping com múltiplas threads
        df = scrape_netimoveis(
            url=url,
            tipo_transacao=transacao,
            total_pages=total_pages,
            workers=workers,
            batch_size=batch_size,
            batch_delay=batch_delay,
            output_dir=output_dir,
            append=append,
            custom_output_files=custom_output_files,
            property_type=property_type
        )
        
        return df
        
    finally:
        # Fechar o driver temporário
        temp_driver.quit()

def run_all_scrapers(output_dir="scripts/net-imoveis/data", max_pages=None, workers=5, batch_size=50, batch_delay=20, append=True):
    """Run scrapers for all combinations of contract types and property types.
    Saves consolidated data files for each contract type with all property types included.
    """
    # Contract types available
    contract_types = ['venda', 'aluguel']
    
    # Property types to scrape
    property_types = [
        'apartamento',
        'casa',
        'flat'
        # Add other property types as needed
    ]
    
    # Common parameters for all scrapers
    # No output_dir for individual scrapers since we'll handle consolidated output
    common_params = {
        'max_pages': max_pages,
        'workers': workers,
        'batch_size': batch_size,
        'batch_delay': batch_delay,
        'append': False  # Don't append to individual files
    }
    
    # Dictionaries to hold all DataFrames by contract type
    consolidated_dfs = {
        'venda': [],
        'aluguel': []
    }
    
    # Run all combinations of contract types and property types
    for contract_type in contract_types:
        for property_type in property_types:
            print(f"\nIniciando scraping para {contract_type} de {property_type}...")
            
            # Run the scraper without saving to files (set output_dir to None)
            df = run_scraper(
                contract_type=contract_type,
                property_type=property_type,
                output_dir=None,  # Don't save individual files
                **common_params
            )
            
            # Add the DataFrame to the appropriate consolidated list
            if df is not None and not df.empty:
                consolidated_dfs[contract_type].append(df)
                print(f"Added {len(df)} rows from {property_type} to consolidated {contract_type} data")
    
    # Process and save consolidated data for each contract type
    for contract_type, df_list in consolidated_dfs.items():
        if df_list:
            # Concatenate all DataFrames for this contract type
            full_df = pd.concat(df_list, ignore_index=True)
            print(f"\nConsolidated {contract_type} data has {len(full_df)} total rows")
            
            # Create filenames for consolidated data
            excel_filename = f'imoveis_netimoveis_{contract_type}_all.xlsx'
            csv_filename = f'imoveis_netimoveis_{contract_type}_all.csv'
            
            # Create a data handler for the consolidated data
            data_handler = DataHandler([])
            
            # Initialize output files if not appending
            if not append:
                # Create empty files to clear any existing data
                empty_df = pd.DataFrame()
                data_handler.save_to_excel(empty_df, excel_filename, output_dir=output_dir, append=False)
                data_handler.save_to_csv(empty_df, csv_filename, output_dir=output_dir, append=False)
            
            # Save the consolidated data
            data_handler.save_to_excel(full_df, excel_filename, output_dir=output_dir, append=append)
            data_handler.save_to_csv(full_df, csv_filename, output_dir=output_dir, append=append)
            
            print(f"Saved consolidated {contract_type} data to {output_dir}/{excel_filename} and {output_dir}/{csv_filename}")
    
    return consolidated_dfs

# Apenas executa se for rodado diretamente (não como módulo)
if __name__ == "__main__":
    # Example usage when running the script directly
    print("Iniciando scraping do NetImóveis para todas as combinações")
    
    # Option 1: Run scraper for a single contract type and property type
    # df = run_scraper(
    #     contract_type='venda',
    #     property_type='apartamento',
    #     max_pages=300,
    #     workers=5,
    #     output_dir="scripts/net-imoveis/data",
    #     batch_size=40,
    #     batch_delay=10,
    #     append=True
    # )
    
    # Option 2: Run for all combinations of contract types and property types
    results = run_all_scrapers(
        output_dir="scripts/net-imoveis/data",
        max_pages=30,  
        workers=3,       
        batch_size=30,   
        batch_delay=30,  
        append=True
    )
    
    print("Scraping do NetImóveis para todas as combinações concluído com sucesso!")