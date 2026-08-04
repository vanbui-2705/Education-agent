"""Schema B: tai lieu RAG + ho so hoc sinh (Phan he B - gia su)."""

SCHEMA_B = """-- Schema B: tai lieu RAG + ho so hoc sinh (Phan he B - gia su)
-- Tach biet hoan toan voi Schema A, cung nam trong 1 file DB.
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    mime TEXT NOT NULL DEFAULT 'text/plain',
    status TEXT NOT NULL DEFAULT 'ready',
    meta TEXT
);

CREATE TABLE IF NOT EXISTS document_chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    idx INTEGER NOT NULL,
    text TEXT NOT NULL,
    embedding_blob TEXT,
    FOREIGN KEY (document_id) REFERENCES documents(id)
);

CREATE TABLE IF NOT EXISTS memory_student (
    user_id TEXT PRIMARY KEY,
    profile TEXT NOT NULL DEFAULT '{}'
);
"""
