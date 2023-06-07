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
    
    translated_food = translator.perform(food, {
        "from": PT_BR,
        "to": EN_US
    })

    criteria['query'] = translated_food

    return fdc_api.search_food_by_criteria(criteria)[0]

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


if __name__ == "__main__":
    app.run(host='0.0.0.0')

