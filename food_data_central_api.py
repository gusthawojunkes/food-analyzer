import requests

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
            print(f"Headers: {headers}")
            print(f"Body: {body}")
            response = requests.post(url, json=body, headers=headers)

        if response.status_code == 200:
            data = response.json()
            size = len(data)
            print(f"Found {size} registers")
            return data
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
    def search_food_by_criteria(self, criteria = {}):
        return self.request('v1/foods/list', body = criteria, request_type = 'POST')
