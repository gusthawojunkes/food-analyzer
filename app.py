import os
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from food_data_central_api import FDCAPI
from translator import Translator
from custom_decorators import CachedRoute
from flask_caching import Cache
import base64
import datetime;
import shutil
import sys

from algorithm.algorithm import predict

PT_BR = "pt-BR"
EN_US = "en-US"

load_dotenv()

fdc_api = FDCAPI(os.environ.get('BASE_URL'), os.environ.get('API_KEY'))
translator = Translator()
translations = {}

app = Flask(__name__, static_url_path='/static')
cache = Cache(app)
app.config['CACHE_TYPE'] = 'simple'
app.config['CACHE_DEFAULT_TIMEOUT'] = (60 * 30)
cached_route = CachedRoute(app).cached_route

@app.route('/')
def index():
    return render_template('index.html')

@cached_route()
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

    return rows[0]

"""
{
    image: "data:image/png;base64,........"
}
"""
@app.route('/api/algorithm', methods=['POST'])
def algorithm():
    try:
        name_image = ''
        
        body = request.get_json()
        image = body['image'][22:]

        time_stamp = datetime.datetime.now().timestamp()
        path = f"algorithm/predict/{str(time_stamp)}"

        file_directory = f"{path}/"
        os.mkdir(file_directory)

        image_directory = f"{path}/img/"
        os.mkdir(image_directory)

        try:
            predict_file = f"{image_directory}/predict.jpg"
            decoded_data = base64.b64decode((image))
        except:
            return ''

        try:
            predicted_image = open(predict_file, 'wb')
            predicted_image.write(decoded_data)
            predicted_image.close()
        except:
            return ''

        name_image = predict(str(time_stamp))
    except NameError:
        name_image = ''
    
    delete_dir(predict_file, file_directory, image_directory)
    
    return { 'name': name_image }

def delete_dir(predict_file ,file_directory, image_directory):
    if os.path.exists(predict_file):
        os.remove(predict_file)
        os.rmdir(image_directory)
        os.rmdir(file_directory)

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