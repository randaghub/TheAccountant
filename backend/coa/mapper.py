import json, os, pandas as pd
COA_PATH = os.path.join("coa","coa_map.json")
with open(COA_PATH,"r") as f:
    COA = json.load(f)

def apply_coa(df: pd.DataFrame) -> pd.DataFrame:
    codes, sides = [], []
    for _, row in df.iterrows():
        m = COA.get(row.get("category","Uncategorized"),{}).get(row.get("subcategory","Uncategorized"))
        if m is None: m = COA["Uncategorized"]["Uncategorized"]
        codes.append(m["code"]); sides.append(m["side"])
    out = df.copy()
    out["account_code"], out["account_side"] = codes, sides
    return out
