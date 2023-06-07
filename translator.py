import requests

"""
https://mymemory.translated.net/doc/spec.php
"""
class Translator:
    def __init__(self, host = "https://api.mymemory.translated.net", api_key = ""):
        self.host = host
        self.api_key = api_key

    def perform(self, text, params = {}):
        lang_from = params['from']
        lang_to = params['to']
        #query_string = f"q={text}&langPair={lang_from}|{lang_to}" error test
        query_string = f"q={text}&langpair={lang_from}|{lang_to}"
        response = self.request('get', request_type='GET', query_string=query_string)
        return response['responseData']['translatedText']


    def request(self, endpoint, request_type = 'GET', query_string = "", body = {}):
        response = None
        if (query_string is not None) and query_string != "":
            query_string = f"?{query_string}"

        url = f"{self.host}/{endpoint}{query_string}"
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

