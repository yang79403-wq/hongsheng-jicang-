from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import sqlite3
import json

BASE = Path(__file__).resolve().parent.parent
DB = BASE / "data" / "market.db"
BAOFU_DATA = BASE / "data" / "baofuju.json"
BAOFU_SOURCES = BASE / "data" / "baofuju_sources.json"

app = FastAPI(title="洪盛集藏资讯网", version="2.4")
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")

def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

@app.on_event("startup")
def startup():
    DB.parent.mkdir(exist_ok=True)
    conn = db()
    conn.execute("""CREATE TABLE IF NOT EXISTS prices(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        price REAL,
        unit TEXT,
        change_pct REAL DEFAULT 0,
        source TEXT,
        captured_at TEXT
    )""")
    conn.commit()
    conn.close()

@app.get("/")
def home():
    return FileResponse(BASE / "static" / "index.html")

@app.get("/en")
def english_home():
    return FileResponse(BASE / "static" / "index-en.html")

@app.get("/baofuju")
def baofuju_page():
    return FileResponse(BASE / "static" / "baofuju.html")

@app.get("/api/baofuju")
def baofuju_data():
    with open(BAOFU_DATA, "r", encoding="utf-8") as f:
        return json.load(f)

@app.get("/api/baofuju/sources")
def baofuju_sources():
    with open(BAOFU_SOURCES, "r", encoding="utf-8") as f:
        return json.load(f)

@app.get("/api/prices")
def prices(category: str | None = None):
    conn = db()
    if category:
        rows = conn.execute("SELECT * FROM prices WHERE category=? ORDER BY id DESC LIMIT 100", (category,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM prices ORDER BY id DESC LIMIT 100").fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.get("/api/health")
def health():
    conn = db()
    n = conn.execute("SELECT COUNT(*) FROM prices").fetchone()[0]
    conn.close()
    return {"ok": True, "price_records": n, "baofuju_database": BAOFU_DATA.exists(), "baofuju_sources": BAOFU_SOURCES.exists()}
