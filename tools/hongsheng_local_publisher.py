#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""洪盛集藏：本地资料库 -> AI整理 -> GitHub网站发布
默认先生成草稿；HONGSHENG_AUTO_PUBLISH=1 才会发布。"""
import os,json,hashlib,datetime,pathlib,urllib.request,base64
ROOT=pathlib.Path(os.environ.get("HONGSHENG_LIBRARY","洪盛资料库")); REPO=os.environ.get("HONGSHENG_REPO","yang79403-wq/yang79403-wq.github.io"); BRANCH=os.environ.get("HONGSHENG_BRANCH","main"); TOKEN=os.environ.get("HONGSHENG_GITHUB_TOKEN",""); AI_ENDPOINT=os.environ.get("HONGSHENG_AI_ENDPOINT",""); AI_KEY=os.environ.get("HONGSHENG_AI_API_KEY",""); AI_MODEL=os.environ.get("HONGSHENG_AI_MODEL","")
EXTS={".txt",".md",".json",".csv"}; MAP={"福建钱币":("fujian","福建铜钱 银元 铜币 纸币"),"银元":("content","收藏交流 · 鉴赏参考"),"铜元":("content","收藏交流 · 鉴赏参考"),"古钱":("content","收藏交流 · 鉴赏参考"),"纸币":("content","收藏交流 · 鉴赏参考"),"纪念币":("content","收藏交流 · 鉴赏参考"),"机制币":("content","收藏交流 · 鉴赏参考"),"评级资料":("services","评级知识"),"行情资料":("market","行情资料参考")}
def sha256(p):
 h=hashlib.sha256(); h.update(p.read_bytes()); return h.hexdigest()
def read_text(p):
 b=p.read_bytes()
 for e in ("utf-8","gb18030","utf-16"):
  try:return b.decode(e)
  except UnicodeDecodeError:pass
 return b.decode("utf-8",errors="ignore")
def classify(p):
 for part in p.parts:
  if part in MAP:return MAP[part]
 return ("content","收藏交流 · 鉴赏参考")
def ai_analyze(title,text,section):
 if not(AI_ENDPOINT and AI_KEY):return {"title":title,"summary":text[:180].replace("\n"," "),"content":text,"tags":[],"ai":False}
 payload={"model":AI_MODEL,"messages":[{"role":"system","content":"你是洪盛集藏钱币资料编辑。只整理用户提供的资料，不编造价格、版别或历史事实。输出JSON：title,summary,content,tags。"},{"role":"user","content":f"目标版块：{section}\n标题：{title}\n资料：\n{text[:50000]}"}],"temperature":0.2}
 req=urllib.request.Request(AI_ENDPOINT,data=json.dumps(payload).encode(),headers={"Content-Type":"application/json","Authorization":"Bearer "+AI_KEY})
 with urllib.request.urlopen(req,timeout=120) as r:data=json.loads(r.read().decode())
 msg=data.get("choices",[{}])[0].get("message",{}).get("content","")
 try:return json.loads(msg)
 except:return {"title":title,"summary":"","content":msg,"tags":[],"ai":True}
def gh(path,method="GET",body=None):
 if not TOKEN:raise RuntimeError("缺少 HONGSHENG_GITHUB_TOKEN")
 url="https://api.github.com/repos/"+REPO+"/contents/"+path+(("?ref="+BRANCH) if method=="GET" else "")
 req=urllib.request.Request(url,data=(json.dumps(body).encode() if body is not None else None),method=method,headers={"Accept":"application/vnd.github+json","Authorization":"Bearer "+TOKEN,"X-GitHub-Api-Version":"2022-11-28","Content-Type":"application/json"})
 with urllib.request.urlopen(req,timeout=60) as r:return json.loads(r.read().decode())
def publish_many(objs,file_name):
 path="data/content/"+file_name
 try:old=gh(path); old_sha=old.get("sha"); raw=base64.b64decode(old.get("content","")).decode() if old.get("content") else "[]"; existing=json.loads(raw)
 except Exception:old_sha=None;existing=[]
 ids={x.get("sourceHash") for x in existing}; new=[x for x in objs if x.get("sourceHash") not in ids]
 if not new:return 0
 existing.extend(new); body={"message":"洪盛集藏：本地资料自动整理发布","content":base64.b64encode(json.dumps(existing,ensure_ascii=False,indent=2).encode()).decode(),"branch":BRANCH}
 if old_sha:body["sha"]=old_sha
 gh(path,"PUT",body);return len(new)
def main():
 if not ROOT.exists():print("资料库不存在：",ROOT);return
 manifest=[]
 for p in ROOT.rglob("*"):
  if not p.is_file() or p.suffix.lower() not in EXTS or p.name=="_processed_manifest.json":continue
  digest=sha256(p);gid,gname=classify(p);text=read_text(p);res=ai_analyze(p.stem,text,gname);manifest.append({"id":"local_"+digest[:16],"title":res.get("title",p.stem),"note":res.get("summary",""),"content":res.get("content",text),"tags":res.get("tags",[]),"date":datetime.date.today().isoformat(),"status":"draft","groupId":gid,"groupName":gname,"source":"local-library","sourceFile":str(p),"sourceHash":digest,"aiAnalyzed":bool(res.get("ai",False))})
 (ROOT/"_processed_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8");print(f"扫描 {len(manifest)} 个资料，已生成处理清单。")
 if os.environ.get("HONGSHENG_AUTO_PUBLISH","0")=="1":
  by={}
  for x in manifest:by.setdefault(x["groupId"],[]).append(x)
  total=0
  for gid,arr in by.items():total+=publish_many(arr,gid+".json")
  print("自动发布新增内容：",total)
if __name__=="__main__":main()
