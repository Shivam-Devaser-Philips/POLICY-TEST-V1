import io
import re
from typing import Dict, List

import fitz
import docx
import pandas as pd


def extract_text_pdf(file_bytes: bytes) -> str:
    document = fitz.open(stream=file_bytes, filetype="pdf")
    text_pages = []
    for page in document:
        text = page.get_text().strip()
        if text:
            text_pages.append(text)
    return "\n\n".join(text_pages)


def extract_text_docx(file_bytes: bytes) -> str:
    document = docx.Document(io.BytesIO(file_bytes))
    paragraphs = []
    for paragraph in document.paragraphs:
        text = paragraph.text.strip()
        if text:
            paragraphs.append(text)
    return "\n\n".join(paragraphs)


def load_document(uploaded_file) -> str:
    if uploaded_file is None:
        return ""

    file_bytes = uploaded_file.read()
    file_type = uploaded_file.type
    if uploaded_file.name.lower().endswith(".pdf") or file_type == "application/pdf":
        raw_text = extract_text_pdf(file_bytes)
    elif uploaded_file.name.lower().endswith(".docx") or file_type in [
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword",
    ]:
        raw_text = extract_text_docx(file_bytes)
    else:
        raise ValueError("Unsupported file type. Please upload PDF or DOCX.")

    return clean_text(raw_text)


def clean_text(text: str) -> str:
    lines = [line.strip() for line in text.splitlines()]
    filtered = [line for line in lines if line and not line.isspace()]
    cleaned = "\n".join(filtered)
    cleaned = re.sub(r"\n{2,}", "\n\n", cleaned)
    return cleaned


def split_into_clauses(text: str) -> pd.DataFrame:
    if not text:
        return pd.DataFrame(columns=["section", "clause"])

    raw_clauses: List[Dict[str, str]] = []
    current_section = "General"
    buffer: List[str] = []

    lines = text.splitlines()
    section_pattern = re.compile(r"^\s*((?:\d+\.)+\d*|Section\s+\d+|[A-Z][A-Za-z ]{2,})[:\.]?\s*")

    for line in lines:
        candidate = line.strip()
        if not candidate:
            continue

        section_match = section_pattern.match(candidate)
        if section_match:
            if buffer:
                raw_clauses.append({"section": current_section, "clause": " ".join(buffer).strip()})
                buffer = []
            current_section = section_match.group(1).strip()
            remainder = candidate[section_match.end():].strip()
            if remainder:
                buffer.append(remainder)
            continue

        if len(candidate) < 160 and candidate.endswith(":"):
            if buffer:
                raw_clauses.append({"section": current_section, "clause": " ".join(buffer).strip()})
                buffer = []
            current_section = candidate.rstrip(":")
            continue

        if len(candidate.split(" ")) <= 6 and candidate.endswith("."):
            if buffer:
                raw_clauses.append({"section": current_section, "clause": " ".join(buffer).strip()})
                buffer = []
            raw_clauses.append({"section": current_section, "clause": candidate})
            continue

        buffer.append(candidate)

    if buffer:
        raw_clauses.append({"section": current_section, "clause": " ".join(buffer).strip()})

    df = pd.DataFrame(raw_clauses)
    if df.empty:
        return df

    df["section"] = df["section"].fillna("General")
    df["clause"] = df["clause"].astype(str)
    return df
