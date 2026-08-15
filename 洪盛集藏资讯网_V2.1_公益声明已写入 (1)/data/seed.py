import sqlite3
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).resolve().parent
DB = BASE / "market.db"
conn = sqlite3.connect(DB)
conn.execute("""CREATE TABLE IF NOT EXISTS prices(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT NOT NULL, category TEXT NOT NULL, price REAL, unit TEXT,
change_pct REAL DEFAULT 0, source TEXT, captured_at TEXT)""")

rows = [
("袁世凯像银元（袁大头）","老银元",None,"枚",0,"待接入授权行情源"),
("孙中山像开国纪念币","老银元",None,"枚",0,"待接入授权行情源"),
("船洋","老银元",None,"枚",0,"待接入授权行情源"),
("龙洋","老银元",None,"枚",0,"待接入授权行情源"),
("清代铜钱","古钱币",None,"枚",0,"待接入授权行情源"),
("第一套人民币","老纸币",None,"套",0,"待接入授权行情源"),
("第三套人民币车工2元","老纸币",None,"张",0,"待接入授权行情源"),
("普通流通纪念币","纪念币",None,"枚",0,"待接入授权行情源"),
("熊猫金银币","金银币",None,"枚",0,"待接入授权行情源"),
("PCGS评级币","评级币",None,"枚",0,"待接入授权行情源"),
]
now = datetime.now().isoformat(timespec="seconds")
conn.executemany("INSERT INTO prices(name,category,price,unit,change_pct,source,captured_at) VALUES(?,?,?,?,?,?,?)",
                 [(a,b,c,d,e,f,now) for a,b,c,d,e,f in rows])
conn.commit()
conn.close()
print("seed complete")
