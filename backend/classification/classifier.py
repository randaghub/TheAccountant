import re, json, os, pandas as pd
from classification.overrides import load_overrides

RULES_PATH = os.path.join("classification","rules.json")
with open(RULES_PATH,"r") as f:
    RULES = json.load(f)

def classify_transactions(df: pd.DataFrame, client_id: str) -> pd.DataFrame:
    over = load_overrides(client_id)
    cats, subs, confs = [], [], []
    for desc in df["description"].astype(str).tolist():
        cat, sub, conf = "Uncategorized","Uncategorized",0.0
        for patt, dest in over.items():
            if re.search(patt, desc, flags=re.IGNORECASE):
                cat, sub, conf = dest["category"], dest["subcategory"], 0.99
                break
        else:
            for rule in RULES:
                if re.search(rule["pattern"], desc, flags=re.IGNORECASE):
                    cat, sub, conf = rule["category"], rule["subcategory"], rule["confidence"]
                    break
        cats.append(cat); subs.append(sub); confs.append(conf)
    out = df.copy()
    out["category"], out["subcategory"], out["classification_confidence"] = cats, subs, confs
    return out
