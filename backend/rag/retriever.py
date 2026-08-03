"""Retriever: tim top-k doan gan nhat voi cau hoi (cosine)."""

from __future__ import annotations

import math


def cosine(a: list[float], b: list[float]) -> float:
    if not a or not b:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def top_k(query_vec: list[float], chunk_vecs: list[list[float]], k: int = 3) -> list[int]:
    """Tra ve chi so cac chunk co diem cosine cao nhat (top k)."""
    scored = [(i, cosine(query_vec, v)) for i, v in enumerate(chunk_vecs)]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [i for i, _ in scored[:k]]
