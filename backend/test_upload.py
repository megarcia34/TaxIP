import requests
import sys

# Token del usuario
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyMGRmNTkyZC00N2MwLTRiN2YtODg4MS1iMjUwZDdlMWFjNzEiLCJ0aXBvIjoiY2hvZmVyIiwiY29udHJvbF9iYXNlX2lkIjoiOTVkZDQyNWQtNTg0MC00ZGVkLWE4MzgtMmNjZDBlYWQwZTBiIiwiZXhwIjoxNzg4MzQ2NzExLCJ0eXBlIjoiYWNjZXNzIn0.cTJUYw6sWfVmraghFDdvcS9EUg4TuRlzLJTkzcPSeD8"

url = "http://localhost:8000/api/chofer/registro-progresivo/documento"
params = {
    "tipo_documento": "dni"
}

headers = {
    "Authorization": f"Bearer {token}"
}

files = {
    "file": ("foto.jpg", open("C:/temp/foto.jpg", "rb"), "image/jpeg")
}

try:
    response = requests.post(url, params=params, headers=headers, files=files)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")