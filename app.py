import os
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from food_data_central_api import FDCAPI

load_dotenv()

fdc_api = FDCAPI(os.environ.get('BASE_URL'), os.environ.get('API_KEY'))

app = Flask(__name__, static_url_path='/static')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/search', methods=['POST'])
def search():
    criteria = request.get_json()
    print(criteria)
    return fdc_api.search_food_by_criteria(criteria)

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

