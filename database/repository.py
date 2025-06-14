from datetime import datetime


class Property:
    def __init__(self, client):
        self.client = client
        self.db = self.client.housingprices
        self.property_listings = self.db.property_listings

    def insert_property(self, property):
        property["timestamp"] = datetime.now()
        return self.property_listings.insert_one(property).inserted_id

    def insert_multiple_properties(self, properties_list):
        for property_data in properties_list:
            property_data["timestamp"] = datetime.now()
        result = self.property_listings.insert_many(properties_list)
        return result.inserted_ids
