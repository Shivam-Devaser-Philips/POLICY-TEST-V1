import os
from collections import Counter
from typing import Dict, List

import pandas as pd

IMPACT_KEYWORDS = [
    "compliance",
    "regulation",
    "audit",
    "legal",
    "risk",
    "customer",
    "employee benefits",
    "benefits",
    "data",
    "privacy",
    "security",
]

STAKEHOLDER_MAP = {
    "employee": "Employees",
    "hr": "HR",
    "compliance": "Compliance Team",
    "operations": "Operations Team",
    "manager": "Managers",
    "customer": "Customers",
}


def classify_impact(clause_text: str) -> Dict[str, str]:
    text = clause_text.lower()
    if any(keyword in text for keyword in ["compliance", "regulation", "audit", "legal", "risk"]):
        return {"impact_level": "High Impact", "reason": "Policy change affects compliance, legal risk, or regulation."}
    if any(keyword in text for keyword in ["customer", "employee benefits", "security", "privacy"]):
        return {"impact_level": "Medium Impact", "reason": "Policy change affects customers, employee benefits, or data privacy."}
    return {"impact_level": "Low Impact", "reason": "Policy change is operational or administrative in nature."}


def identify_stakeholders(clause_text: str) -> List[Dict[str, str]]:
    text = clause_text.lower()
    stakeholders: List[Dict[str, str]] = []
    for keyword, stakeholder in STAKEHOLDER_MAP.items():
        if keyword in text:
            impact = "High Impact" if keyword in ["compliance", "hr", "manager"] else "Medium Impact"
            stakeholders.append(
                {
                    "stakeholder": stakeholder,
                    "impact_level": impact,
                    "reason": f"Phrase '{keyword}' indicates relevance to {stakeholder}.",
                }
            )
    if not stakeholders:
        stakeholders.append(
            {
                "stakeholder": "Employees",
                "impact_level": "Low Impact",
                "reason": "General policy wording with broad employee impact.",
            }
        )
    return stakeholders


def generate_executive_summary(comparison_df: pd.DataFrame) -> Dict[str, int]:
    counts = comparison_df["change_type"].value_counts().to_dict()
    return {
        "added": int(counts.get("Added", 0)),
        "deleted": int(counts.get("Deleted", 0)),
        "modified": int(counts.get("Modified", 0)),
        "unchanged": int(counts.get("Unchanged", 0)),
        "total_clauses": int(len(comparison_df)),
    }


def summarize_by_section(comparison_df: pd.DataFrame, section_key: str = "new_section") -> pd.DataFrame:
    """
    Summarize changes grouped by a section column.

    Args:
        comparison_df: DataFrame with comparison rows containing `change_type` and section columns.
        section_key: Column to group by (e.g., 'new_section' or 'old_section').

    Returns:
        DataFrame with columns ['section', 'added', 'deleted', 'modified', 'unchanged']
    """
    if comparison_df.empty:
        return pd.DataFrame(columns=["section", "added", "deleted", "modified", "unchanged"])

    if section_key not in comparison_df.columns:
        raise KeyError(f"Section key '{section_key}' not found in comparison_df columns.")

    section_groups = []
    for section, group in comparison_df.groupby(section_key):
        counts = group["change_type"].value_counts().to_dict()
        section_groups.append(
            {
                "section": section or "General",
                "added": int(counts.get("Added", 0)),
                "deleted": int(counts.get("Deleted", 0)),
                "modified": int(counts.get("Modified", 0)),
                "unchanged": int(counts.get("Unchanged", 0)),
            }
        )

    return pd.DataFrame(section_groups).sort_values(by=["added", "modified", "deleted"], ascending=False)


def add_impact_labels(comparison_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in comparison_df.iterrows():
        text = row["new_clause"] or row["old_clause"]
        impact = classify_impact(text)
        stakeholders = identify_stakeholders(text)
        rows.append(
            {
                **row.to_dict(),
                "impact_level": impact["impact_level"],
                "impact_reason": impact["reason"],
                "stakeholders": stakeholders,
            }
        )
    return pd.DataFrame(rows)


def build_recommendations(comparison_df: pd.DataFrame) -> pd.DataFrame:
    recommendations = []
    for _, row in comparison_df.iterrows():
        change_type = row["change_type"]
        clause_text = row["new_clause"] or row["old_clause"]
        if "compliance" in clause_text.lower() or "regulation" in clause_text.lower():
            rec = "Review compliance updates with the legal and compliance teams."
        elif change_type == "Added":
            rec = "Notify affected teams about the new policy clause."
        elif change_type == "Deleted":
            rec = "Confirm that removed policy language is no longer required."
        elif change_type == "Modified":
            rec = "Validate updated policy wording with stakeholders."
        else:
            rec = "Monitor unchanged policy sections for future updates."
        recommendations.append(
            {
                "section": row["new_section"] or row["old_section"],
                "change_type": change_type,
                "recommendation": rec,
                "reason": clause_text[:120],
            }
        )
    return pd.DataFrame(recommendations)
