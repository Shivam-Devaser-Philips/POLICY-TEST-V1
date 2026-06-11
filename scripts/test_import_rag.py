import sys, traceback
try:
    import rag
    print('OK', rag.__file__)
    print([n for n in dir(rag) if 'build_section' in n])
except Exception:
    traceback.print_exc()
    sys.exit(1)
