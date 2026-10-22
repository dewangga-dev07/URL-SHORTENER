import pytest
from  fastapi.testclient import  TestClient
from main import app, init_db

@pytest.fixture(scope="module")
def client():
	init_db()
	with TestClient(app) as c:
		yield c

def test_health(client):
	r = client.get("/health")
	assert r.status_code == 200
	assert r.json() == {"status": "ok"}

def test_shorten_returns_code(client):
	r = client.post("/shorten", json={"url": "https://example.com"})
	assert r.status_code == 200
	assert len(r.json()["code"]) ==  8

def test_redirect_works(client):
	r = client.post("/shorten", json={"url": "https://example.com"})
	code =  r.json()["code"]
	r2 = client.get(f"/{code}", follow_redirects=False)
	assert r2.status_code in (302, 307)
	assert r2.headers["location"] == "https://example.com"

def test_unknown_code_returns_404(client):
	r = client.get("/tidakada", follow_redirects=False)
	assert r.status_code == 404

def test_stats_returns_total(client):
	r = client.get("/stats")
	assert r.status_code == 200
	assert isinstance(r.json()["total_links"], int)
def test_stats_increases_after_shorten(client):
        before = client.get("/stats").json()["total_links"]
        client.post ("/shorten", json={"url" : "https://example.com"})
        after = client.get("/stats").json()["total_links"]
        assert after == before + 1
