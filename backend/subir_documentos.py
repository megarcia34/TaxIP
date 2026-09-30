import requests

# Token del usuario
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyMGRmNTkyZC00N2MwLTRiN2YtODg4MS1iMjUwZDdlMWFjNzEiLCJ0aXBvIjoiY2hvZmVyIiwiY29udHJvbF9iYXNlX2lkIjoiOTVkZDQyNWQtNTg0MC00ZGVkLWE4MzgtMmNjZDBlYWQwZTBiIiwiZXhwIjoxNzg4MzQ2NzExLCJ0eXBlIjoiYWNjZXNzIn0.cTJUYw6sWfVmraghFDdvcS9EUg4TuRlzLJTkzcPSeD8"

# URL base
base_url = "http://localhost:8000/api/chofer/registro-progresivo/documento"

# Archivo a subir (la misma imagen para todos)
file_path = "C:/temp/foto.jpg"

# Tipos de documentos a subir
documentos = [
    {"tipo": "licencia", "fecha": "2027-12-31"},
    {"tipo": "sanidad", "fecha": "2027-12-31"},
    {"tipo": "buena_conducta", "fecha": "2027-12-31"}
]

headers = {
    "Authorization": f"Bearer {token}"
}

for doc in documentos:
    params = {
        "tipo_documento": doc["tipo"],
        "fecha_vencimiento": doc["fecha"]
    }
    
    files = {
        "file": ("foto.jpg", open(file_path, "rb"), "image/jpeg")
    }
    
    print(f"📤 Subiendo {doc['tipo']}...")
    
    try:
        response = requests.post(base_url, params=params, headers=headers, files=files)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}\n")
    except Exception as e:
        print(f"Error: {e}\n")