from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time



# Função para extrair os dados dos imóveis na página atual
def extrair_dados():
    anuncios = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, 'property-card__container'))
    )

    # Extraia informações de cada anúncio
    for anuncio in anuncios:
        try:
            titulo = anuncio.find_element(By.CLASS_NAME, 'property-card__title').text
        except:
            titulo = 'N/A'

        try:
            preco = anuncio.find_element(By.CLASS_NAME, 'property-card__price').text
        except:
            preco = 'N/A'

        try:
            endereco = anuncio.find_element(By.CLASS_NAME, 'property-card__address').text
        except:
            endereco = 'N/A'

        # Pegue informações adicionais como área, quartos, banheiros e vagas
        try:
            area = anuncio.find_element(By.CLASS_NAME, 'property-card__detail-area').text
        except:
            area = 'N/A'

        try:
            quartos = anuncio.find_element(By.XPATH, ".//ul[@class='property-card__details']/li[1]").text
        except:
            quartos = 'N/A'

        try:
            banheiros = anuncio.find_element(By.XPATH, ".//ul[@class='property-card__details']/li[2]").text
        except:
            banheiros = 'N/A'

        try:
            vagas = anuncio.find_element(By.XPATH, ".//ul[@class='property-card__details']/li[3]").text
        except:
            vagas = 'N/A'

        # Pegue as amenidades, se houver
        try:
            amenidades = anuncio.find_element(By.CLASS_NAME, 'property-card__amenities').text
        except:
            amenidades = 'N/A'

        # Adicione os dados a uma lista
        dados_imoveis.append({
            'Título': titulo,
            'Preço': preco,
            'Endereço': endereco,
            'Área': area,
            'Quartos': quartos,
            'Banheiros': banheiros,
            'Vagas': vagas,
            'Amenidades': amenidades})
        print(len(dados_imoveis))


def definir_ranges_vivareal(preco_inferior=1,preco_superior=250000):
    # Defina o caminho para o ChromeDriver
    driver_path = r'C:\Users\Felipe Loureiro\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe'
    service = Service(driver_path)
    # Inicialize o Chrome usando o serviço
    driver = webdriver.Chrome(service=service)
    url = 'https://www.vivareal.com.br/venda/distrito-federal/brasilia/#onde=Brasil,Distrito%20Federal,Bras%C3%ADlia,,,,,,BR%3EDistrito%20Federal%3ENULL%3EBrasilia,,,&preco-desde=1'
    driver.get(url)
    total = int(WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'results-summary__count'))).text.replace('.', ''))
    ranges = []
    totais_ranges = 0
    while totais_ranges < 0.995*total:
        url = f'https://www.vivareal.com.br/venda/distrito-federal/brasilia/#onde=Brasil,Distrito%20Federal,Bras%C3%ADlia,,,,,,BR%3EDistrito%20Federal%3ENULL%3EBrasilia,,,&preco-ate={preco_superior}&preco-desde={preco_inferior}'
        print(f'Novo url é: {url}')
        time.sleep(10)
        driver.get(url)
        time.sleep(10)
        total_range_atual = int(WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'results-summary__count'))).text.replace('.', ''))
        if total_range_atual > 9950:
            preco_superior = int((preco_superior + preco_inferior)/2)
            print(f'{[preco_inferior,preco_superior]} tem {total_range_atual}')
        else: 
            ranges.append([preco_inferior,preco_superior])
            print(f'{[preco_inferior,preco_superior]} tem {total_range_atual}, adicionando à lista')
            preco_inferior=preco_superior+1
            preco_superior=preco_superior*2
            totais_ranges=totais_ranges+total_range_atual



    
    driver.quit()
    return ranges

ranges = definir_ranges_vivareal()
print(ranges)

# Crie uma lista para armazenar os dados dos imóveis
dados_imoveis = []


for rangezinho in ranges:
    # Defina o caminho para o ChromeDriver
    if rangezinho != ranges[0]:
        driver.quit()
    driver_path = r'C:\Users\Felipe Loureiro\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe'
    service = Service(driver_path)
    
    # Inicialize o Chrome
    driver = webdriver.Chrome(service=service)
    preco_superior = rangezinho[1]
    preco_inferior = rangezinho[0]
    # Abra a página 
    url = f'https://www.vivareal.com.br/venda/distrito-federal/brasilia/#onde=Brasil,Distrito%20Federal,Bras%C3%ADlia,,,,,,BR%3EDistrito%20Federal%3ENULL%3EBrasilia,,,&preco-ate={preco_superior}&preco-desde={preco_inferior}'
    time.sleep(6)
    driver.get(url)
    time.sleep(6)
    # Determine o número total de imóveis e o número de imóveis por página
    total_imoveis = int(WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'results-summary__count'))
    ).text.replace('.', ''))
    
    imoveis_por_pagina = 36  # Geralmente 36 imóveis por página no Viva Real
    # Calcule o número total de páginas a serem percorridas
    total_paginas = (total_imoveis // imoveis_por_pagina) + (1 if total_imoveis % imoveis_por_pagina != 0 else 0)
    print(f'total de imoveis: {total_imoveis} e total de paginas:{total_paginas }')
    # Loop para navegar por todas as páginas
    for pagina in range(total_paginas):
        # Extrair dados da página atual
        extrair_dados()
        print(f'Extraída a pagina {pagina}')
        if pagina < total_paginas - 1:
            try:
                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@class='js-change-page' and @title='Próxima página']"))
                )
                driver.execute_script("arguments[0].scrollIntoView();", next_button)  # Role até o botão
                driver.execute_script("arguments[0].click();", next_button)  # Use JavaScript para clicar
                time.sleep(6)  # Aguarde o carregamento da próxima página
            except:
                # Se não houver mais o botão de "Próxima Página", encerre o loop
                print('caiu aqui')
                break
        else:
            break

# Crie um DataFrame com os dados coletados
df_imoveis = pd.DataFrame(dados_imoveis)

# Feche o navegador

driver.quit()

# Salve o DataFrame em um arquivo CSV
df_imoveis.to_csv('imoveis_brasilia_approch_precos.csv', index=False)

# Defina o caminho para o ChromeDriver
driver_path = r'C:\Users\Felipe Loureiro\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe'
service = Service(driver_path)

# Inicialize o Chrome usando o serviço
driver = webdriver.Chrome(service=service)

# Abra a página inicial
url = 'https://www.vivareal.com.br/aluguel/distrito-federal/brasilia/#onde=Brasil,Distrito%20Federal,Bras%C3%ADlia,,,,,,BR%3EDistrito%20Federal%3ENULL%3EBrasilia,,,'
driver.get(url)

# Crie uma lista para armazenar os dados dos imóveis
dados_imoveis = []


# Determine o número total de imóveis e o número de imóveis por página
total_imoveis = int(WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, 'results-summary__count'))
).text.replace('.', ''))

imoveis_por_pagina = 36  # Geralmente 36 imóveis por página no Viva Real

# Calcule o número total de páginas a serem percorridas
total_paginas = (total_imoveis // imoveis_por_pagina) + (1 if total_imoveis % imoveis_por_pagina != 0 else 0)

url_antigo = []

# Loop para navegar por todas as páginas
for pagina in range(total_paginas):
    # Extrair dados da página atual
    extrair_dados()
    # Tente encontrar o botão de "Próxima Página" e clique, exceto na última página
    if pagina < total_paginas - 1:
        try:
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@class='js-change-page' and @title='Próxima página']"))
            )
            driver.execute_script("arguments[0].scrollIntoView();", next_button)  # Role até o botão
            driver.execute_script("arguments[0].click();", next_button)  # Use JavaScript para clicar
            time.sleep(6)  # Aguarde o carregamento da próxima página
        except:
            # Se não houver mais o botão de "Próxima Página", encerre o loop
            print('caiu aqui')
            break

# Crie um DataFrame com os dados coletados
df_imoveis = pd.DataFrame(dados_imoveis)

# Feche o navegador

driver.quit()

# Exiba o DataFrame

# Salve o DataFrame em um arquivo CSV
df_imoveis.to_csv('alugueis_viva_real.csv', index=False)

# Carregar o CSV como um DataFrame
venda = pd.read_csv('imoveis_brasilia_approch_precos.csv')

# Remover duplicatas
venda = venda.drop_duplicates()

aluguel = pd.read_csv('imoveis_brasilia_aluguel.csv')

aluguel = aluguel.drop_duplicates()

# Adicionar a coluna "tipo" no DataFrame de venda
venda['tipo'] = 'venda'

# Adicionar a coluna "tipo" no DataFrame de aluguel
aluguel['tipo'] = 'aluguel'

# Concatenar os DataFrames
df_combinado = pd.concat([venda, aluguel], ignore_index=True)

df_combinado.to_csv('viva_real.csv', index=False)