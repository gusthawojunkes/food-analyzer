import os
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from food_data_central_api import FDCAPI
from translator import Translator
PT_BR = "pt-BR"
EN_US = "en-US"

load_dotenv()

fdc_api = FDCAPI(os.environ.get('BASE_URL'), os.environ.get('API_KEY'))
translator = Translator()
translations = {}

app = Flask(__name__, static_url_path='/static')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/search', methods=['POST'])
def search():
    criteria = request.get_json()
    food = criteria['query']
    if (food is None):
        return jsonify({"error": "No food item specified"})
    
    translated_food = find_translation(food, {
        "from": PT_BR,
        "to": EN_US
    })

    criteria['query'] = translated_food

    response = fdc_api.search_food_by_criteria(criteria, translations)
    rows = response['rows']
    new_translations = response['translations']
    for key in new_translations:
        if key not in translations:
            translations[key] = new_translations[key]

    print(translations)

    return rows[0]

"""
{
    image: "data:image/png;base64,........"
}
"""
@app.route('/api/algorithm', methods=['POST'])
def algorithm():
    body = request.get_json()
    print(body)
    image = body.image
    return image;

def find_translation(food, params = {}):
    language_from = params['from'] or EN_US
    language_to = params['to'] or PT_BR
    key = f"{food}|{language_from}=>{language_to}"

    if (key in translations): return translations[key]

    translated_food = translator.perform(food, params)
    add_new_translation_to_map(key, translated_food)

    return translated_food


def add_new_translation_to_map(key, value): 
    translations[key] = value

if __name__ == "__main__":
    app.run(host='0.0.0.0')