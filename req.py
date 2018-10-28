import json
import requests
from urllib.parse import quote

filters = [{
    "or": [
        {
            "name": "num_quizzes",
            "op": "eq",
            "val": 0
        }, {
            "name": "quizzes",
            "op": "any",
            "val": {
                "name": "id",
                "op": "neq",
                "val": 1
            }
        }
    ]
}]

filters = [{
    "name": "id",
    "op": "in",
    "val": [1, 3, 5, 7, 9]
}]

url = 'http://localhost:5000/api/question'
headers = {'Content-Type': 'application/json'}
params = dict(q=json.dumps(dict(filters=filters)))

response = requests.delete(url, params=params, headers=headers)
assert response.status_code == 200

j = response.json()
try:
    print([x.get('id') for x in j['objects']])
    print(j['num_results'], 'results')
except KeyError:
    print(j)
