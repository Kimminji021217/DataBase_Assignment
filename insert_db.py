import sqlite3
import pandas as pd
from pathlib import Path

# 경로 설정
CSV_PATH = Path("data") / "steel_plates_faults_clean.csv"
DB_PATH = Path("app.db")

# CSV 읽기
df = pd.read_csv(CSV_PATH)

# SQLite 연결
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 기존 테이블 삭제 (다시 실행해도 되게)
cursor.execute("DROP TABLE IF EXISTS plates")

# 테이블 생성
columns_sql = []
for col in df.columns:
    if col == "fault_type":
        columns_sql.append(f"{col} TEXT")
    else:
        columns_sql.append(f"{col} REAL")

create_table_sql = f"""
CREATE TABLE plates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    {", ".join(columns_sql)}
)
"""

cursor.execute(create_table_sql)

# 데이터 삽입
df.to_sql("plates", conn, if_exists="append", index=False)

# 저장 후 종료
conn.commit()
conn.close()
