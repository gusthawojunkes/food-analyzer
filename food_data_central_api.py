import requests
from translator import Translator

PT_BR = "pt-BR"
EN_US = "en-US"

translator = Translator()

class FDCAPI:
    def __init__(self, host, api_key):
        self.host = host
        self.api_key = api_key
    
    def request(self, endpoint, body = {}, request_type = 'GET'):
        response = None
        url = f"{self.host}/{endpoint}?api_key={self.api_key}"
        print(f"[{request_type}] Requesting to: {url}")
        headers = None

        if request_type == 'GET':
            response = requests.get(url)
        elif request_type == 'POST':
            headers = {"Content-Type": "application/json"}
            response = requests.post(url, json=body, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            print(response.json())
            print(f"Status code: {response.status_code}")

    """
    Criteria schema
    {
        "query": "Cheddar cheese",
        "dataType": [
            "Foundation",
            "SR Legacy"
        ],
        "pageSize": 25,
        "pageNumber": 2,
        "sortBy": "dataType.keyword",
        "sortOrder": "asc",
        "brandOwner": "Kar Nut Products Company",
        "tradeChannel": [
            "“CHILD_NUTRITION_FOOD_PROGRAMS”",
            "“GROCERY”"
        ],
        "startDate": "2021-01-01",
        "endDate": "2021-12-30"
    }
    """
    def search_food_by_criteria(self, criteria = {}, translations = None):
        founded = []
        response = self.request('v1/foods/list', body = criteria, request_type = 'POST')
        for row in response:
            description = row['description']
            translated_description = self.find_translation(description, {
                "from": EN_US,
                "to": PT_BR,
                "translations": translations
            })

            key = f"{description}|{EN_US}=>{PT_BR}"
            if key not in translations: translations[key] = translated_description

            row['description'] = translated_description

            for nutrient in row['foodNutrients']:
                nutrient_name = nutrient['name']
                translated_nutrient = self.find_translation(nutrient_name, {
                    "from": EN_US,
                    "to": PT_BR,
                    "translations": translations
                })

                key = f"{nutrient_name}|{EN_US}=>{PT_BR}"
                if key not in translations: translations[key] = translated_nutrient

                nutrient['name'] = translated_nutrient

            founded.append(row)

        return { "rows": founded, "translations": translations }


    def find_translation(self, text, params = {}):
        language_from = params['from'] or EN_US
        language_to = params['to'] or PT_BR
        translations = params['translations'] or {}
        key = f"{text}|{language_from}=>{language_to}"

        if (key in translations): return translations[key]

        return translator.perform(text, params)
