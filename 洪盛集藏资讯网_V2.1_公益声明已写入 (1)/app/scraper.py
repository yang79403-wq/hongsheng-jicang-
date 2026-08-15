from datetime import datetime
from pathlib import Path
import sqlite3, time, requests
from bs4 import BeautifulSoup

BASE = Path(__file__).resolve().parent.parent
DB = BASE / "data" / "market.db"

SOURCES = {
    "钱币天堂": "https://www.yy11.com/",
    "一尘网": "https://www.ybk1.com/board/2",
}

HEADERS = {
    "User-Agent": "HongshengJicang/1.0 (+public-market-data; contact site owner)"
}

def fetch(url):
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    return r.text

def parse_public_prices(html, source):
    """
    仅提供安全的解析骨架。
    正式部署时，根据获得授权/允许采集的公开页面字段编写解析器。
    不绕过登录、验证码、反爬或访问控制。
    """
    soup = BeautifulSoup(html, "html.parser")
    results = []
    for row in soup.select("table tr"):
        cells = [x.get_text(" ", strip=True) for x in row.select("th,td")]
        if len(cells) >= 2:
            # 模板：不要把未知字段直接当成价格。
            pass
    return results

def save(rows):
    conn = sqlite3.connect(DB)
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
    now = datetime.now().isoformat(timespec="seconds")
    for x in rows:
        conn.execute(
            """INSERT INTO prices(name,category,price,unit,change_pct,source,captured_at)
               VALUES(?,?,?,?,?,?,?)""",
            (x["name"], x["category"], x.get("price"), x.get("unit"),
             x.get("change_pct", 0), x["source"], now)
        )
    conn.commit()
    conn.close()

def run():
    all_rows = []
    for source, url in SOURCES.items():
        try:
            html = fetch(url)
            all_rows.extend(parse_public_prices(html, source))
            time.sleep(2)
        except Exception as e:
            print(f"[WARN] {source}: {e}")
    if all_rows:
        save(all_rows)
    print(f"采集完成：{len(all_rows)} 条")

if __name__ == "__main__":
    run()
