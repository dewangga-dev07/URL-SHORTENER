import os
import random
import string

import psycopg
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

app = FastAPI()

DATABASE_URL = os.getenv(
	"DATABASE_URL", "postgresql://shortener:shortener@localhost:5432/shortener"
	)

def get_conn():
	return psycopg.connect(DATABASE_URL)

def init_db():
	with get_conn() as conn:
		conn.execute(
			"CREATE TABLE IF NOT EXISTS urls (code TEXT PRIMARY KEY, url TEXT NOT NULL)"
		)


class ShortenRequest(BaseModel):
	url: str

def generate_code(length=8):
	chars = string.ascii_letters + string.digits
	return "".join(random.choices(chars, k=length))

@app.on_event("startup")
def startup():
	init_db()

@app.get("/health")
def health():
	return {"status": "ok"}

@app.post("/shorten")
def shorten(req:ShortenRequest):
	code = generate_code()
	with get_conn() as conn:
		conn.execute("INSERT INTO  urls (code, url) VALUES (%s, %s)", (code, req.url))
	return {"code": code,  "short_url": f"http://localhost:8000/{code}"}

@app.get("/stats")
def stats():
	with get_conn() as conn:
		row = conn.execute ("SELECT COUNT(*) FROM urls").fetchone()
	return {"total_links": row[0]}

@app.get("/{code}")
def redirect(code: str):
	with get_conn() as conn:
		row = conn.execute("SELECT url FROM  urls WHERE code = %s", (code,)).fetchone()
	if row is None:
		raise  HTTPException(status_code=404, detail="Link tidak ditemukan")
	return RedirectResponse(row[0]) 

