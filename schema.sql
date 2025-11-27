DROP TABLE IF EXISTS export_stats;

CREATE TABLE export_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    category TEXT NOT NULL,
    name TEXT NOT NULL,

    year_month TEXT NOT NULL,   -- "2015-01"
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

CREATE INDEX idx_category ON export_stats (category);
CREATE INDEX idx_name ON export_stats (name);
CREATE INDEX idx_year_month ON export_stats (year_month);
CREATE INDEX idx_export_value ON export_stats (export_value);
CREATE INDEX idx_yoy ON export_stats (yoy);
