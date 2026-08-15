from datetime import datetime, timezone
from pathlib import Path
import json
import requests
from bs4 import BeautifulSoup

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data" / "baofuju_sources.json"
HEADERS = {"User-Agent": "HongshengJicang/1.0 (+public-source-index)"}

def inspect_source(item):
    result = dict(item)
    try:
        r = requests.get(item["url"], headers=HEADERS, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        title = soup.title.get_text(" ", strip=True) if soup.title else item["title"]
        result["page_title"] = title[:180]
        result["image_count"] = len(soup.find_all("img"))
        result["checked_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        result["status"] = "可访问"
    except Exception as exc:
        result["checked_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        result["status"] = f"暂时无法访问：{type(exc).__name__}"
    return result

def run():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    data["updated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    data["sources"] = [inspect_source(x) for x in data["sources"]]
    DATA.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("宝福局资料源检查完成：", len(data["sources"]))

if __name__ == "__main__":
    run()
