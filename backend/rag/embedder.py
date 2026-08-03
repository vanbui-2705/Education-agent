"""Embedding van ban.

Mac dinh dung phuong phap local (hash-based, khong can API key) de test offline.
Khi co OPENAI_API_KEY, chuyen sang embedding that qua core/llm.py.
"""

from __future__ import annotations

import hashlib
import re
from core.llm import build_llm


def _local_embed(text: str, dim: int = 256) -> list[float]:
    """Embedding deterministic: token-frequency vector tu vocab bam.
    Khong phai semantic that, chi de test offline + retrieval co ban."""
    vec = [0.0] * dim
    toks = re.findall(r"\w+", text.lower())
    for t in toks:
        h = int(hashlib.md5(t.encode("utf-8")).hexdigest(), 16)
        idx = h % dim
        vec[idx] += 1.0
    # chuan hoa
    norm = sum(v * v for v in vec) ** 0.5
    if norm > 0:
        vec = [v / norm for v in vec]
    return vec


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Tra ve list embedding. Dung local neu khong co key that."""
    try:
        llm = build_llm()
        if hasattr(llm, "embed"):
            return llm.embed(texts)
    except Exception:
        pass
    return [_local_embed(t) for t in texts]


def embed_query(text: str) -> list[float]:
    return embed_texts([text])[0]
