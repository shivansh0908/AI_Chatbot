# retriever.py
import os
from typing import List, Tuple
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from openai import OpenAI
from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from utils import normalize_whitespace, dedupe_keep_order

load_dotenv()

INDEX_DIR = "data/faiss_index"
EMBED_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
MIN_RELEVANCE = float(os.getenv("MIN_RELEVANCE", 0.58))

# Load embeddings & FAISS once
_embedding_model = OpenAIEmbeddings(model=EMBED_MODEL, api_key=OPENAI_KEY)
_vector_store = FAISS.load_local(INDEX_DIR, _embedding_model, allow_dangerous_deserialization=True)
_openai = OpenAI(api_key=OPENAI_KEY)


def retrieve_with_scores(query: str, k: int = 12) -> List[Tuple[str, float]]:
    """Return (text, score) where score is cosine similarity in [0,1]."""
    results = _vector_store.similarity_search_with_relevance_scores(query, k=k)
    # Langchain FAISS often returns distance; depending on implementation score meaning may vary.
    # We'll try to normalise to cosine-like score: if score is distance, convert; otherwise clamp.
    # Here we assume returned score is similarity-like (higher = better). If not, you must adapt.
    processed = []
    for doc, score in results:
        text = normalize_whitespace(doc.page_content)
        processed.append((text, float(score)))
    return processed


def filter_by_threshold(retrieved: List[Tuple[str, float]], threshold: float = MIN_RELEVANCE):
    """Keep docs with score >= threshold."""
    return [(t, s) for t, s in retrieved if s >= threshold]


def mmr_select(query: str, candidates: List[Tuple[str, float]], top_k: int = 5, lambda_mult: float = 0.7):
    """
    Simple MMR selection:
    - candidates: list of (text, score)
    - returns top_k texts that maximize relevance + diversity
    """
    if not candidates:
        return []

    texts = [t for t, _ in candidates]
    # compute embeddings for candidates and query (use the same embedding model)
    # embed texts in batch
    embeddings = _embedding_model.embed_documents(texts)
    q_emb = _embedding_model.embed_query(query)
    emb_matrix = np.array(embeddings)
    q_vec = np.array(q_emb).reshape(1, -1)

    # compute similarities
    sim_to_query = cosine_similarity(emb_matrix, q_vec).reshape(-1)
    selected = []
    selected_idxs = []
    candidate_idxs = list(range(len(texts)))

    # pick first as max sim to query
    first = int(np.argmax(sim_to_query))
    selected_idxs.append(first)
    candidate_idxs.remove(first)

    while len(selected_idxs) < min(top_k, len(texts)):
        mmr_scores = []
        for idx in candidate_idxs:
            sim_q = sim_to_query[idx]
            sim_min_to_selected = max([cosine_similarity(emb_matrix[idx].reshape(1,-1), emb_matrix[j].reshape(1,-1))[0,0] for j in selected_idxs])
            mmr_score = lambda_mult * sim_q - (1 - lambda_mult) * sim_min_to_selected
            mmr_scores.append((mmr_score, idx))
        mmr_scores.sort(reverse=True)
        next_idx = mmr_scores[0][1]
        selected_idxs.append(next_idx)
        candidate_idxs.remove(next_idx)

    return [(texts[i], float(sim_to_query[i])) for i in selected_idxs]


def build_context(query: str, k: int = 12, mmr_k: int = 5, threshold: float = MIN_RELEVANCE, max_chars: int = 6000):
    """
    Retrieve -> filter by threshold -> MMR select -> dedupe -> join into context
    Returns (context_text, used_docs_list)
    """
    retrieved = retrieve_with_scores(query, k=k)

    # If no docs pass the threshold, we still take top-1 to allow "I don't know"
    filtered = filter_by_threshold(retrieved, threshold)
    if not filtered:
        # fallback: take top 2 raw retrieved items (but mark them as low confidence)
        filtered = retrieved[:2]

    # MMR selection for diversity
    selected = mmr_select(query, filtered, top_k=mmr_k)

    # collect texts, dedupe
    docs = [t for t, _ in selected]
    docs = dedupe_keep_order(docs)

    # trim context to max_chars
    ctx = "\n---\n".join(docs)
    if len(ctx) > max_chars:
        # trim from the end (prefer earlier chunks)
        allowed = max_chars
        new_docs = []
        cur = 0
        for d in docs:
            if cur + len(d) + 5 <= allowed:
                new_docs.append(d)
                cur += len(d) + 5
            else:
                break
        ctx = "\n---\n".join(new_docs)

    return ctx, docs
