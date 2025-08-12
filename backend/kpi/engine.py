import pandas as pd
from typing import Dict, Any

def compute_kpis(statements: Dict[str, Any], ledger: pd.DataFrame) -> Dict[str, Any]:
    revenue = statements["revenue"]; expenses = statements["expenses"]; net_profit = statements["net_profit"]
    ledger = ledger.copy(); ledger["date"] = pd.to_datetime(ledger["tx_date"], errors="coerce")
    daily = ledger.groupby(ledger["date"].dt.date)["amount"].sum().reset_index(name="net_flow")
    avg_outflows = ledger[ledger["direction"]=="debit"]["amount"].abs().mean() or 0.0
    days_cash = float(ledger["amount"].sum() / avg_outflows) if avg_outflows>0 else None

    overdraft_days = 0
    if "balance_after" in ledger.columns and ledger["balance_after"].notna().any():
        bal = ledger[["date","balance_after"]].dropna()
        overdraft_days = int((bal["balance_after"] < 0).sum())

    return {
        "revenue": float(revenue),
        "expenses": float(expenses),
        "net_profit": float(net_profit),
        "avg_daily_net_flow": float(daily["net_flow"].mean()) if len(daily)>0 else 0.0,
        "days_cash_proxy": days_cash,
        "overdraft_days": overdraft_days,
        "top_expense_categories": _top_expense_categories(ledger),
        "flags": _compute_flags(ledger)
    }

def _top_expense_categories(ledger: pd.DataFrame, n:int=5):
    exp = ledger[ledger["category"]!="Income"]
    g = exp.groupby("category")["amount"].sum().abs().sort_values(ascending=False).head(n)
    return [{"category":k, "total":float(v)} for k,v in g.items()]

def _compute_flags(ledger: pd.DataFrame):
    flags = []
    exp = ledger[ledger["category"]!="Income"].copy()
    if len(exp)>0:
        med = exp.groupby("category")["amount"].apply(lambda s: s.abs().median()).to_dict()
        for _, row in exp.iterrows():
            m = med.get(row["category"], 0.0)
            if m and abs(row["amount"]) > 3*m and abs(row["amount"]) > 1000:
                flags.append({"type":"expense_spike","date":str(row["tx_date"]),"amount":float(row["amount"]),
                              "category":row["category"],"description":row["description"]})
    ledger["weekday"] = pd.to_datetime(ledger["tx_date"], errors="coerce").dt.weekday
    wknd = ledger[ledger["weekday"].isin([5,6])]
    for _, row in wknd.iterrows():
        if abs(row["amount"]) > 5000:
            flags.append({"type":"weekend_high_value","date":str(row["tx_date"]),"amount":float(row["amount"]),
                          "category":row.get("category",""),"description":row.get("description","")})
    return flags
