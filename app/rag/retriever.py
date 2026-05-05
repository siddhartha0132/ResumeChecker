"""
RAG Retriever — fetches relevant context for scoring prompts
"""

from typing import List, Dict
from app.rag.vector_store import get_vector_store


def retrieve_ev_context(query: str, role_type: str = "", n: int = 3) -> str:
    """
    Retrieve relevant EV guidelines from the knowledge base.
    Returns a single concatenated string ready to inject into a prompt.
    """
    store = get_vector_store()

    # Build a richer query combining role and query text
    full_query = f"{role_type} {query}".strip()
    chunks = store.search_knowledge(full_query, n=n)

    if not chunks:
        return ""

    return "\n\n---\n\n".join(chunks)


def retrieve_similar_candidates(query: str, n: int = 3) -> List[Dict]:
    """
    Retrieve similar previously-scored resumes for few-shot context.
    """
    store = get_vector_store()
    return store.search_similar_resumes(query, n=n)


def retrieve_talent_pool(query: str, n: int = 5) -> List[Dict]:
    """
    Search the talent pool for candidates matching a query.
    """
    store = get_vector_store()
    return store.search_talent_pool(query, n=n)
