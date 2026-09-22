from uuid import uuid4
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_register_and_protected_farm_flow():
    email = f"test-{uuid4().hex}@example.com"
    r = client.post("/api/auth/register", json={
        "full_name": "Test Farmer",
        "email": email,
        "phone": "08000000000",
        "password": "StrongPass123!"
    })
    assert r.status_code == 200
    token = r.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    r = client.post("/api/farms", headers=headers, json={
        "name": "Test Farm",
        "location": "Mokwa",
        "farm_type": "crop",
        "size_hectares": 2,
        "primary_activity": "Beans"
    })
    assert r.status_code == 200
    farm = r.json()
    assert farm["name"] == "Test Farm"

    r = client.get("/api/farms", headers=headers)
    assert r.status_code == 200
    assert any(item["id"] == farm["id"] for item in r.json())
