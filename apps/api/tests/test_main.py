from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get('/health')
    assert r.status_code == 200
    assert r.json()['status'] == 'ok'

def test_farmer():
    r = client.post('/api/farmers', json={'full_name':'Test Farmer','phone':'08000000000','location':'Mokwa','farm_type':'crop'})
    assert r.status_code == 200
    assert r.json()['full_name'] == 'Test Farmer'
