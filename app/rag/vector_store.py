"""
ChromaDB vector store for RAG pipeline.
Manages 4 collections: resumes, job_descriptions, ev_knowledge, talent_pool
"""

import os
from typing import List, Dict, Optional
from datetime import datetime

import chromadb
from chromadb.config import Settings as ChromaSettings

# ── Paths ─────────────────────────────────────────────────────────────────────
CHROMA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "chroma_db")
CHROMA_DIR = os.path.abspath(CHROMA_DIR)
os.makedirs(CHROMA_DIR, exist_ok=True)

# ── Embedding model (local, free, fast) — lazy load ──────────────────────────
_EMBED_MODEL = None

def _get_embedder():
    global _EMBED_MODEL
    if _EMBED_MODEL is None:
        from sentence_transformers import SentenceTransformer
        _EMBED_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    return _EMBED_MODEL


class ResumeVectorStore:
    """
    ChromaDB-backed vector store.
    Collections:
      - resumes        : parsed resume texts
      - job_descriptions: JD texts
      - ev_knowledge   : EV industry guidelines (RAG context)
      - talent_pool    : shortlisted candidates for re-matching
    """

    def __init__(self):
        self.client = chromadb.PersistentClient(path=CHROMA_DIR)
        self.embedder = _get_embedder()

        # Create / open collections
        self.resumes = self.client.get_or_create_collection(
            name="resumes", metadata={"hnsw:space": "cosine"}
        )
        self.jobs = self.client.get_or_create_collection(
            name="job_descriptions", metadata={"hnsw:space": "cosine"}
        )
        self.knowledge = self.client.get_or_create_collection(
            name="ev_knowledge", metadata={"hnsw:space": "cosine"}
        )
        self.talent_pool = self.client.get_or_create_collection(
            name="talent_pool", metadata={"hnsw:space": "cosine"}
        )

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _embed(self, text: str) -> List[float]:
        return self.embedder.encode(text, show_progress_bar=False).tolist()

    def _chunk_text(self, text: str, size: int = 800, overlap: int = 150) -> List[str]:
        words = text.split()
        chunks, i = [], 0
        while i < len(words):
            chunks.append(" ".join(words[i : i + size]))
            i += size - overlap
        return chunks

    def _fmt(self, results: dict) -> List[Dict]:
        out = []
        if not results.get("ids") or not results["ids"][0]:
            return out
        for idx in range(len(results["ids"][0])):
            out.append(
                {
                    "id": results["ids"][0][idx],
                    "document": (results.get("documents") or [[]])[0][idx] if results.get("documents") else "",
                    "metadata": (results.get("metadatas") or [[]])[0][idx] if results.get("metadatas") else {},
                    "similarity": 1.0 - (results.get("distances") or [[0]])[0][idx],
                }
            )
        return out

    # ── Resumes ───────────────────────────────────────────────────────────────

    def add_resume(self, resume_id: str, text: str, metadata: Dict) -> str:
        """Upsert a resume into the vector store."""
        self.resumes.upsert(
            ids=[resume_id],
            embeddings=[self._embed(text[:2000])],
            documents=[text[:2000]],
            metadatas=[{k: str(v) for k, v in metadata.items()}],
        )
        return resume_id

    def search_similar_resumes(self, query: str, n: int = 5) -> List[Dict]:
        """Find resumes semantically similar to a query."""
        try:
            results = self.resumes.query(
                query_embeddings=[self._embed(query)],
                n_results=min(n, max(self.resumes.count(), 1)),
                include=["documents", "metadatas", "distances"],
            )
            return self._fmt(results)
        except Exception:
            return []

    # ── Job Descriptions ──────────────────────────────────────────────────────

    def add_job(self, job_id: str, text: str, metadata: Dict) -> str:
        self.jobs.upsert(
            ids=[job_id],
            embeddings=[self._embed(text[:2000])],
            documents=[text[:2000]],
            metadatas=[{k: str(v) for k, v in metadata.items()}],
        )
        return job_id

    # ── Knowledge Base ────────────────────────────────────────────────────────

    def add_knowledge_doc(self, doc_id: str, text: str, metadata: Dict) -> str:
        """Chunk and store an EV knowledge document."""
        chunks = self._chunk_text(text)
        for i, chunk in enumerate(chunks):
            cid = f"{doc_id}_chunk_{i}"
            self.knowledge.upsert(
                ids=[cid],
                embeddings=[self._embed(chunk)],
                documents=[chunk],
                metadatas=[{**{k: str(v) for k, v in metadata.items()}, "chunk": str(i)}],
            )
        return doc_id

    def search_knowledge(self, query: str, n: int = 3) -> List[str]:
        """Retrieve relevant EV guidelines for RAG context."""
        try:
            count = self.knowledge.count()
            if count == 0:
                return []
            results = self.knowledge.query(
                query_embeddings=[self._embed(query)],
                n_results=min(n, count),
                include=["documents"],
            )
            return results["documents"][0] if results.get("documents") else []
        except Exception:
            return []

    def knowledge_count(self) -> int:
        return self.knowledge.count()

    # ── Talent Pool ───────────────────────────────────────────────────────────

    def add_to_talent_pool(self, candidate_id: str, text: str, metadata: Dict) -> str:
        self.talent_pool.upsert(
            ids=[candidate_id],
            embeddings=[self._embed(text[:2000])],
            documents=[text[:2000]],
            metadatas=[{k: str(v) for k, v in metadata.items()}],
        )
        return candidate_id

    def search_talent_pool(self, query: str, n: int = 5) -> List[Dict]:
        try:
            count = self.talent_pool.count()
            if count == 0:
                return []
            results = self.talent_pool.query(
                query_embeddings=[self._embed(query)],
                n_results=min(n, count),
                include=["documents", "metadatas", "distances"],
            )
            return self._fmt(results)
        except Exception:
            return []

    # ── Stats ─────────────────────────────────────────────────────────────────

    def stats(self) -> Dict:
        return {
            "resumes": self.resumes.count(),
            "job_descriptions": self.jobs.count(),
            "knowledge_chunks": self.knowledge.count(),
            "talent_pool": self.talent_pool.count(),
        }


# ── Singleton ─────────────────────────────────────────────────────────────────
_store: Optional[ResumeVectorStore] = None

def get_vector_store() -> ResumeVectorStore:
    global _store
    if _store is None:
        _store = ResumeVectorStore()
    return _store
