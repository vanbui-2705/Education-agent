"""Cấu hình chung. Mọi file khác lấy đường dẫn và key từ đây.

Vì sao gom một chỗ: sau này đổi tên file database hay đổi model,
chỉ sửa ở đây, không phải đi lục từng file.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Thư mục gốc dự án = thư mục chứa chính file config.py này
ROOT = Path(__file__).parent

# Đọc file .env, nạp các dòng KEY=VALUE vào biến môi trường
load_dotenv(ROOT / ".env")

# --- Đường dẫn ---
DATA_DIR = ROOT / "data"
SAMPLES_DIR = ROOT / "samples"
DB_PATH = DATA_DIR / "trung_tam.db"
SCHEMA_PATH = ROOT / "db" / "schema.sql"

# --- Gemini ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# --- Quy ước thời gian (CHỐT SAU khi bạn xác nhận ca học thật) ---
# Thứ: 2..8, trong đó 8 = Chủ nhật
THU_HOP_LE = [2, 3, 4, 5, 6, 7, 8]
TEN_THU = {2: "Thứ 2", 3: "Thứ 3", 4: "Thứ 4", 5: "Thứ 5",
           6: "Thứ 6", 7: "Thứ 7", 8: "Chủ nhật"}

# Ca: 1..4. Giờ giấc dưới đây là TẠM, sửa lại khi bạn check xong.
CA_HOP_LE = [1, 2, 3, 4]
GIO_CA = {
    1: "08:00-09:30",
    2: "09:45-11:15",
    3: "14:00-15:30",
    4: "19:00-20:30",
}


def kiem_tra_cau_hinh() -> None:
    """Gọi lúc khởi động để báo lỗi sớm thay vì lỗi khó hiểu lúc chạy."""
    if not GEMINI_API_KEY:
        raise RuntimeError(
            "Chưa có GEMINI_API_KEY. Chép .env.example thành .env rồi điền key."
        )
