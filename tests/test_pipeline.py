from database.connection import MongoDBConnection
from database.repository import Property
from database.config import DB_URI
from scripts.df_imoveis.scrapings.scrapping_df_imoveis import properties_data

def insert_scraped_data(uri=DB_URI):
    connection = MongoDBConnection(uri)
    client = connection.connect()
    property_manager = Property(client)

    inserted_ids = property_manager.insert_multiple_properties(properties_data)
    print(f"Properties inserted with IDs: {inserted_ids}")

    connection.close()

    return inserted_ids

if __name__ == "__main__":
    insert_scraped_data()

