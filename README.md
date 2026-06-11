# POLICY-TEST-V1

Policy Intelligence Platform prototype for comparing policy documents, analyzing changes, performing semantic search, and generating reports.

## Overview

This repository contains a Streamlit-based prototype for comparing two policy documents (PDF/DOCX), detecting added, deleted, modified, and unchanged clauses, analyzing impact, generating section summaries, running semantic search, and asking AI-assisted questions using Groq.

## Folder Structure

- `.env` / `.env.example` — environment configuration for API keys and model names.
- `.gitignore` — ignored files and directories.
- `.venv/` — local virtual environment (not tracked by version control).
- `analytics.py` — impact classification, section summaries, stakeholder mapping, and recommendation helpers.
- `app.py` — main Streamlit application, page routing, UI components, filters, pagination, and session state.
- `comparison.py` — clause matching and classification logic used to compare old/new policy content.
- `data/` — storage location for sample or uploaded document assets used during development.
- `documentation.md` — detailed developer documentation for features, setup, and architecture.
- `embeddings.py` — embedding model loader and clause vectorization utilities.
- `parser.py` — document extraction and clause splitting for PDF and DOCX inputs.
- `rag.py` — FAISS vector store, semantic search helpers, prompt builders, and Groq LLM wrapper.
- `reports.py` — PDF and Excel report generation utilities.
- `requirements.txt` — Python package dependencies.
- `scripts/` — helper scripts for syntax validation and module import checks.
- `outputs/` — optional location for generated reports and exported files.
- `vector_store/` — optional location for cached embeddings or vector artifacts.

## Setup

1. Create and activate the Python virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and configure keys:

```powershell
copy .env.example .env
```

Edit `.env` and add your `GROQ_API_KEY` and optional model names.

## Run

```powershell
python -m streamlit run .\app.py
```

The Streamlit UI will open in your browser at the local URL shown in the terminal.

## Core Features

- Upload and compare old/new policy documents in PDF or DOCX format.
- Detect Added, Deleted, Modified, and Unchanged policy clauses.
- Score and label impact severity for each change.
- Generate both executive and section-level summaries.
- Perform semantic search over policy clauses using FAISS embeddings.
- Use Groq-based RAG for question answering and section review question generation.
- Export filtered comparison results to CSV.

## Environment Variables

- `GROQ_API_KEY` — required for AI-assisted features.
- `GROQ_MODEL_NAME` — optional Groq model name.
- `EMBEDDING_MODEL_NAME` — sentence transformer model name (default `all-MiniLM-L6-v2`).

## Troubleshooting

- If the app cannot find `python-dotenv`, install it with `pip install python-dotenv` or set environment variables directly in the shell.
- If the app fails due to `torch` or `torchvision`, install the correct PyTorch wheel from https://pytorch.org/get-started/locally and then re-run `pip install -r requirements.txt`.
- If Streamlit shows stale or cached imports after code changes, stop the server with `Ctrl+C`, clear cache with `python -m streamlit cache clear`, and restart.

## Notes

- This repository is a prototype. The code is designed for extension with unit tests, larger document caching, and production-ready validation.
- Use `scripts/compile_check.py` to run a quick syntax check across the Python modules.
