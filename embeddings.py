import functools
from typing import List

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


@functools.lru_cache(maxsize=1)
def load_embedding_model(model_name: str = "all-MiniLM-L6-v2") -> SentenceTransformer:
    return SentenceTransformer(model_name)


def create_embeddings(texts: List[str], model: SentenceTransformer) -> np.ndarray:
    if not texts:
        return np.zeros((0, model.get_sentence_embedding_dimension()))
    embeddings = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
    return embeddings


def calculate_similarity(query_embedding: np.ndarray, embeddings: np.ndarray) -> np.ndarray:
    if embeddings.size == 0:
        return np.array([])
    scores = cosine_similarity([query_embedding], embeddings)[0]
    return scores
