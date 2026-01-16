from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_db_count_endpoint():
    r = client.get("/db/count")
    assert r.status_code == 200
    assert "count" in r.json()
