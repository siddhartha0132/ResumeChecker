"""
RAG routes — knowledge base management, vector store stats, talent pool search
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.rag.vector_store import get_vector_store
from app.rag.knowledge_base import ingest_knowledge_base
from app.rag.retriever import retrieve_ev_context, retrieve_talent_pool

router = APIRouter(prefix="/api/rag", tags=["RAG / Knowledge Base"])


# ── Models ────────────────────────────────────────────────────────────────────

class SearchRequest(BaseModel):
    query: str
    role_type: Optional[str] = ""
    n: Optional[int] = 3


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/ingest", summary="Ingest EV knowledge base into ChromaDB")
async def ingest_kb(force: bool = Query(False, description="Re-ingest even if already done")):
    """
    **Ingest EV industry guidelines** into the ChromaDB knowledge base.

    This must be run at least once before RAG-enhanced scoring works.
    Includes guidelines for: Battery, Powertrain, Charging, ADAS, Embedded, Resume Best Practices.
    """
    result = await ingest_knowledge_base(force=force)
    return {**result, "timestamp": datetime.now().isoformat()}


@router.get("/stats", summary="Vector store collection statistics")
async def rag_stats():
    """Returns the number of documents in each ChromaDB collection."""
    store = get_vector_store()
    stats = store.stats()
    return {
        **stats,
        "knowledge_base_ready": stats["knowledge_chunks"] > 0,
        "timestamp": datetime.now().isoformat(),
    }


@router.post("/search/knowledge", summary="Search the EV knowledge base")
async def search_knowledge(req: SearchRequest):
    """
    **Semantic search** over the EV industry knowledge base.
    Returns the most relevant guideline chunks for a query.
    """
    context = retrieve_ev_context(req.query, req.role_type or "", req.n or 3)
    if not context:
        raise HTTPException(
            status_code=404,
            detail="Knowledge base is empty. Call POST /api/rag/ingest first.",
        )
    return {
        "query": req.query,
        "role_type": req.role_type,
        "context": context,
        "timestamp": datetime.now().isoformat(),
    }


@router.post("/search/resumes", summary="Semantic search over stored resumes")
async def search_resumes(req: SearchRequest):
    """
    **Semantic search** over all resumes stored in the vector store.
    Useful for finding candidates similar to a job description.
    """
    store = get_vector_store()
    results = store.search_similar_resumes(req.query, n=req.n or 5)
    return {
        "query": req.query,
        "results": results,
        "total_found": len(results),
        "timestamp": datetime.now().isoformat(),
    }


@router.post("/search/talent-pool", summary="Search the shortlisted talent pool")
async def search_talent_pool(req: SearchRequest):
    """
    **Search the talent pool** for candidates matching a new job description.
    Only shortlisted candidates are in the talent pool.
    """
    results = retrieve_talent_pool(req.query, n=req.n or 5)
    return {
        "query": req.query,
        "results": results,
        "total_found": len(results),
        "timestamp": datetime.now().isoformat(),
    }


@router.delete("/clear", summary="Clear all ChromaDB collections (dev utility)")
async def clear_rag():
    """⚠️ Deletes all vectors from all collections. Use with caution."""
    store = get_vector_store()
    # Re-create collections by deleting and recreating
    store.client.delete_collection("resumes")
    store.client.delete_collection("job_descriptions")
    store.client.delete_collection("ev_knowledge")
    store.client.delete_collection("talent_pool")
    # Reinitialise
    store.resumes     = store.client.get_or_create_collection("resumes",     metadata={"hnsw:space": "cosine"})
    store.jobs        = store.client.get_or_create_collection("job_descriptions", metadata={"hnsw:space": "cosine"})
    store.knowledge   = store.client.get_or_create_collection("ev_knowledge", metadata={"hnsw:space": "cosine"})
    store.talent_pool = store.client.get_or_create_collection("talent_pool", metadata={"hnsw:space": "cosine"})
    return {"success": True, "message": "All RAG collections cleared", "timestamp": datetime.now().isoformat()}
