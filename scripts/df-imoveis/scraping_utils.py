import re

def get_text_or_none(element, selector):
    """ Extrai texto de um elemento usando um seletor CSS. """

    selected_element = element.select_one(selector)
    return selected_element.get_text(strip=True) if selected_element else None

def get_link_or_none(element, selector):
    """ Extrai href de um elemento usando um seletor CSS. """

    selected_element = element.select_one(selector)
    if selected_element:
        if selected_element.name == 'a':
            return selected_element.get('href')
        parent_link = selected_element.find_parent('a')
        if parent_link:
            return parent_link.get('href')
        child_link = selected_element.find('a')
        if child_link:
            return child_link.get('href')
    return None

def extract_numeric_value(text, allow_float=True, handle_range=True):
    """ Extrai valor numérico do texto. """
    if not text:
        return None
    
    # Trata intervalos como "2 a 3" pegando o primeiro valor
    if handle_range and 'a' in text:
        text = text.split('a')[0].strip()
    
    # Extrai a parte numérica
    pattern = r'(\d+(?:[.,]\d+)?)' if allow_float else r'(\d+)'
    numeric_match = re.search(pattern, text)
    
    if numeric_match:
        value = numeric_match.group(1)
        if allow_float:
            # Substitui vírgula por ponto para valores decimais
            value = value.replace('.', '').replace(',', '.')
            try:
                return float(value)
            except:
                return text
        else:
            try:
                return int(value)
            except:
                return text
    return text if text else None

# Constantes
PROPERTY_TYPES = [
    "apartamento",
    "casa",
    "casa-condominio",
    "galpao",
    "garagem", 
    "hotel-flat",
    "kitnet",
    "loja",
    "lote",
    "loteamento",
    "ponto-comercial",
    "predio",
    "rural",
    "sala"
]
