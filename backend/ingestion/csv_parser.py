import pandas as pd
def parse_csv_bytes(b: bytes, bank_hint: str|None=None) -> pd.DataFrame:
    df = pd.read_csv(pd.io.common.BytesIO(b))
    cols = {c.lower(): c for c in df.columns}
    date_col = next((cols[k] for k in cols if "date" in k), None)
    desc_col = next((cols[k] for k in cols if "descr" in k or "narr" in k or "details" in k), None)
    amt_col  = next((cols[k] for k in cols if "amount" in k or "value" in k), None)
    bal_col  = next((cols[k] for k in cols if "bal" in k), None)
    if not (date_col and desc_col and amt_col):
        raise ValueError("CSV must include date, description, amount columns")
    out = pd.DataFrame({
        "tx_date": pd.to_datetime(df[date_col], errors="coerce"),
        "description": df[desc_col].astype(str),
        "amount": pd.to_numeric(df[amt_col].astype(str).str.replace(',', ''), errors="coerce"),
        "balance_after": pd.to_numeric(df[bal_col].astype(str).str.replace(',', ''), errors="coerce") if bal_col else None
    }).dropna(subset=["tx_date","amount"])
    out["direction"] = out["amount"].apply(lambda x: "credit" if x > 0 else "debit")
    return out
