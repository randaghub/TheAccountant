import pandas as pd
def normalize_df(df: pd.DataFrame) -> pd.DataFrame:
    required = ["tx_date","description","amount","direction"]
    for c in required:
        if c not in df.columns: raise ValueError(f"Missing column: {c}")
    df["description"] = df["description"].astype(str).str.replace(r"\s+"," ", regex=True).str.strip()
    return df.sort_values("tx_date").reset_index(drop=True)
