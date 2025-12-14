import sqlite3

conn = sqlite3.connect("app.db")
cursor = conn.cursor()

# faults 테이블 생성
cursor.execute("""
CREATE TABLE IF NOT EXISTS faults (
    fault_code TEXT PRIMARY KEY,
    fault_name TEXT NOT NULL
)
""")

# 기본 fault 데이터 삽입
fault_data = [
    ("fault_0", "Pastry"),
    ("fault_1", "Z_Scratch"),
    ("fault_2", "K_Scratch"),
    ("fault_3", "Stains"),
    ("fault_4", "Dirtiness"),
    ("fault_5", "Bumps"),
    ("fault_6", "Other Faults")
]

cursor.executemany(
    "INSERT OR IGNORE INTO faults (fault_code, fault_name) VALUES (?, ?)",
    fault_data
)

conn.commit()
conn.close()
