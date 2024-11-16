from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as bs
import pandas as pd
import time

def scrape_netimoveis(url, tipo_transacao, total_pages):
    dados = []
    
    # Inicia o driver
    driver.get(url)
    time.sleep(5)
    
    for n in range(1, total_pages + 1):
        print(f"Navegando na página {n} de {total_pages} para {tipo_transacao}...")
        
        # Atualiza o BeautifulSoup com a nova página
        page_source = driver.page_source
        soup = bs(page_source, 'html.parser')
        imoveis = soup.find_all("section", class_='imovel-info')

        for imovel in imoveis:
            descricao = imovel.select_one("h2").text.strip() if imovel.select_one("h2") else ""
            address = imovel.select_one("div.endereco").text.strip() if imovel.select_one("div.endereco") else ""
            m2 = imovel.select_one("div.caracteristica.area").text.split()[0] if imovel.select_one("div.caracteristica.area") else ""
            bedroom = imovel.select_one("div.caracteristica.quartos").text.split()[0] if imovel.select_one("div.caracteristica.quartos") else ""
            vagas_estacionameto = imovel.select_one("div.caracteristica.vagas").text.split()[0] if imovel.select_one("div.caracteristica.vagas") else ""
            bathroom = imovel.select_one("div.caracteristica.banheiros").text.split()[0] if imovel.select_one("div.caracteristica.banheiros") else ""
            price = imovel.select_one("div.valor").text.split()[1] if imovel.select_one("div.valor") else ""

            # Adiciona os dados ao DataFrame com o tipo de transação
            dados.append({
                "Descrição": descricao,
                "Endereço": address,
                "Área (m²)": m2,
                "Quartos": bedroom,
                "Banheiros": bathroom,
                "Vagas": vagas_estacionameto,
                "Preço": price,
                "Tipo Transação": tipo_transacao
            })

        # Tenta clicar no botão "Próximo" para ir para a próxima página, se não for a última página
        if n < total_pages:
            try:
                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'next') and contains(@class, 'page-link') and text()='Próximo']"))
                )
                driver.execute_script("arguments[0].scrollIntoView(true);", next_button)  # Role até o botão
                time.sleep(1)  # Pequena pausa para garantir visibilidade
                next_button.click()  # Clicar diretamente no botão
                time.sleep(5)  # Aguarde o carregamento da próxima página
            except Exception as e:
                print(f"Erro ao clicar no botão 'Próxima página' na página {n}: {e}")
                break

    return pd.DataFrame(dados)

# Configurações do WebDriver
chrome_options = Options()
# chrome_options.add_argument("--headless")  # Descomente para executar no modo headless
driver_path = r'C:\Users\Felipe Loureiro\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe'
service = Service(driver_path)
driver = webdriver.Chrome(service=service)

# URL para venda e aluguel
url_venda = "https://www.netimoveis.com/venda/distrito-federal/brasilia?transacao=venda&localizacao=BR-DF-brasilia---&pagina=1"
url_aluguel = "https://www.netimoveis.com/aluguel/distrito-federal/brasilia?transacao=aluguel&localizacao=BR-DF-brasilia---&pagina=1"

# Captura o número total de páginas para venda
driver.get(url_venda)
time.sleep(5)
soup = bs(driver.page_source, 'html.parser')
total_pages_venda = int(soup.find_all("a", class_="page-link")[-2].text)

# Captura o número total de páginas para aluguel
driver.get(url_aluguel)
time.sleep(5)
soup = bs(driver.page_source, 'html.parser')
total_pages_aluguel = int(soup.find_all("a", class_="page-link")[-2].text)

# Scraping para venda e aluguel
df_venda = scrape_netimoveis(url_venda, "Venda", total_pages_venda)
df_aluguel = scrape_netimoveis(url_aluguel, "Aluguel", total_pages_aluguel)

# Combinar os dados de venda e aluguel em um único DataFrame
df_final = pd.concat([df_venda, df_aluguel], ignore_index=True).drop_duplicates()

# Salvar os dados no CSV
df_final.to_csv("imoveis_netimoveis.csv", index=False, encoding="utf-8-sig")
print("Dados salvos no arquivo 'imoveis_netimoveis.csv'.")

driver.quit()