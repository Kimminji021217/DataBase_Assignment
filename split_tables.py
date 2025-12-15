import sqlite3

conn = sqlite3.connect("app.db")
cursor = conn.cursor()

# 1. plates_new (목록용)
cursor.execute("""
CREATE TABLE IF NOT EXISTS plates_new (
    plate_id INTEGER PRIMARY KEY,
    fault_code TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
""")

# 2. plate_measurements (상세용)
cursor.execute("""
CREATE TABLE IF NOT EXISTS plate_measurements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plate_id INTEGER,
    thickness REAL,
    width REAL,
    surface_area REAL,
    FOREIGN KEY (plate_id) REFERENCES plates_new(plate_id)
)
""")

# 3. 기존 plates 데이터 옮기기
cursor.execute("""
INSERT INTO plates_new (plate_id, fault_code)
SELECT id, fault_type FROM plates
""")

cursor.execute("""
INSERT INTO plate_measurements (plate_id, thickness, width, surface_area)
SELECT id, thickness, width, surface_area FROM plates
""")

conn.commit()
conn.close()

print("Table split completed.")
