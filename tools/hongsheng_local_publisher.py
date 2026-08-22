#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""洪盛集藏：本地资料库 -> AI整理 -> GitHub网站发布
标准库版本；支持 txt/md/json/csv。PDF/Word/图片可先放入待处理目录，
安装对应解析库后再扩展。默认先生成 draft，避免未经检查的资料直接上线。
"""
import os, json, hashlib, datetime, pathlib, urllib.request

ROOT = pathlib.Path(os.environ.get("HONGSHENG_LIBRARY", "洪盛资料库"))
REPO = os.environ.get("HONGSHENG_REPO", "yang79403-wq/yang79403-wq.github.io")
BRANCH = os.environ.get("HONGSHENG_BRANCH", "main")
TOKEN = os.environ.get("HONGSHENG_GITHUB_TOKEN", "")
AI_ENDPOINT = os.environ.get("HONGSHENG_AI_ENDPOINT", "")
AI_KEY = os.environ.get("HONGSHENG_AI_API_KEY", "")
AI_MODEL = os.environ.get("HONGSHENG_AI_MODEL", "")

EXTS = {".txt", ".md", ".json", ".csv"}
MAP = {
    "福建钱币": ("fujian", "福建铜钱 银元 铜币 纸币"),
    "银元": ("content", "收藏交流 · 鉴赏参考"),
    "铜元": ("content", "收藏交流 · 鉴赏参考"),
    "古钱": ("content", "收藏交流 · 鉴赏参考"),
    "纸币": ("content", "收藏交流 · 鉴赏参考"),
    "纪念币": ("content", "收藏交流 · 鉴赏参考"),
    "机制币": ("content", "收藏交流 · 鉴赏参考"),
    "评级资料": ("services", "评级知识"),
    "行情资料": ("market", "行情资料参考")
}

def sha256(p):
    h=hashlib.sha256(); h.update(p.read_bytes()); return h.hexdigest()

def read_text(p):
    b=p.read_bytes()
    for enc in ("utf-8", "gb18030", "utf-16"):
        try: return b.decode(enc)
        except UnicodeDecodeError: pass
    return b.decode("utf-8", errors="ignore")

def classify(p):
    for part in p.parts:
        if part in MAP: return MAP[part]
    return ("content", "收藏交流 · 鉴赏参考")

def ai_analyze(title, text, section):
    if not (AI_ENDPOINT and AI_KEY):
        return {"title": title, "summary": text[:180].replace("\n", " "), "content": text, "tags": [], "ai": False}
    payload={"model":AI_MODEL,"messages":[{"role":"system","content":"你是洪盛集藏钱币资料编辑。只整理用户提供的资料，不编造价格、版别或历史事实。输出JSON：title,summary,content,tags。"},{"role":"user","content":f"目标版块：{section}\n标题：{title}\n资料：\n{text[:50000]}"}],"temperature":0.2}
    req=urllib.request.Request(AI_ENDPOINT,data=json.dumps(payload).encode(),headers={"Content-Type":"application/json","Authorization":"Bearer "+AI_KEY})
    with urllib.request.urlopen(req, timeout=120) as r: data=json.loads(r.read().decode())
    msg=data.get("choices",[{}])[0].get("message",{}).get("content", "")
    try: return json.loads(msg)
    except Exception: return {"title":title,"summary":"","content":msg,"tags":[],"ai":True}

def gh(path, method="GET", body=None):
    if not TOKEN: raise RuntimeError("缺少 HONGSHENG_GITHUB_TOKEN")
    url="https://api.github.com/repos/"+REPO+"/contents/"+path
    if method=="GET": url += "?ref="+BRANCH
    data=json.dumps(body).encode() if body is not None else None
    req=urllib.request.Request(url,data=data,method=method,headers={"Accept":"application/vnd.github+json","Authorization":"Bearer "+TOKEN,"X-GitHub-Api-Version":"2022-11-28","Content-Type":"application/json"})
    with urllib.request.urlopen(req,timeout=60) as r: return json.loads(r.read().decode())

def b64(s):
    import base64; return base64.b64encode(s.encode()).decode()

def publish(obj, file_name):
    path="data/content/"+file_name
    try: old=gh(path); sha=old.get("sha")
    except Exception: sha=None
    try: existing=json.loads(__import__('base64').b64decode(old["content"]).decode()) if old else []
    except Exception: existing=[]
    existing.append(obj)
    body={"message":"洪盛集藏：本地资料自动整理（草稿）","content":b64(json.dumps(existing,ensure_ascii=False,indent=2)),"branch":BRANCH}
    if sha: body["sha"]=sha
    gh(path,"PUT",body)

def main():
    if not ROOT.exists(): print("资料库不存在：", ROOT); return
    manifest=[]
    for p in ROOT.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in EXTS: continue
        digest=sha256(p); section_id,section_name=classify(p); text=read_text(p)
        title=p.stem
        result=ai_analyze(title,text,section_name)
        obj={"id":"local_"+digest[:16],"title":result.get("title",title),"note":result.get("summary",""),"content":result.get("content",text),"tags":result.get("tags",[]),"date":datetime.date.today().isoformat(),"status":"draft","groupId":section_id,"groupName":section_name,"source":"local-library","sourceFile":str(p),"sourceHash":digest,"aiAnalyzed":bool(result.get("ai",False))}
        manifest.append(obj)
    out=ROOT/"_processed_manifest.json"; out.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"扫描 {len(manifest)} 个资料。已生成 {out}。默认草稿，不会未经审核直接上线。")
    if os.environ.get("HONGSHENG_AUTO_PUBLISH","0")=="1":
        by={}
        for x in manifest: by.setdefault(x["groupId"],[]).append(x)
        for gid,arr in by.items(): publish(arr[0], gid+".json")
        print("已执行自动发布。")

if __name__=="__main__": main()
