import re
from time import sleep

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

options = Options()
options.add_argument('window-size=1400,925')
# options.add_argument('--headless')

def extract_value_text(element):
    valor = re.search(r"\d+\.?\d*", element)
    return valor.group() if valor else None

def extract_size_text(element):
    size = re.search(r"\d+\s*m²", element)
    return size.group() if size else None

def extract_rooms_text(element):
    rooms = re.search(r"\d+\s*[Qq]uartos?", element)
    return rooms.group() if rooms else None

def extract_parking_text(element):
    parking = re.search(r"(\d+|0)\s*[Vv]agas?", element)
    return parking.group() if parking else "0 vaga"

def extract_type_text(element):
    house_type = re.search(r'\b(apartamento|casa|studio|kitnet)\b', element, re.IGNORECASE)
    return house_type.group() if house_type else None

def extract_property_data(valor, size, rooms, parking, house_type, description):
    return {
        'description': description,
        'type': house_type,
        'price': valor,
        'size': size,
        'bedrooms': rooms,
        'car_spaces': parking
    }

navegador = webdriver.Chrome(options=options)
navegador.get('https://www.quintoandar.com.br/alugar/imovel/brasilia-df-brasil?pagina=')

data_list = []

# Clicar no botão "Ver mais" até que não esteja mais disponível
while True:
    try:
        # Espera até que o botão "Ver mais" esteja clicável
        button = WebDriverWait(navegador, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Ver mais']"))
        )
        button.click()
        sleep(3)  # Aguarde um pouco para garantir que os novos imóveis sejam carregados

    except Exception as e:
        print("Botão 'Ver mais' não está mais disponível ou erro:", e)
        break

# Após clicar em "Ver mais" até o fim, agora raspamos todos os imóveis
WebDriverWait(navegador, 10).until(
    EC.presence_of_element_located((By.XPATH, "//div[@aria-live='polite']"))
)

page_content = navegador.page_source
site = BeautifulSoup(page_content, 'html.parser')

# Agora raspamos todos os imóveis que foram carregados na página
properties = site.find_all('div', attrs={'role': 'presentation', 'class': 'Cozy__CardRow-Container oVdjIf'})

for property_card in properties:
    # Extraindo dados de cada imóvel
    valor = extract_value_text(property_card.find('h3').text) if property_card.find('h3') else None
    size = extract_size_text(property_card.text)  # Buscando no texto completo do card
    description = property_card.find('h2').text if property_card.find('h2') else None
    house_type = extract_type_text(description) if description else None
    rooms = extract_rooms_text(description) if description else None
    parking = extract_parking_text(description) if description else None

    property_data = extract_property_data(valor, size, rooms, parking, house_type, description)
    data_list.append(property_data)

navegador.quit()

# Criar um DataFrame e salvar em um arquivo CSV
df = pd.DataFrame(data_list)
df.to_csv('imoveis_brasilia2.csv', index=False, encoding='utf-8-sig')
print("Dados salvos em 'imoveis_brasilia.csv'")