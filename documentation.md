# Policy Intelligence Platform — Documentation

**Overview**
- Prototype Streamlit app to compare two policy documents (PDF/DOCX), detect Added/Deleted/Modified/Unchanged clauses, analyze impact, perform semantic search, and produce reports (PDF/Excel).
- Modular Python code: parser, embeddings, comparison, analytics, rag, reports, and Streamlit `app.py` frontend.

**Folder Structure**
- `.env` / `.env.example` — environment variables for Groq and embedding configuration.
- `app.py` — main Streamlit application, page routing, UI, filters, pagination, and session state.
- `parser.py` — document extraction and clause splitting for PDF and DOCX uploads.
- `embeddings.py` — sentence-transformers model loader and clause embedding generation.
- `comparison.py` — old/new clause matching, change classification, and comparison data frame construction.
- `analytics.py` — change impact scoring, section summaries, stakeholder mapping, and recommendation generation.
- `rag.py` — FAISS vector store builder, semantic search helpers, prompt construction, and Groq LLM wrapper.
- `reports.py` — export generation for report outputs, including PDF and Excel files.
- `scripts/compile_check.py` — syntax validation of Python modules.
- `generate_sample_documents.py` — helper for producing sample policy text or documents.
- `data/` — sample or reference document storage for development.
- `outputs/` — generated reports, exports, and application output artifacts.
- `vector_store/` — optional location for serialized vector store or cached embeddings.
- `.venv/` — local virtual environment (should not be committed).

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
- `app.py` — Streamlit UI and page routing (Upload, Dashboard, Comparison, Search, Chatbot, Reports), plus filtering, pagination, and session state.
- `parser.py` — extract text from PDF/DOCX and split into clauses using heuristics and document parsing.
- `embeddings.py` — load Sentence-Transformers model and compute embeddings for clause-level semantic search.
- `rag.py` — build a FAISS vector store, perform semantic search, assemble prompts, and call Groq for RAG question answering and section question generation.
- `comparison.py` — compare old/new clauses, classify changes, and create a structured comparison data frame.
- `analytics.py` — compute change impact levels, classify stakeholder effects, summarize by section, and generate recommendation text.
- `reports.py` — export comparison analysis as PDF and Excel reports, and format outputs for download.
- `scripts/compile_check.py` — quick syntax check for Python files using `py_compile`.
- `generate_sample_documents.py` — optional helper to generate sample policy content for testing.
- `data/` — repository folder for sample documents and development assets.
- `outputs/` — optional output folder for exported reports and generated files.
- `vector_store/` — optional location for storing serialized embeddings or vector indexes.

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
