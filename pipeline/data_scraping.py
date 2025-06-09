import os
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd

class ScraperOrchestrator:
    def __init__(self, scraper_configs: List[Dict[str, Any]], output_dir: str = "dataset/test", append: bool = True):
        """
        Initialize the scraper orchestrator with a list of scraper configurations.
        """
        self.scraper_configs = scraper_configs
        self.output_dir = output_dir
        self.append = append
        self.all_properties = []
        
        self.category_files = {
            'aluguel': {
                'excel': os.path.join(output_dir, 'imoveis_aluguel.xlsx'),
                'csv': os.path.join(output_dir, 'imoveis_aluguel.csv')
            },
            'venda': {
                'excel': os.path.join(output_dir, 'imoveis_venda.xlsx'),
                'csv': os.path.join(output_dir, 'imoveis_venda.csv')
            }
        }
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def run_scraper(self, scraper_config: Dict[str, Any]) -> pd.DataFrame:
        """
        Run a scraper based on its configuration.
        """
        name = scraper_config['name']
        module_path = scraper_config['module_path']
        function_name = scraper_config['function_name']
        params = scraper_config.get('params', {})
        
        print(f"Iniciando scraping em {name}...")
        
        module = __import__(module_path, fromlist=[function_name])
        scraper_function = getattr(module, function_name)
        category = params.get('category', '').lower()
        
        custom_output_files = None
        if category in self.category_files:
            custom_output_files = {
                'excel_path': self.category_files[category]['excel'],
                'tsv_path': self.category_files[category]['tsv']
            }
        
        common_params = {
            'output_dir': self.output_dir,
            'append': self.append,
            'custom_output_files': custom_output_files
        }
        
        all_params = {**common_params, **params}
        df = scraper_function(**all_params)
        
        self.all_properties.append({
            'source': name,
            'params': params,
            'data': df
        })
        
        return df

    def run_all_scrapers(self):
        """Run all configured scrapers and return all collected data."""
        for config in self.scraper_configs:
            try:
                self.run_scraper(config)
            except Exception as e:
                print(f"Error running scraper {config['name']}: {str(e)}")
        
        print(f"Scraping concluído. {len(self.all_properties)} conjuntos de dados coletados.")
        return self.all_properties


def main():
    """Main function to run the scraper orchestrator."""
    output_dir = "dataset"
    
    scraper_configs = [
        # DF Imoveis
        # {
        #     'name': 'df_imoveis_aluguel',
        #     'module_path': 'scripts.df-imoveis.scrapings.scrapping_df_imoveis',
        #     'function_name': 'run_scraper',
        #     'params': {
        #         'category': 'aluguel',  # Updated parameter name
        #         'max_pages': 100,  # No limit - will scrape all available pages
        #         'workers': 5,
        #         'batch_size': 50,    # Process in batches of 50 pages
        #         'batch_delay': 20    # Wait 20 seconds between batches
        #     }
        # },
        # {
        #     'name': 'df_imoveis_venda',
        #     'module_path': 'scripts.df-imoveis.scrapings.scrapping_df_imoveis',
        #     'function_name': 'run_scraper',
        #     'params': {
        #         'category': 'venda',  # Updated parameter name
        #         'max_pages': 100,  # No limit - will scrape all available pages
        #         'workers': 5,
        #         'batch_size': 50,    # Process in batches of 50 pages
        #         'batch_delay': 20    # Wait 20 seconds between batches
        #     }
        # },
        # Net Imoveis
        {
            'name': 'net_imoveis_aluguel',
            'module_path': 'scripts.net-imoveis.scrapping_net_imoveis',
            'function_name': 'run_scraper',
            'params': {
                'category': 'aluguel',
                'max_pages': 100,  # No limit - will scrape all available pages
                'workers': 5,
                'batch_size': 50,    # Process in batches of 50 pages
                'batch_delay': 20    # Wait 20 seconds between batches
            }
        },
        {
            'name': 'net_imoveis_venda',
            'module_path': 'scripts.net-imoveis.scrapping_net_imoveis',
            'function_name': 'run_scraper',
            'params': {
                'category': 'venda',
                'max_pages': 100,  # No limit - will scrape all available pages
                'workers': 5,
                'batch_size': 50,    # Process in batches of 50 pages
                'batch_delay': 20    # Wait 20 seconds between batches
            }
        }
    ]
    
    orchestrator = ScraperOrchestrator(
        scraper_configs=scraper_configs,
        output_dir=output_dir,
        append=True
    )
    
    # run all
    all_property_data = orchestrator.run_all_scrapers()
    return all_property_data

# Run the orchestrator if this script is executed directly
if __name__ == "__main__":
    main()

