from datetime import datetime, timezone
from pathlib import Path
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data" / "baofuju_sources.json"
HEADERS = {"User-Agent": "HongshengJicang/2.0 (+public-source-index; educational-use)"}

# 只建立公开来源的资料/图片索引，不把第三方受版权保护的图片直接复制到本站。
def inspect_source(item):
    result = dict(item)
    try:
        r = requests.get(item["url"], headers=HEADERS, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        title = soup.title.get_text(" ", strip=True) if soup.title else item.get("title", "")
        images = []
        for img in soup.find_all("img"):
            src = img.get("src") or img.get("data-src")
            if src:
                images.append(urljoin(r.url, src))
        result["page_title"] = title[:180]
        result["image_count"] = len(images)
        result["image_index"] = images[:30]
        result["checked_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        result["status"] = "可访问"
    except Exception as exc:
        result["checked_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        result["status"] = f"暂时无法访问：{type(exc).__name__}"
        result["image_index"] = []
    return result

def run():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    data["updated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    data["collection_policy"] = "公开资料索引；图片按来源记录，不默认复制受版权保护图片；优先使用公共领域、博物馆开放资料或明确授权素材。"
    data["sources"] = [inspect_source(x) for x in data["sources"]]
    DATA.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("福建/宝福局公开资料图片索引检查完成：", len(data["sources"]))

if __name__ == "__main__":
    run()
