from  fastapi.testclient import  TestClient
from main import app

client = TestClient(app)

def test_health():
	r = client.get("/health")
	assert r.status_code == 200
	assert r.json() == {"status": "ok"}

def test_shorten_returns_code():
	r = client.post("/shorten", json={"url": "https://example.com"})
	assert r.status_code == 200
	assert len(r.json()["code"]) ==  6

def test_redirect_works():
	r = client.post("/shorten", json={"url": "https://example.com"})
	code =  r.json()["code"]
	r2 = client.get(f"/{code}", follow_redirects=False)
	assert r2.status_code in (302, 307)
	assert r2.headers["location"] == "https://example.com"

def test_unknown_code_returns_404():
	r = client.get("/tidakada", follow_redirects=False)
	assert r.status_code == 404
