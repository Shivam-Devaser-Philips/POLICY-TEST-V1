#!/usr/bin/env python3
"""
Run py_compile on project modules using the active Python interpreter.

Usage:
  - Activate your virtualenv in PowerShell:
      .\.venv\Scripts\Activate.ps1
  - Run the script:
      python .\scripts\compile_check.py

This uses `sys.executable` so it will run with the currently active Python (venv recommended).
"""
import sys
import subprocess

FILES = [
    "parser.py",
    "embeddings.py",
    "comparison.py",
    "analytics.py",
    "rag.py",
    "reports.py",
    "app.py",
]


def main():
    exe = sys.executable
    print(f"Using python executable: {exe}")
    errors = False
    for f in FILES:
        print(f"Compiling {f} ...", end=" ")
        try:
            subprocess.check_call([exe, "-m", "py_compile", f])
            print("OK")
        except subprocess.CalledProcessError as e:
            print(f"FAILED (exit {e.returncode})")
            errors = True
        except FileNotFoundError:
            print("MISSING")
            errors = True

    if errors:
        print("One or more files failed to compile.")
        sys.exit(1)

    print("All files compiled successfully.")


if __name__ == "__main__":
    main()
