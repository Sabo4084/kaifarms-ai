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


def test_assistant_mode_routing():
    from app.main import route_mode
    assert route_mode("auto", None, "My layer chickens stopped eating") == "poultry"
    assert route_mode("auto", None, "My goats have diarrhea") == "livestock"
    assert route_mode("auto", "poultry", "What should I record today?") == "poultry"
    assert route_mode("crop", "poultry", "My chickens are sick") == "crop"

def test_referral_create_and_private_listing():
    email = f"referral-{uuid4().hex}@example.com"
    registered = client.post("/api/auth/register", json={
        "full_name": "Referral Farmer", "email": email,
        "phone": "08000000000", "password": "StrongPass123!"
    })
    assert registered.status_code == 200
    headers = {"Authorization": f"Bearer {registered.json()['token']}"}
    created = client.post("/api/referrals", headers=headers, json={
        "category": "crop", "urgency": "soon",
        "issue_summary": "My maize leaves are yellowing and growth has slowed.",
        "contact_method": "in_app"
    })
    assert created.status_code == 201
    assert created.json()["status"] == "submitted"
    listed = client.get("/api/referrals", headers=headers)
    assert listed.status_code == 200
    assert any(item["id"] == created.json()["id"] for item in listed.json())
    assert client.get("/api/referrals").status_code == 401
