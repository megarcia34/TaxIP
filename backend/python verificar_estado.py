
import requests
import json

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyMGRmNTkyZC00N2MwLTRiN2YtODg4MS1iMjUwZDdlMWFjNzEiLCJ0aXBvIjoiY2hvZmVyIiwiY29udHJvbF9iYXNlX2lkIjoiOTVkZDQyNWQtNTg0MC00ZGVkLWE4MzgtMmNjZDBlYWQwZTBiIiwiZXhwIjoxNzg4MzQ2NzExLCJ0eXBlIjoiYWNjZXNzIn0.cTJUYw6sWfVmraghFDdvcS9EUg4TuRlzLJTkzcPSeD8"

url = "http://localhost:8000/api/chofer/registro-progresivo/estado-expediente"
headers = {"Authorization": f"Bearer {token}"}

response = requests.get(url, headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")
