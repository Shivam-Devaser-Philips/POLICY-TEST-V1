# Policy Intelligence Platform — Documentation

**Overview**
- Prototype Streamlit app to compare two policy documents (PDF/DOCX), detect Added/Deleted/Modified/Unchanged clauses, analyze impact, perform semantic search, and produce reports (PDF/Excel).
- Modular Python code: parser, embeddings, comparison, analytics, rag, reports, and Streamlit `app.py` frontend.

**Requirements**
- Python 3.10+ (3.14 used during development)
- Virtual environment recommended
- Key packages (see `requirements.txt`): streamlit, sentence-transformers, faiss-cpu, pymupdf, python-docx, pandas, numpy, plotly, reportlab, scikit-learn, groq, openpyxl, python-dotenv, torch, torchvision

**Setup**
1. Create and activate venv (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

3. Copy and edit `.env`:

```powershell
copy .env.example .env
# then edit .env to add GROQ_API_KEY and adjust model names
```

**Run**

```powershell
python -m streamlit run .\app.py
```

Open the Streamlit UI in the browser (URL shown in terminal).

**Key Files & Structure**
- `app.py` — Streamlit UI and page routing (Upload, Dashboard, Comparison, Search, Chatbot, Reports).
- `parser.py` — extract text from PDF/DOCX and split into clauses.
- `embeddings.py` — load Sentence-Transformers model and compute embeddings.
- `rag.py` — vector store (FAISS), search helpers, LLM prompt builders, and `query_llm` wrapper for Groq.
- `comparison.py` — semantic matching of clauses and change classification.
- `analytics.py` — impact classification, stakeholder mapping, section summaries, recommendations.
- `reports.py` — export PDF / Excel reports.
- `scripts/compile_check.py` — helper to run `py_compile` across modules.

**Environment Variables**
- `GROQ_API_KEY` — required for LLM features (RAG chat, section question generation). If unset, the app runs in limited mode.
- `GROQ_MODEL_NAME` — Groq chat model name (default in `.env.example`).
- `EMBEDDING_MODEL_NAME` — sentence-transformers model used for embeddings (default `all-MiniLM-L6-v2`).

**New Features (Agent-driven dashboard)**
- Dashboard now shows both Old and New section summaries side-by-side.
- You can select a section and click `Generate section review questions` to have the LLM (Groq) produce focused review questions for that section. The prompt includes both old and new section contexts.
- Generated questions are stored per-section in session state for quick review.

**How the LLM is used**
- `rag.query_llm(...)` calls Groq's chat completions API when `GROQ_API_KEY` is present.
- `rag.build_chat_prompt(...)` prepares RAG prompts for general Q&A using retrieved clauses.
- `rag.build_section_question_prompt(section, old_ctx, new_ctx)` builds a prompt asking the LLM to produce review questions for a given section.

**Troubleshooting**
- ImportError: `python-dotenv` — ensure `python-dotenv` is installed (`pip install python-dotenv`) or set env vars in your shell. `app.py` now handles missing `dotenv` gracefully.
- ImportError: `torchvision`/`torch` — `transformers` may import vision components requiring `torch`/`torchvision`. Install appropriate CPU/CUDA wheel from https://pytorch.org/get-started/locally and then re-run `pip install -r requirements.txt`.
- Stale imports in Streamlit: If you edit modules and Streamlit still reports import errors, stop the server (Ctrl+C), clear cache (`python -m streamlit cache clear`), and restart Streamlit.

**Developer notes**
- Added `build_section_question_prompt` to `rag.py` and extended `app.py` to return old/new section summaries and contexts from `process_documents`.
- `analytics.summarize_by_section` now accepts a `section_key` to compute summaries for either `old_section` or `new_section`.
- Session state keys added in `app.py`: `old_section_summary`, `new_section_summary`, `old_section_contexts`, `new_section_contexts`, `selected_section`, `section_questions`.
- Use `scripts/compile_check.py` to run a quick syntax check using the venv Python.

**Next steps & improvements**
- Add unit tests for `comparison.py` and `analytics.py`.
- Add caching and partial re-processing for very large documents.
- Add pagination and advanced filtering to the comparison table.
- Improve LLM prompt templates and add safety/content filters for generated output.

**Contact / Ownership**
- Prototype authored in this workspace. For changes, modify the corresponding module and run `scripts/compile_check.py` before starting Streamlit.

---
Generated on 2026-06-11
