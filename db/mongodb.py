from pymongo import MongoClient
from datetime import datetime
import os

# Environment variables for secure credentials
DB_USER = os.environ['MONGO_DB_USER']
DB_PASSWORD = os.environ['MONGO_DB_PASS']
DB_CLUSTER = 'cluster0.mhq2j'
DB_URI = f"mongodb+srv://{DB_USER}:{DB_PASSWORD}@{DB_CLUSTER}.mongodb.net/"

class MongoDBConnection:
    def __init__(self, uri=DB_URI):
        self.uri = uri
        self.client = None

    def connect(self):
        """Connect to MongoDB."""
        self.client = MongoClient(self.uri)
        return self.client

    def close(self):
        """Close the MongoDB connection."""
        if self.client:
            self.client.close()

class Property:
    def __init__(self, client):
        self.client = client
        self.db = self.client.housingprices
        self.property_listings = self.db.property_listings

    def insert_property(self, data):
        """Insert a single property record."""
        data['timestamp'] = datetime.now()
        return self.property_listings.insert_one(data).inserted_id

    def insert_multiple_properties(self, properties_list):
        """Insert multiple property records with timestamps."""
        for property_data in properties_list:
            property_data['timestamp'] = datetime.now()
        result = self.property_listings.insert_many(properties_list)
        return result.inserted_ids

# Example usage:
if __name__ == "__main__":
    # Connect to MongoDB
    connection = MongoDBConnection()
    client = connection.connect()

    # Create Property object
    property_manager = Property(client)

    # Sample property data
    test_data = [
        {
            "state": "DF",
            "city": "Brasília",
            "description": "SHS Quadra 06 Conjunto A Bloco D, ASA SUL, BRASILIA",
            "type": "Aluguel Loja 86 m²",
            "price": 10.285,
            "size": 86,
            "bedrooms": None,
            "cars_spaces": None,
        },
        {
            "state": "SP",
            "city": "São Paulo",
            "description": "Av. Paulista, Bela Vista",
            "type": "Venda Apartamento 120 m²",
            "price": 1.250,
            "size": 120,
            "bedrooms": 3,
            "cars_spaces": 2,
        },
        {
            "state": "RJ",
            "city": "Rio de Janeiro",
            "description": "Rua Barata Ribeiro, Copacabana",
            "type": "Venda Apartamento 80 m²",
            "price": 900,
            "size": 80,
            "bedrooms": 2,
            "cars_spaces": 1,
        }
    ]

    # Insert multiple properties and print inserted IDs
    inserted_ids = property_manager.insert_multiple_properties(test_data)
    print(f"Properties inserted with IDs: {inserted_ids}")

    # Close the connection
    connection.close()
