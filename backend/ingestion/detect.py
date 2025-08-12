def detect_ext(ext: str) -> str:
    e = ext.lower()
    return 'csv' if e=='.csv' else 'pdf' if e=='.pdf' else 'unknown'
