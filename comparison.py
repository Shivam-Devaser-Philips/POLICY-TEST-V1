from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity


def compare_policy_clauses(
    old_df: pd.DataFrame,
    new_df: pd.DataFrame,
    threshold: float = 0.7,
) -> pd.DataFrame:
    old_clauses = old_df["clause"].fillna("").tolist()
    new_clauses = new_df["clause"].fillna("").tolist()

    if not old_clauses and not new_clauses:
        return pd.DataFrame(
            columns=[
                "old_section",
                "old_clause",
                "new_section",
                "new_clause",
                "similarity_score",
                "change_type",
            ]
        )

    if not old_clauses:
        return pd.DataFrame(
            [
                {
                    "old_section": "",
                    "old_clause": "",
                    "new_section": row["section"],
                    "new_clause": row["clause"],
                    "similarity_score": 0.0,
                    "change_type": "Added",
                }
                for _, row in new_df.iterrows()
            ]
        )

    if not new_clauses:
        return pd.DataFrame(
            [
                {
                    "old_section": row["section"],
                    "old_clause": row["clause"],
                    "new_section": "",
                    "new_clause": "",
                    "similarity_score": 0.0,
                    "change_type": "Deleted",
                }
                for _, row in old_df.iterrows()
            ]
        )

    old_embeddings = np.vstack(old_df["embedding"].values)
    new_embeddings = np.vstack(new_df["embedding"].values)
    similarity_matrix = cosine_similarity(old_embeddings, new_embeddings)

    matched_old = set()
    matched_new = set()
    rows: List[Dict] = []

    for old_idx, old_row in old_df.iterrows():
        best_new = int(np.argmax(similarity_matrix[old_idx]))
        best_score = float(similarity_matrix[old_idx, best_new])
        if best_score >= threshold and best_new not in matched_new:
            matched_old.add(old_idx)
            matched_new.add(best_new)
            new_row = new_df.iloc[best_new]
            change_type = "Unchanged" if best_score > 0.92 else "Modified"
            rows.append(
                {
                    "old_section": old_row["section"],
                    "old_clause": old_row["clause"],
                    "new_section": new_row["section"],
                    "new_clause": new_row["clause"],
                    "similarity_score": round(best_score, 3),
                    "change_type": change_type,
                }
            )

    for old_idx, old_row in old_df.iterrows():
        if old_idx in matched_old:
            continue
        rows.append(
            {
                "old_section": old_row["section"],
                "old_clause": old_row["clause"],
                "new_section": "",
                "new_clause": "",
                "similarity_score": 0.0,
                "change_type": "Deleted",
            }
        )

    for new_idx, new_row in new_df.iterrows():
        if new_idx in matched_new:
            continue
        rows.append(
            {
                "old_section": "",
                "old_clause": "",
                "new_section": new_row["section"],
                "new_clause": new_row["clause"],
                "similarity_score": 0.0,
                "change_type": "Added",
            }
        )

    comparison_df = pd.DataFrame(rows)
    comparison_df["change_type"] = pd.Categorical(
        comparison_df["change_type"],
        categories=["Added", "Deleted", "Modified", "Unchanged"],
        ordered=True,
    )
    return comparison_df
