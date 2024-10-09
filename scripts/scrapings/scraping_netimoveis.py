from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from bs4 import BeautifulSoup as bs


# Config chrome com webdriver manager
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")


service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

num_page = 3
URL = "https://www.netimoveis.com/venda/distrito-federal/brasilia?transacao=venda&localizacao=BR-DF-brasilia---&pagina=2"
driver.get(URL)
page_source = driver.page_source

soup = bs(page_source, 'html.parser')


imovel = soup.select_one("section.imovel-info")

descricao = imovel.select_one("h2").text.split()
address = imovel.select_one("div.endereco").text
m2 = imovel.select_one("div.caracteristica.area").text.split()
bedroom = imovel.select_one("div.caracteristica.quartos").text.split()
vagas_estacionameto = imovel.select_one("div.caracteristica.vagas").text.split()
bathroom = imovel.select_one("div.caracteristica.banheiros").text.split()
price = imovel.select_one("div.valor").text.split()

print(f"""
      {descricao}
      {address}
      {m2}
      {bedroom}
      {bathroom}
      {vagas_estacionameto}
      {price}
      """)
driver.quit()
