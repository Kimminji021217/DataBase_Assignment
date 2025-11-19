-- 반도체·디스플레이 수출동향 테이블
CREATE TABLE IF NOT EXISTS export_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- 분류 정보
    category TEXT NOT NULL,        -- ex. 반도체, 디스플레이, 메모리 등
    name TEXT NOT NULL,            -- ex. 메모리_D램, 시스템반도체 등

    -- 날짜 정보
    year_month INTEGER NOT NULL,   -- ex. 202401
    year INTEGER,                  
    month INTEGER,

    -- 데이터 값
    export_value REAL,             -- 억불 단위 수출액
    yoy REAL,                      -- 전년동월 대비 증감률 (%)
    unit TEXT DEFAULT '억불',

    -- 자동 계산
    is_increase INTEGER GENERATED ALWAYS AS 
        (CASE WHEN yoy > 0 THEN 1 ELSE 0 END) VIRTUAL,

    -- 데이터 출처
    source TEXT DEFAULT '산업통상자원부 반도체·디스플레이 수출동향',

    -- 중복 방지
    UNIQUE(category, name, year_month)
);

-- 인덱스들
CREATE INDEX IF NOT EXISTS idx_category ON export_stats (category);
CREATE INDEX IF NOT EXISTS idx_name ON export_stats (name);
CREATE INDEX IF NOT EXISTS idx_year_month ON export_stats (year_month);
CREATE INDEX IF NOT EXISTS idx_export_value ON export_stats (export_value);
CREATE INDEX IF NOT EXISTS idx_yoy ON export_stats (yoy);
