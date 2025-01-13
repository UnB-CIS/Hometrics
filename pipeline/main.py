from database.connection import MongoDBConnection
from database.repository import Property
from database.config import DB_URI
from pipeline import scrape_data
from pipeline import DataCleaner
from pipeline import DataTransformer

test_data = [
        {
            "state": "DF",
            "city": "Brasília",
            "description": "SHS Quadra 06 Conjunto A Bloco D, ASA SUL, BRASILIA",
            "type": "Aluguel Loja 86 m²",
            "price": 10.285,
            "size": 86,
            "bedrooms": None,
            "car_spaces": None,
        },
        {
            "state": "SP",
            "city": "São Paulo",
            "description": "Av. Paulista, Bela Vista",
            "type": "Venda Apartamento 120 m²",
            "price": 1.250,
            "size": 120,
            "bedrooms": 3,
            "car_spaces": 2,
        },
        {
            "state": "RJ",
            "city": "Rio de Janeiro",
            "description": "Rua Barata Ribeiro, Copacabana",
            "type": "Venda Apartamento 80 m²",
            "price": 900,
            "size": 80,
            "bedrooms": 2,
            "car_spaces": 1,
        }
    ]


def insert_data(uri=DB_URI):
    connection = MongoDBConnection(uri)
    client = connection.connect()
    property_manager = Property(client)

    inserted_ids = property_manager.insert_multiple_properties(test_data)
    print(f"Properties inserted with IDs: {inserted_ids}")

    connection.close()

    return inserted_ids


def main():
    while True:
        # Step 1: Scrape data
        scraped_data = scrape_data()
        
        # Step 2: Clean data
        cleaner = DataCleaner(scraped_data)
        standard_keys = ["state", "city", "description", "type", "price", "size", "bedrooms", "car_spaces"]
        cleaned_data = cleaner.clean_data(standard_keys)
        
        # Step 3: Transform data
        transformer = DataTransformer(cleaned_data)
        transformed_data = transformer.transform_data()
        
        # Step 4: Insert data into MongoDB
        connection = MongoDBConnection(DB_URI)
        client = connection.connect()
        property_manager = Property(client)
        property_manager.insert_multiple_properties(transformed_data)
        connection.close()


if __name__ == "__main__":
    main()
