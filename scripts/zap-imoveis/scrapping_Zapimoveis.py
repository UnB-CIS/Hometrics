from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
import time

# Configurações do Selenium
chrome_options = Options()
'''chrome_options.add_argument("--headless")  # Executa o Chrome no modo headless
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")'''
driver_path = r'C:\Users\Felipe Loureiro\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe'  # Atualize o caminho para o chromedriver
service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

BASE_URL = 'https://www.zapimoveis.com.br/venda/apartamentos/df+brasilia/?transacao=venda&onde=,Distrito%20Federal,Bras%C3%ADlia,,,,,city,BR%3EDistrito%20Federal%3ENULL%3EBrasilia,-15.826691,-47.92182,&tipos=apartamento_residencial,studio_residencial,kitnet_residencial,casa_residencial,sobrado_residencial,condominio_residencial,casa-vila_residencial,cobertura_residencial,flat_residencial,loft_residencial&itl_id=1000072&itl_name=zap_-_botao-cta_buscar_to_zap_resultado-pesquisa'

# Abrindo a página
driver.get(BASE_URL)

# Função para extrair dados dos imóveis
def extrair_dados():
    imoveis = driver.find_elements(By.CLASS_NAME, 'ListingCard_result-card__Pumtx')
    dados_imoveis = []
    
    for imovel in imoveis:
        try:
            descricao = imovel.find_element(By.CLASS_NAME, 'ListingCard_card__description__slBTG').text
        except:
            descricao = None
        
        try:
            preco = imovel.find_element(By.CSS_SELECTOR, 'p[data-cy="rp-cardProperty-price-txt"]').text
        except:
            preco = None
        
        try:
            area = imovel.find_element(By.CSS_SELECTOR, 'p[data-cy="rp-cardProperty-propertyArea-txt"]').text
        except:
            area = None
        
        try:
            quartos = imovel.find_element(By.CSS_SELECTOR, 'p[data-cy="rp-cardProperty-bedroomQuantity-txt"]').text
        except:
            quartos = None
        
        try:
            banheiros = imovel.find_element(By.CSS_SELECTOR, 'p[data-cy="rp-cardProperty-bathroomQuantity-txt"]').text
        except:
            banheiros = None
        
        try:
            vagas = imovel.find_element(By.CSS_SELECTOR, 'p[data-cy="rp-cardProperty-parkingSpacesQuantity-txt"]').text
        except:
            vagas = None
        
        try:
            endereco = imovel.find_element(By.CSS_SELECTOR, 'h2[data-cy="rp-cardProperty-location-txt"]').text
        except:
            endereco = None

        try:
            cond_iptu = imovel.find_element(By.CSS_SELECTOR, 'p.text-balance').text
        except:
            cond_iptu = None

        dados_imoveis.append({
            'Descrição': descricao,
            'Preço': preco,
            'Área': area,
            'Quartos': quartos,
            'Banheiros': banheiros,
            'Vagas': vagas,
            'Endereço': endereco,
            'Condomínio e IPTU': cond_iptu
        })

    return dados_imoveis

# Lista para armazenar os dados de todos os imóveis
todos_dados_imoveis = []
scroll_increment = 500  # Quantidade para cada rolagem
scroll_total = 0  # Acumulador de rolagem para cada página
target_total = 5000  # Alvo global de imóveis para coleta
max_scroll_per_page = 40000  # Limite de rolagem por página antes de mudar para a próxima página

# Loop principal para coletar imóveis até atingir o limite global
while len(todos_dados_imoveis) < target_total:
    


    # Rolagem contínua até atingir o limite de 40.000 por página
    while scroll_total < max_scroll_per_page:
        driver.execute_script(f"window.scrollBy(0, {scroll_increment});")
        scroll_total += scroll_increment
        #time.sleep(0.5)
        # Extrair dados da página atual
        dados_pagina = extrair_dados()
        todos_dados_imoveis.extend(dados_pagina)
        todos_dados_imoveis = list({frozenset(item.items()): item for item in todos_dados_imoveis}.values())  # Remove duplicatas globais
        print(f"Total de imóveis coletados até agora: {len(todos_dados_imoveis)} / {target_total}")
    # Resetando o contador de scroll e tentando avançar para a próxima página
    scroll_total = 0
    try:
        next_button = driver.find_element(By.CSS_SELECTOR, 'button[data-testid="next-page"]')
        if next_button.is_enabled():
            driver.execute_script("arguments[0].click();", next_button)
            time.sleep(3)  # Pequena pausa para carregamento da próxima página
    except Exception as e:
        print("Não foi possível encontrar ou clicar no botão 'Próxima página'.", e)
        break

# Fecha o navegador
driver.quit()

# Cria o DataFrame e salva os dados
df_imoveis = pd.DataFrame(todos_dados_imoveis).drop_duplicates()
df_imoveis.to_csv('imoveis_zap.csv', index=False, encoding='utf-8-sig')
print(f"Dados salvos em 'imoveis_zap.csv' com {len(df_imoveis)} registros.")