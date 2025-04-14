import requests

print(requests.post('http://localhost:8001', json={}, timeout=10).json())