from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import faiss
import numpy as np

from app.core.config import get_settings


EMBED_DIM = 384


@dataclass
class DocumentHit:
    title: str
    snippet: str
    source_ref: str


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _resolve_data_path(rel_path: str) -> Path:
    return (_project_root() / rel_path).resolve()


def _chunk_text(text: str, chunk_size: int = 450, overlap: int = 80) -> list[str]:
    if len(text) <= chunk_size:
        return [text]
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = max(end - overlap, 0)
    return chunks


def _embed_text(text: str, dim: int = EMBED_DIM) -> np.ndarray:
    # Deterministic local embedding for MVP so ingestion/retrieval works without paid embedding API.
    vector = np.zeros(dim, dtype=np.float32)
    for token in text.lower().split():
        digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
        idx = int(digest[:8], 16) % dim
        vector[idx] += 1.0
    norm = np.linalg.norm(vector)
    if norm > 0:
        vector /= norm
    return vector


def _load_meta(meta_path: Path) -> list[dict]:
    if not meta_path.exists():
        return []
    return json.loads(meta_path.read_text(encoding="utf-8"))


def ingest_documents(documents_dir: Path | None = None) -> int:
    settings = get_settings()
    index_path = _resolve_data_path(settings.faiss_index_path)
    meta_path = _resolve_data_path(settings.faiss_meta_path)

    source_dir = documents_dir or (_project_root() / "data" / "documents")
    if not source_dir.exists():
        return 0

    vectors: list[np.ndarray] = []
    metadata: list[dict] = []

    for file_path in sorted(source_dir.glob("*.txt")):
        content = file_path.read_text(encoding="utf-8")
        for idx, chunk in enumerate(_chunk_text(content)):
            vectors.append(_embed_text(chunk))
            metadata.append(
                {
                    "title": file_path.stem.replace("_", " ").title(),
                    "snippet": chunk[:280],
                    "source_ref": f"local://{file_path.name}#chunk-{idx}",
                }
            )

    if not vectors:
        return 0

    matrix = np.vstack(vectors).astype(np.float32)
    index = faiss.IndexFlatIP(EMBED_DIM)
    index.add(matrix)

    index_path.parent.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(index_path))
    meta_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return len(metadata)


def retrieve_documents(query: str, k: int = 3) -> list[DocumentHit]:
    settings = get_settings()
    index_path = _resolve_data_path(settings.faiss_index_path)
    meta_path = _resolve_data_path(settings.faiss_meta_path)

    if not index_path.exists() or not meta_path.exists():
        ingested = ingest_documents()
        if ingested == 0:
            return []

    index = faiss.read_index(str(index_path))
    metadata = _load_meta(meta_path)
    if not metadata:
        return []

    query_vec = _embed_text(query).reshape(1, -1)
    _scores, indices = index.search(query_vec, min(k, len(metadata)))

    hits: list[DocumentHit] = []
    for index_value in indices[0]:
        if index_value < 0 or index_value >= len(metadata):
            continue
        item = metadata[index_value]
        hits.append(
            DocumentHit(
                title=item["title"],
                snippet=item["snippet"],
                source_ref=item["source_ref"],
            )
        )

    return hits
