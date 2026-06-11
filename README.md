# POLICY-TEST-V1

Policy Intelligence Platform prototype for comparing policy documents, analyzing changes, performing semantic search, and generating reports.

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

3. Copy `.env.example` to `.env` and set your Groq API key:

```powershell
copy .env.example .env
```

Then edit `.env` and add your `GROQ_API_KEY`.

## Run

```powershell
python -m streamlit run .\app.py
```

## Notes

- The app uses `GROQ_API_KEY`, `GROQ_MODEL_NAME`, and `EMBEDDING_MODEL_NAME` from `.env`.
- If `python-dotenv` is missing, the app will still run, but environment variables should be set in the shell.
