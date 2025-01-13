import os
import importlib.util
from pathlib import Path
from typing import List, Dict, Any

class Scraper:
    def __init__(self, scraper_path: str, data_variable: str):
        self.scraper_path = scraper_path
        self.data_variable = data_variable

    def import_scraper(self) -> Any:
        module_name = self.scraper_path.split('.')[-1]
        module_path = Path(self.scraper_path.replace('.', '/'))
        spec = importlib.util.spec_from_file_location(module_name, module_path.with_suffix('.py'))
        scraper_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(scraper_module)
        return scraper_module

    def run(self) -> Any:
        scraper_module = self.import_scraper()
        scraper_function = getattr(scraper_module, self.scraper_path.split('.')[-1])  # Nome da função
        scraped_data = scraper_function()  # Executa a função de scraping
        return getattr(scraper_module, self.data_variable)  # Retorna a variável com os dados


class ScraperOrchestrator:
    def __init__(self, scraper_info: List[Dict[str, str]]):
        self.scraper_info = scraper_info
        self.all_properties = []

    def run_all_scrapers(self) -> List[Dict[str, Any]]:
        for scraper in self.scraper_info:
            print(f"Iniciando scraping em {scraper['path']}...")
            scraper_instance = Scraper(scraper['path'], scraper['data'])
            scrape_data = scraper_instance.run()
            self.all_properties.extend(scrape_data)  # Adiciona os dados coletados

        print(f"Scraping concluído. {len(self.all_properties)} imóveis coletados.")
        return self.all_properties


scraper_info = [
    {"path": "scripts.df-imoveis", "data": "property_data"},
    {"path": "scripts.net-imoveis", "data": "property_data"},
    {"path": "scripts.quinto-andar", "data": "property_data"},
    {"path": "scripts.viva-real", "data": "property_data"},
    {"path": "scripts.zap-imoveis", "data": "property_data"},
    {"path": "scripts.w-imoveis", "data": "property_data"},
]


def all_scraped_data(scraper_info: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    orchestrator = ScraperOrchestrator(scraper_info)
    all_property_data = orchestrator.run_all_scrapers()
    return all_property_data
