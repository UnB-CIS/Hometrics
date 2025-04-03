from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as bs
import pandas as pd
import time
import concurrent.futures
import threading
from utils.data_handler import DataHandler

def scrape_page(driver, url, tipo_transacao, page_number):
    """
    Raspa dados de imóveis de uma única página.
    """
    try:
        # Construir URL para a página específica
        page_url = url.replace("pagina=1", f"pagina={page_number}")
        
        # Navegar para a página
        driver.get(page_url)
        
        # Aguardar mais tempo para garantir que os templates JavaScript sejam renderizados
        time.sleep(5)  # Aumentar tempo de espera
        
        # Verificar se a página foi completamente carregada
        page_ready = False
        max_attempts = 5  # Aumentar o número de tentativas
        attempt = 0
        
        while not page_ready and attempt < max_attempts:
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
                descricao = " ".join(descricao_raw.split())
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
                    "type": '',
                    "price": price,
                    "size": m2,
                    "bedrooms": bedroom,
                    "bathrooms": bathroom,
                    "parking_spaces": vagas_estacionameto,
                    "category": tipo_transacao
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


def scrape_netimoveis(url, tipo_transacao, total_pages, workers=5, output_dir=None, append=False, custom_output_files=None):
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
            thread_local.driver = webdriver.Chrome(options=chrome_options)
        return thread_local.driver
    
    # Função para scrape com o driver da thread
    def scrape_with_local_driver(page_number):
        driver = get_driver()
        return scrape_page(driver, url, tipo_transacao, page_number)
    
    all_properties = []
    page = 1
    continue_scraping = True
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        while continue_scraping and page <= total_pages:
            futures = []
            
            # Submit batch of pages to the executor
            for i in range(workers):
                if page > total_pages:
                    break
                futures.append(executor.submit(scrape_with_local_driver, page))
                page += 1
            
            # Process results as they complete
            for future in concurrent.futures.as_completed(futures):
                properties, status_code = future.result()
                if status_code == 200 and properties:
                    all_properties.extend(properties)
                    print(f"Obtidos {len(properties)} imóveis. Total até agora: {len(all_properties)}")
                else:
                    print(f"Falha ao obter dados. Status code: {status_code}")
            
            # Aguardar um pouco entre lotes para não sobrecarregar o servidor
            time.sleep(1)
    
    # Fechar todos os drivers
    for thread in threading.enumerate():
        if hasattr(thread_local, 'driver'):
            thread_local.driver.quit()
    
    # Salvar dados se output_dir for especificado
    if output_dir is not None:
        # Usar o DataHandler para salvar os dados
        data_handler = DataHandler(all_properties)
        
        # Criar DataFrame com a coluna 'modo' adicionada (equivalente a 'category' no outro scraper)
        df = data_handler.create_dataframe(tipo_transacao.lower())
        
        # Verificar se há arquivos personalizados definidos
        if custom_output_files and 'excel_path' in custom_output_files and 'csv_path' in custom_output_files:
            # Usar caminhos personalizados (orquestrador)
            excel_path = custom_output_files['excel_path']
            csv_path = custom_output_files['csv_path']
            
            
            # Salvar diretamente nos caminhos personalizados
            data_handler.save_to_excel(df, excel_path, append=append)
            data_handler.save_to_csv(df, csv_path, append=append)
            
            print(f"Excel data saved to {excel_path}")
            print(f"CSV data saved to {csv_path}")
        else:
            # Usar o modo padrão com prefixo de arquivo
            file_prefix = f'imoveis_netimoveis_{tipo_transacao.lower()}'
            
            # Salvar em Excel
            excel_filename = f'{file_prefix}.xlsx'
            data_handler.save_to_excel(df, excel_filename, output_dir=output_dir, append=append)
            
            # Salvar em CSV
            csv_filename = f'{file_prefix}.csv'
            data_handler.save_to_csv(df, csv_filename, output_dir=output_dir, append=append)
            
            print(f"Excel data saved to {output_dir}/{excel_filename}")
            print(f"CSV data saved to {output_dir}/{csv_filename}")
    
    # Make sure we return the DataFrame if output_dir is specified, not None
    return df if 'df' in locals() else pd.DataFrame(all_properties)

def run_scraper(category='venda', max_pages=None, workers=5, output_dir=None, append=False, custom_output_files=None):
    """
    Run the Net Imoveis scraper with the specified parameters.
    
    Args:
        category (str): Type of listings to scrape ('venda' or 'aluguel')
        max_pages (int): Maximum number of pages to scrape
        workers (int): Number of worker threads
        output_dir (str): Directory to save output files
        append (bool): Whether to append to existing files
        custom_output_files (dict): Custom file paths for output (excel_path, csv_path)
    """
    # Inicializar driver temporário para descobrir o número total de páginas
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    temp_driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # URL base de acordo com o modo de busca
        if category.lower() == 'aluguel':
            url = "https://www.netimoveis.com/aluguel/distrito-federal/brasilia?transacao=aluguel&localizacao=BR-DF-brasilia---&pagina=1"
            transacao = "Aluguel"
        else:  # venda por padrão
            url = "https://www.netimoveis.com/venda/distrito-federal/brasilia?transacao=venda&localizacao=BR-DF-brasilia---&pagina=1"
            transacao = "venda"
        
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
            output_dir=output_dir,
            append=append,
            custom_output_files=custom_output_files
        )
        
        return df
        
    finally:
        # Fechar o driver temporário
        temp_driver.quit()

# Apenas executa se for rodado diretamente (não como módulo)
if __name__ == "__main__":
    # Executar o scraper de venda e aluguel
    print("Iniciando scraping do NetImóveis")
    
    # Diretório para salvar os dados
    output_dir = "scripts/net-imoveis/data"
    
    # Executar scraper de venda
    df_venda = run_scraper(
        category='venda',
        max_pages=10,  # Limite para teste, use None para todas as páginas
        workers=5,
        output_dir=output_dir,
        append=True
    )
    
    # Executar scraper de aluguel
    df_aluguel = run_scraper(
        category='aluguel',
        max_pages=10,  # Limite para teste, use None para todas as páginas
        workers=5,
        output_dir=output_dir,
        append=True
    )
    
    print("Scraping do NetImóveis concluído com sucesso!")