"""Tien ich xu ly tieng Viet: bo dau de so khop gan dung."""

from __future__ import annotations

import unicodedata


def bo_dau(text: str) -> str:
    """Chuyen tieng Viet ve dang khong dau, viet thuong.

    Dung de tim kiem ten giao vien/ lop khi nguoi dung go thieu dau.
    Vi du: bo_dau('Nguyen Thi Lan') -> 'nguyen thi lan'
    """
    if not text:
        return ""
    nfkd = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in nfkd if not unicodedata.combining(c))
