import os, json
OVERRIDES_DIR = "storage/overrides"
os.makedirs(OVERRIDES_DIR, exist_ok=True)

def _file(client_id: str):
    return os.path.join(OVERRIDES_DIR, f"{client_id}.json")

def load_overrides(client_id: str):
    p = _file(client_id)
    if os.path.exists(p):
        with open(p,"r",encoding="utf-8") as f: return json.load(f)
    return {}
