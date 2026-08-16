from datetime import datetime, timezone
from pathlib import Path
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
HEADERS = {"User-Agent": "HongshengJicang/2.1 (+public-source-index; educational-use)"}
BLOCKED_HOST_HINTS = ("tcmb.culture.tw", ".tw/", ".tw")

def mainland_allowed(url: str) -> bool:
    u = (url or "").lower()
    return not any(h in u for h in BLOCKED_HOST_HINTS)

def inspect(item):
    out = dict(item)
    url = item.get("url", "")
    if not mainland_allowed(url):
        out.update({"status": "blocked_non_mainland", "image_count": 0, "checked_at": now()})
        return out
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        imgs = []
        for img in soup.find_all("img"):
            src = img.get("src") or img.get("data-src")
            if src:
                imgs.append(urljoin(r.url, src))
        out.update({"status": "ok", "page_title": soup.title.get_text(" ", strip=True)[:180] if soup.title else item.get("name", ""), "image_count": len(imgs), "image_index": imgs[:30], "checked_at": now()})
    except Exception as e:
        out.update({"status": f"error:{type(e).__name__}", "image_count": 0, "image_index": [], "checked_at": now()})
    return out

def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def run():
    sources_file = DATA / "fujian_sources.json"
    src = json.loads(sources_file.read_text(encoding="utf-8"))
    checked = [inspect(x) for x in src.get("sources", []) if mainland_allowed(x.get("url", ""))]
    status = {"updated_at": now(), "policy": "中国大陆来源优先；台湾地区网站不进入自动采集池；受版权保护图片不直接复制。", "sources": checked}
    (DATA / "source_status.json").write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8")

    f = json.loads((DATA / "fujian.json").read_text(encoding="utf-8"))
    f["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    f["source_status_count"] = len(checked)
    f["collection_note"] = "自动任务检查公开来源并建立资料/图片索引；授权不明确时只保留来源，不镜像图片。"
    f["records"] = [r for r in f.get("records", []) if mainland_allowed(r.get("source_url", ""))]
    (DATA / "fujian.json").write_text(json.dumps(f, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"checked={len(checked)}, fujian_records={len(f['records'])}")

if __name__ == "__main__":
    run()
