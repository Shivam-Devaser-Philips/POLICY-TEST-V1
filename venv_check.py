import importlib
pkgs = ['sentence_transformers','faiss','fitz','docx','reportlab','openpyxl','streamlit']
for p in pkgs:
    print(p, 'OK' if importlib.util.find_spec(p) else 'MISSING')
