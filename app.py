import os
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from food_data_central_api import FDCAPI

load_dotenv()

fdc_api = FDCAPI(os.environ.get('BASE_URL'), os.environ.get('API_KEY'))

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    criteria = request.get_json()
    return fdc_api.search_food_by_criteria(criteria)

"""
{
    image: "data:image/png;base64,........"
}
"""
@app.route('/algorithm', methods=['POST'])
def algorithm():
    body = request.get_json()
    image = body.image
    return image;