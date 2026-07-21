
# Crear el script test_post.py para el usuario
script_content = '''import requests
import json

url = "http://localhost:8000/api/reservas"
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1MmMyMGZlMy1lYjZmLTQ0NzgtYjk4Yy01MmFmMTMyZGM0MDAiLCJlbWFpbCI6InJlY2VwY2lvbmlzdGFAdGVzdC5jb20iLCJ0aXBvIjoiZW1wbGVhZG8iLCJleHAiOjE3ODIzMDQ4OTQsInR5cGUiOiJhY2Nlc3MifQ.cbpdCHJg0bF-YM_iP73B009V0A85mUyFyMG_uGzXl6o"

payload = {
    "empresa_id": "cf750359-d16e-47a7-96be-5e77fd10465f",
    "pasajero_nombre": "Juan Pérez",
    "pasajero_telefono": "+5491123456789",
    "direccion_origen": "Av. Corrientes 1234, Buenos Aires",
    "direccion_destino": "Calle Florida 100, Buenos Aires",
    "tipo_vehiculo": "premium",
    "nota_conductor": "Pasajero con equipaje grande",
    "es_programado": False,
    "metodo_pago": "vehiculo"
}

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

print("Enviando petición...")
response = requests.post(url, json=payload, headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
'''

print(script_content)
