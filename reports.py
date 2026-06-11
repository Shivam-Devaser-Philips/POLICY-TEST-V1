import io
import os
from datetime import datetime
from typing import Dict

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def create_pdf_report(
    executive_summary: Dict[str, int],
    section_summary: pd.DataFrame,
    impact_df: pd.DataFrame,
    recommendation_df: pd.DataFrame,
) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = {
        "Heading": ParagraphStyle(
            name="Heading",
            fontSize=16,
            leading=20,
            spaceAfter=12,
            alignment=1,
        ),
        "Normal": ParagraphStyle(name="Normal", fontSize=10, leading=14),
    }

    story = []
    story.append(Paragraph("Policy Intelligence Platform Report", styles["Heading"]))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles["Normal"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Executive Summary", styles["Heading"]))
    story.append(
        Paragraph(
            f"Total clauses analyzed: {executive_summary.get('total_clauses', 0)}. "
            f"Added: {executive_summary.get('added', 0)}. "
            f"Deleted: {executive_summary.get('deleted', 0)}. "
            f"Modified: {executive_summary.get('modified', 0)}. "
            f"Unchanged: {executive_summary.get('unchanged', 0)}.",
            styles["Normal"],
        )
    )
    story.append(Spacer(1, 12))

    story.append(Paragraph("Section Summary", styles["Heading"]))
    section_rows = [["Section", "Added", "Deleted", "Modified", "Unchanged"]]
    for _, row in section_summary.iterrows():
        section_rows.append([row["section"], row["added"], row["deleted"], row["modified"], row["unchanged"]])
    section_table = Table(section_rows, colWidths=[2 * inch, 1 * inch, 1 * inch, 1 * inch, 1 * inch])
    section_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2E86C1")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ]
        )
    )
    story.append(section_table)
    story.append(Spacer(1, 12))

    story.append(Paragraph("Impact Highlights", styles["Heading"]))
    impact_rows = [["Clause", "Impact Level", "Reason"]]
    for _, row in impact_df.head(10).iterrows():
        impact_rows.append([row["new_clause"] or row["old_clause"], row["impact_level"], row["impact_reason"]])
    impact_table = Table(impact_rows, colWidths=[3 * inch, 1.25 * inch, 2.25 * inch])
    impact_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#117A65")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ]
        )
    )
    story.append(impact_table)
    story.append(Spacer(1, 12))

    story.append(Paragraph("Recommendations", styles["Heading"]))
    for _, row in recommendation_df.iterrows():
        story.append(Paragraph(f"- {row['recommendation']} ({row['reason']})", styles["Normal"]))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def create_excel_report(
    comparison_df: pd.DataFrame,
    impact_df: pd.DataFrame,
    recommendation_df: pd.DataFrame,
) -> bytes:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        comparison_df.to_excel(writer, sheet_name="Changes", index=False)
        impact_df.to_excel(writer, sheet_name="Impacts", index=False)
        recommendation_df.to_excel(writer, sheet_name="Recommendations", index=False)
    buffer.seek(0)
    return buffer.getvalue()
