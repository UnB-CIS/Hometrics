from pymongo import MongoClient
from datetime import datetime
import os


print(os.environ['MONGO_DB_USER'])

db_user = os.environ['MONGO_DB_USER']
db_password = os.environ['MONGO_DB_PASS']
db_uri = f"mongodb+srv://{db_user}:{db_password}@cluster0.mhq2j.mongodb.net/"

def connect_to_mongo(uri=db_uri):
    client = MongoClient(uri)
    return client

def insert_property(client, data):
    db = client.housingprices
    property_listings = db.property_listings
    return property_listings.insert_one(data).inserted_id

def insert_multiple_properties(client, properties_list):
    db = client.housingprices
    property_listings = db.property_listings
    # Adicionar timestamp atual a cada propriedade
    for property_data in properties_list:
        property_data['timestamp'] = datetime.now()
    result = property_listings.insert_many(properties_list)
    return result.inserted_ids

client = connect_to_mongo()

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

inserted_ids = insert_multiple_properties(client, test_data)

print(f"Property inserted with ID: {inserted_ids}")
