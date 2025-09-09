"""
Country configurations for Wilo website
"""

COUNTRIES = {
    'germany': {
        'name': 'Deutschland',
        'code': 'DE',
        'language': 'German',
        'hydraulic_pump_text': 'Hydraulische Pumpenauswahl',
        'url_params': {'country': 'de', 'lang': 'de'}
    },
    'austria': {
        'name': 'Österreich', 
        'code': 'AT',
        'language': 'German',
        'hydraulic_pump_text': 'Hydraulische Pumpenauswahl',
        'url_params': {'country': 'at', 'lang': 'de'}
    },
    'france': {
        'name': 'France',
        'code': 'FR', 
        'language': 'French',
        'hydraulic_pump_text': 'Sélection de pompes hydrauliques',
        'url_params': {'country': 'fr', 'lang': 'fr'}
    },
    'italy': {
        'name': 'Italia',
        'code': 'IT',
        'language': 'Italian', 
        'hydraulic_pump_text': 'Selezione pompe idrauliche',
        'url_params': {'country': 'it', 'lang': 'it'}
    },
    'spain': {
        'name': 'España',
        'code': 'ES',
        'language': 'Spanish',
        'hydraulic_pump_text': 'Selección de bombas hidráulicas',
        'url_params': {'country': 'es', 'lang': 'es'}
    },
    'netherlands': {
        'name': 'Nederland',
        'code': 'NL',
        'language': 'Dutch',
        'hydraulic_pump_text': 'Hydraulische pompselectie',
        'url_params': {'country': 'nl', 'lang': 'nl'}
    },
    'poland': {
        'name': 'Polska',
        'code': 'PL',
        'language': 'Polish',
        'hydraulic_pump_text': 'Wybór pomp hydraulicznych',
        'url_params': {'country': 'pl', 'lang': 'pl'}
    },
    'united_kingdom': {
        'name': 'United Kingdom',
        'code': 'GB', 
        'language': 'English',
        'hydraulic_pump_text': 'Hydraulic pump selection',
        'url_params': {'country': 'gb', 'lang': 'en'}
    }
}

def get_country_config(country_key):
    """Get configuration for specific country"""
    return COUNTRIES.get(country_key.lower())

def get_all_countries():
    """Get list of all supported countries"""
    return list(COUNTRIES.keys())

def get_country_by_name(country_name):
    """Get country data by display name"""
    for key, data in COUNTRIES.items():
        if data['name'] == country_name:
            return key, data
    return None, None
