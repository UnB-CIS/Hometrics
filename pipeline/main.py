from database.connection import MongoDBConnection
from database.repository import Property
from database.config import DB_URI
from pipeline.data_scraping import ScraperOrchestrator
import os

def insert_data(uri=DB_URI):
    connection = MongoDBConnection(uri)
    client = connection.connect()
    property_manager = Property(client)

    inserted_ids = property_manager.insert_multiple_properties(test_data)
    print(f"Properties inserted with IDs: {inserted_ids}")

    connection.close()

    return inserted_ids

def run_scrapers(output_dir="dataset/v01"):
    """Run all scrapers and save data to the specified output directory."""
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # Define scraper configurations for full scraping (no page limits)
    scraper_configs = [
        {
            'name': 'df_imoveis_aluguel',
            'module_path': 'scripts.df-imoveis.scrapings.scrapping_df_imoveis',
            'function_name': 'run_scraper',
            'params': {
                'category': 'aluguel',
                'max_pages': None,  # Run until completion
                'workers': 5
            }
        },
        {
            'name': 'df_imoveis_venda',
            'module_path': 'scripts.df-imoveis.scrapings.scrapping_df_imoveis',
            'function_name': 'run_scraper',
            'params': {
                'category': 'venda',
                'max_pages': None,  # Run until completion
                'workers': 5
            }
        },
        {
            'name': 'net_imoveis_aluguel',
            'module_path': 'scripts.net-imoveis.scrapping_Netimoveis',
            'function_name': 'run_scraper',
            'params': {
                'category': 'aluguel',
                'max_pages': None,  # Run until completion
                'workers': 5
            }
        },
        {
            'name': 'net_imoveis_venda',
            'module_path': 'scripts.net-imoveis.scrapping_Netimoveis',
            'function_name': 'run_scraper',
            'params': {
                'category': 'venda',
                'max_pages': None,  # Run until completion
                'workers': 5
            }
        },
    ]
    
    # Initialize and run the orchestrator
    orchestrator = ScraperOrchestrator(scraper_configs, output_dir=output_dir, append=True)
    property_data = orchestrator.run_all_scrapers()
    
    print(f"Scraping completed. Data saved to {output_dir}")
    return property_data

def main():
    # Step 1: Scrape data using the orchestrator
    run_scrapers(output_dir="dataset/v01")
    
    # The following steps are commented out until we integrate the scraped data properly
    # with the data processing pipeline
    
    # # Step 2: Clean data
    # cleaner = DataCleaner(scraped_data)
    # standard_keys = ["state", "city", "description", "type", "price", "size", "bedrooms", "car_spaces"]
    # cleaned_data = cleaner.clean_data(standard_keys)
    # 
    # # Step 3: Transform data
    # transformer = DataTransformer(cleaned_data)
    # transformed_data = transformer.transform_data()
    # 
    # # Step 4: Insert data into MongoDB
    # connection = MongoDBConnection(DB_URI)
    # client = connection.connect()
    # property_manager = Property(client)
    # property_manager.insert_multiple_properties(transformed_data)
    # connection.close()


if __name__ == "__main__":
    main()
