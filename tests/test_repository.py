import pytest
from database.connection import MongoDBConnection
from database.repository import Property
from database.config import DB_URI

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
    ]


def test_valid_insertion(uri=DB_URI,test_data=test_data):
    """ This test will pass if MDB_URI is set to a valid connection string. """
    connection = MongoDBConnection(uri)
    client = connection.connect()
    property_manager = Property(client)
    inserted_data = property_manager.insert_multiple_properties(test_data)


    print(f"test_valid_insertion: Properties inserted with IDs: {inserted_data}")
    connection.close()

    assert inserted_data is not None

