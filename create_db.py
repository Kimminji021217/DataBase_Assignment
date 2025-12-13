import pandas as pd
import sqlite3

csv_file = "산업통상자원부_반도체디스플레이 수출동향 추이_20241231.csv"
db_file = "export.db"

# 1) CSV 읽기
df = pd.read_csv(csv_file, encoding="utf-8")

# 2) year, month 분리 ("2015-01" 형태)
df["year_month"] = df["년월"]
df["year"] = df["년월"].str.split("-").str[0].astype(int)
df["month"] = df["년월"].str.split("-").str[1].astype(int)

# 3) 컬럼 매핑 (value, yoy)
columns_map = {
    "반도체": ("반도체(억불)", "반도체_전년동월대비_증감률(퍼센트)"),
    "메모리": ("메모리(억불)", "메모리_전년동월대비_증감률(퍼센트)"),
    "메모리_DRAM": ("메모리_D램(억불)", "메모리_D램_전년동월대비_증감률(퍼센트)"),
    "메모리_NAND": ("메모리_낸드(억불)", "메모리_낸드_전년동월대비_증감률(퍼센트)"),
    "메모리_MCP": ("메모리_MCP(억불)", "메모리_MCP_전년동월대비_증감률(퍼센트)"),
    "시스템반도체": ("시스템_반도체(억불)", "시스템_반도체_전년동월대비_증감률(퍼센트)"),
    "개별소자": ("개별소자(억불)", "개별소자_전년동월대비_증감률(퍼센트)"),
    "디스플레이패널": ("디스플레이_패널(억불)", "디스플레이_패널_전년동월대비_증감률(퍼센트)")
}

# 4) SQLite 연결
conn = sqlite3.connect(db_file)

# 스키마 생성
conn.execute("""
DROP TABLE IF EXISTS export_stats;
""")

conn.execute("""
CREATE TABLE export_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    name TEXT NOT NULL,
    year_month TEXT NOT NULL,
    year INTEGER,
    month INTEGER,
    export_value REAL,
    yoy REAL,
    unit TEXT DEFAULT '억불',
    is_increase INTEGER GENERATED ALWAYS AS 
        (CASE WHEN yoy > 0 THEN 1 ELSE 0 END) VIRTUAL,
    source TEXT DEFAULT '산업통상자원부 반도체·디스플레이 수출동향',
    UNIQUE(category, name, year_month)
);
""")

# 5) insert 준비
insert_sql = """
INSERT OR IGNORE INTO export_stats
(category, name, year_month, year, month, export_value, yoy)
VALUES (?, ?, ?, ?, ?, ?, ?)
"""

# 6) wide → long 변환
for _, row in df.iterrows():
    ym = row["year_month"]
    year = int(row["year"])
    month = int(row["month"])

    for name, (value_col, yoy_col) in columns_map.items():
        category = name.split("_")[0]
        export_value = row[value_col]
        yoy = row[yoy_col]

        conn.execute(insert_sql, (category, name, ym, year, month, export_value, yoy))

conn.commit()
conn.close()
