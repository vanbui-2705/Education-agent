"""Tach van ban thanh cac doan nho (chunk) de embed."""

from __future__ import annotations


def chunk_text(text: str, max_chars: int = 500, overlap: int = 50) -> list[str]:
    """Tach theo doan, uu tien ngat o dau cau/ngat dong. Rất don gian, tieng Viet OK."""
    text = text.strip()
    if not text:
        return []
    chunks = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + max_chars, n)
        # tim diem ngat tot nhat truoc end
        if end < n:
            cut = text.rfind(".", start, end)
            if cut <= start:
                cut = text.rfind("\n", start, end)
            if cut > start:
                end = cut + 1
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= n:
            break
        start = max(end - overlap, start + 1)
    return chunks
