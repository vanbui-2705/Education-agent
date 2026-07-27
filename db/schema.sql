-- Cấu trúc database. Chạy file này để tạo bảng: python -m db.init_db
-- "IF NOT EXISTS" = chạy lại nhiều lần cũng không lỗi.

CREATE TABLE IF NOT EXISTS giao_vien (
    ma_gv TEXT PRIMARY KEY,          -- GV01
    ten   TEXT NOT NULL              -- Nguyễn Thị Lan
);

CREATE TABLE IF NOT EXISTS phong (
    ma_phong  TEXT PRIMARY KEY,      -- P302
    suc_chua  INTEGER NOT NULL       -- 20
);

CREATE TABLE IF NOT EXISTS lop (
    ma_lop   TEXT PRIMARY KEY,       -- T9A
    ten_lop  TEXT NOT NULL,          -- Toán 9 nâng cao - K12
    mon      TEXT NOT NULL,          -- Toán
    si_so    INTEGER NOT NULL        -- 18
);

-- Bảng lõi: mỗi dòng = một buổi học trong tuần.
-- Mọi câu hỏi về lịch đều quy về việc lọc bảng này.
CREATE TABLE IF NOT EXISTS buoi_hoc (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_lop    TEXT NOT NULL REFERENCES lop(ma_lop),
    ma_gv     TEXT NOT NULL REFERENCES giao_vien(ma_gv),
    ma_phong  TEXT NOT NULL REFERENCES phong(ma_phong),
    thu       INTEGER NOT NULL,      -- 2..8, 8 = Chủ nhật
    ca        INTEGER NOT NULL,      -- 1..4

    -- Chặn trùng ngay ở tầng database, không đợi code kiểm tra:
    -- một phòng không thể có 2 lớp cùng thứ + cùng ca
    UNIQUE (ma_phong, thu, ca),
    -- một giáo viên không thể dạy 2 lớp cùng lúc
    UNIQUE (ma_gv, thu, ca)
);

-- Chỉ mục giúp tra "thứ 3 ca 2 có gì" chạy nhanh
CREATE INDEX IF NOT EXISTS idx_buoi_thu_ca ON buoi_hoc (thu, ca);
