import random
import string
import sqlite3

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

app = FastAPI()
DB_PATH = "urls.db"

def get_conn():
	return sqlite3.connect (DB_PATH)

def init_db():
	with get_conn() as conn:
		conn.execute(
			"CREATE TABLE IF NOT EXISTS urls (code TEXT PRIMARY KEY, url TEXT NOT NULL)"
		)

init_db()

class ShortenRequest(BaseModel):
	url: str

def generate_code(length=6):
	chars = string.ascii_letters + string.digits
	return "".join(random.choices(chars, k=length))

@app.get("/health")
def health():
	return {"status": "ok"}

@app.post("/shorten")
def shorten(req:ShortenRequest):
	code = generate_code()
	with get_conn() as conn:
		conn.execute("INSERT INTO  urls (code, url) VALUES (?, ?)", (code, req.url))
	return {"code": code,  "short_url": f"http://localhost:8000/{code}"}

@app.get("/{code}")
def redirect(code: str):
	with get_conn() as conn:
		row = conn.execute("SELECT url FROM  urls WHERE code = ?", (code,)).fetchone()
	if row is None:
		raise  HTTPException(status_code=404, detail="Link tidak ditemukan")
	return RedirectResponse(row[0]) 

