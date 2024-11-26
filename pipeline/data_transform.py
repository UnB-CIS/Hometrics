from typing import List, Dict, Any

class DataTransformer:
    def __init__(self, data: List[Dict[str, Any]]):
        self.data = data

    def transform_price(self) -> None:
        for d in self.data:
            if 'price' in d and isinstance(d['price'], (int, str)):
                d['price'] = float(d['price'])

    def transform_size(self) -> None:
        for d in self.data:
            if 'size' in d and isinstance(d['size'], str):
                try:
                    d['size'] = int(d['size'])
                except ValueError:
                    d['size'] = None

    def transform_bedrooms(self) -> None:
        for d in self.data:
            if 'bedrooms' in d and isinstance(d['bedrooms'], str):
                try:
                    d['bedrooms'] = int(d['bedrooms'])
                except ValueError:
                    d['bedrooms'] = None

    def transform_car_spaces(self) -> None:
        for d in self.data:
            if 'car_spaces' in d and isinstance(d['car_spaces'], str):
                try:
                    d['car_spaces'] = int(d['car_spaces'])
                except ValueError:
                    d['car_spaces'] = None

    def normalize_state(self) -> None:
        state_mapping = {
            "AC": "Acre",
            "AL": "Alagoas",
            "AP": "Amapá",
            "AM": "Amazonas",
            "BA": "Bahia",
            "CE": "Ceará",
            "DF": "Distrito Federal",
            "ES": "Espírito Santo",
            "GO": "Goiás",
            "MA": "Maranhão",
            "MT": "Mato Grosso",
            "MS": "Mato Grosso do Sul",
            "MG": "Minas Gerais",
            "PA": "Pará",
            "PB": "Paraíba",
            "PR": "Paraná",
            "PE": "Pernambuco",
            "PI": "Piauí",
            "RJ": "Rio de Janeiro",
            "RN": "Rio Grande do Norte",
            "RS": "Rio Grande do Sul",
            "RO": "Rondônia",
            "RR": "Roraima",
            "SC": "Santa Catarina",
            "SP": "São Paulo",
            "SE": "Sergipe",
            "TO": "Tocantins"
        }

        for d in self.data:
            if 'state' in d and d['state'] in state_mapping:
                d['state'] = state_mapping[d['state']]

    def normalize_city(self) -> None:
        for d in self.data:
            if 'city' in d:
                d['city'] = d['city'].title()

    def normalize_description(self) -> None:
        for d in self.data:
            if 'description' in d:
                d['description'] = d['description'].strip().capitalize()

    def transform_data(self) -> List[Dict[str, Any]]:
        self.transform_price()
        self.transform_size()
        self.transform_bedrooms()
        self.transform_car_spaces()
        self.normalize_state()
        self.normalize_city()
        self.normalize_description()
        return self.data


# data = [
#     {
#         "state": "Rio de Janeiro",
#         "city": "Rio de Janeiro",
#         "description": "Rua Barata Ribeiro, Copacabana",
#         "type": "Venda Apartamento 80 m²",
#         "price": "900",
#         "size": "80",
#         "bedrooms": "2",
#         "car_spaces": "1",
#     }
# ]

# transformer = DataTransformer(data)
# transformed_data = transformer.transform_data()

# print(transformed_data)