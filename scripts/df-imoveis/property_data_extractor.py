import re
from scraping_utils import get_text_or_none, get_link_or_none, extract_numeric_value, PROPERTY_TYPES

class PropertyDataExtractor:
    """ Classe responsável por extrair dados estruturados de elementos HTML de propriedades """
    
    def __init__(self, property_type="imoveis"):
        """Inicializa com o tipo de propriedade para contexto"""
        self.property_type = property_type

    def extract_property_data(self, property_soup):
        """Extrai dados relevantes de um elemento HTML de propriedade. """

        address = get_text_or_none(property_soup, 'h2.new-title.phrase')
        link = "https://www.dfimoveis.com.br" + (get_link_or_none(property_soup, 'h2.new-title.phrase') or "")
        
        property_type = self.property_type
        
        price_raw = get_text_or_none(property_soup, 'div.new-price span')
        price = self._extract_price(price_raw)
        
        size_m2_element = property_soup.find('span', string=lambda x: x and "m²" in x)
        size_m2_raw = size_m2_element.get_text(strip=True) if size_m2_element else None
        size_m2 = extract_numeric_value(size_m2_raw, allow_float=True, handle_range=True)
        
        bedroom_element = property_soup.find('span', string=lambda x: x and re.search(r'\b(quartos?|Quartos?)\b', x))
        bedroom_raw = bedroom_element.get_text(strip=True) if bedroom_element else None
        bedroom = extract_numeric_value(bedroom_raw, allow_float=False, handle_range=True)
        
        parking_element = property_soup.find('span', string=lambda x: x and re.search(r'\b(vagas?|Vagas?)\b', x))
        parking_raw = parking_element.get_text(strip=True) if parking_element else None
        parking = extract_numeric_value(parking_raw, allow_float=False, handle_range=True)
        
        property_data = {
            'page_link': link,
            'address': address,
            'property_type': property_type,
            'price': price,
            'size_m2': size_m2,
            'bedroom': bedroom,
            'parking_spaces': parking,
        }
        
        return property_data
        
    def _extract_price(self, price_raw):
        """ Extrai valor numérico de preço do texto bruto. """

        price = None
        if price_raw:
            if 'Sob Consulta' in price_raw:
                price = ''
            else:
                return extract_numeric_value(price_raw, allow_float=True, handle_range=False)
        
        return price
