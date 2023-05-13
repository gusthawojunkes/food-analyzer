import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from food_data_central_api import FDCAPI

load_dotenv()

fdc_api = FDCAPI(os.environ.get('BASE_URL'), os.environ.get('API_KEY'))

app = Flask(__name__)

@app.route('/')
def index():
    return fdc_api.request('v1/foods/list')

@app.route('/search', methods=['POST'])
def search():
    criteria = request.get_json()
    return fdc_api.search_food_by_criteria(criteria)