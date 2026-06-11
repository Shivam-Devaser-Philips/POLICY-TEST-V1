import os
from typing import Dict, List, Optional

import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

from embeddings import create_embeddings, load_embedding_model


def build_vector_store(clause_df: pd.DataFrame, model: SentenceTransformer) -> Dict[str, object]:
    texts = clause_df["clause"].fillna("").tolist()
    sections = clause_df["section"].fillna("General").tolist()
    embeddings = create_embeddings(texts, model)
    dim = embeddings.shape[1] if embeddings.ndim == 2 else 0
    index = faiss.IndexFlatIP(dim)
    faiss.normalize_L2(embeddings)
    index.add(embeddings)
    return {
        "index": index,
        "embeddings": embeddings,
        "clauses": texts,
        "sections": sections,
        "data": clause_df.reset_index(drop=True),
    }


def search_vector_store(
    store: Dict[str, object],
    query: str,
    model: SentenceTransformer,
    top_k: int = 5,
) -> pd.DataFrame:
    if query.strip() == "" or store["embeddings"].size == 0:
        return pd.DataFrame(columns=["score", "clause", "section"])
    query_embedding = model.encode([query], convert_to_numpy=True)
    faiss.normalize_L2(query_embedding)
    D, I = store["index"].search(query_embedding, top_k)
    rows = []
    for score, idx in zip(D[0], I[0]):
        if idx < 0 or idx >= len(store["clauses"]):
            continue
        rows.append(
            {
                "score": float(score),
                "clause": store["clauses"][idx],
                "section": store["sections"][idx],
            }
        )
    return pd.DataFrame(rows)


def build_chat_prompt(query: str, retrieved_docs: List[Dict[str, str]]) -> str:
    context_text = "\n\n".join(
        [f"Section: {doc['section']}\nClause: {doc['clause']}" for doc in retrieved_docs]
    )
    prompt = (
        "You are a factual policy assistant. Use ONLY the provided context to answer. Do NOT hallucinate. "
        "If the answer cannot be found in the context, reply exactly: 'Information not found in uploaded policies.' "
        "Be concise and return a short, factual answer.\n\n"
        f"Context:\n{context_text}\n\nQuestion: {query}"
    )
    return prompt


def build_section_question_prompt(section_name: str, old_context: str, new_context: str, num_questions: int = 5) -> str:
    """Build a prompt for generating section-specific review questions."""
    old_text = old_context.strip() or "No old section content available."
    new_text = new_context.strip() or "No new section content available."
    prompt = (
        f"You are a policy review assistant. Using ONLY the provided old and new section content, generate {num_questions} concise, actionable review questions about the changes in the '{section_name}' section. "
        "Focus on compliance, stakeholder impact, implementation steps, and risks. If no changes are present, return a single line: 'No significant changes detected.' Return numbered questions only.\n\n"
        "Old section content:\n"
        f"{old_text}\n\n"
        "New section content:\n"
        f"{new_text}\n\n"
        "Questions:"
    )
    return prompt


def sanitize_llm_output(output: str, max_chars: int = 2000) -> str:
    """
    Basic sanitization and safety filtering for LLM output.
    - Truncates very long outputs
    - Masks explicit PII-like tokens (naive)
    - Blocks outputs containing disallowed keywords and returns a warning instead
    """
    if not isinstance(output, str):
        output = str(output)

    # Truncate
    if len(output) > max_chars:
        output = output[: max_chars - 3] + "..."

    # Naive PII masking: replace common sensitive token strings
    pii_tokens = ["ssn", "social security", "credit card", "card number", "password"]
    lowered = output.lower()
    for token in pii_tokens:
        if token in lowered:
            return "The model output was removed for containing potential sensitive information."

    # Basic disallowed words list (can be extended)
    disallowed = ["kill", "terrorist", "illegal"]
    for bad in disallowed:
        if bad in lowered:
            return "The model produced content that violates safety policies and was removed."

    return output


def query_llm(prompt: str, api_key: str = None, provider: str = "groq", model_name: str = None, endpoint: Optional[str] = None) -> str:
    # Allow explicit api_key or fallback to environment variables for compatibility
    key = api_key or os.getenv("GROQ_API_KEY") or os.getenv("LLM_API_KEY")
    if not key:
        return "LLM is not configured. Provide GROQ_API_KEY in .env to enable AI-assisted answers."

    if provider.lower() == "groq":
        try:
            from groq import Groq
        except Exception:
            return "Groq SDK not installed. Install the `groq` package to enable LLM features."

        client = Groq(api_key=key)
        model = model_name or os.getenv("GROQ_MODEL_NAME") or os.getenv("LLM_MODEL_NAME") or "mixtral-8x7b-32768"
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a policy assistant. Answer only using provided context."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=1024,
                temperature=0.7,
            )
            # Preferred structured response
            if hasattr(response, "choices") and len(response.choices) > 0:
                raw = getattr(response.choices[0].message, "content", str(response))
                return sanitize_llm_output(raw)
            # Fallback for dict-like responses
            if isinstance(response, dict):
                choices = response.get("choices") or []
                if choices:
                    msg = choices[0].get("message") or {}
                    raw = msg.get("content", str(response))
                    return sanitize_llm_output(raw)
            return sanitize_llm_output(str(response))
        except Exception as e:
            return f"Groq request failed: {e}"

    return "LLM provider not supported. Use Groq with LLM_PROVIDER=groq."
