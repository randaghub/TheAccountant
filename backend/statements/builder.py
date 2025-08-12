import pandas as pd
from typing import Optional, Dict, Any

def build_statements(ledger: pd.DataFrame, period_start: Optional[str], period_end: Optional[str]) -> Dict[str, Any]:
    df = ledger.copy()
    if period_start: df = df[df["tx_date"] >= pd.to_datetime(period_start)]
    if period_end:   df = df[df["tx_date"] <= pd.to_datetime(period_end)]
    tb = df.groupby(["account_code","category","subcategory","account_side"], dropna=False)["amount"].sum().reset_index()

    def is_amount(row):
        amt = row["amount"]
        return amt if row["category"]=="Income" else -abs(amt) if row["account_side"]=="D" else amt
    is_df = df.copy()
    is_df["is_amount"] = is_df.apply(is_amount, axis=1)
    is_summary = is_df.groupby("category")["is_amount"].sum().reset_index()
    revenue = is_df[is_df["category"]=="Income"]["is_amount"].sum()
    expenses = is_df[is_df["category"]!="Income"]["is_amount"].sum()
    net_profit = revenue + expenses

    cash = df["amount"].sum()
    bs = pd.DataFrame([
        {"item":"Cash & Equivalents","amount":cash},
        {"item":"Unreconciled/Other","amount":0.0}
    ])
    cfo = is_df[is_df["category"].isin(["Income","Retail","Utilities","Telecom","Fuel","Delivery/Platforms","Banking","Tax","Payroll","Premises","Insurance"]) ]["is_amount"].sum()
    cf = pd.DataFrame([
        {"section":"Operating","amount":cfo},
        {"section":"Investing","amount":0.0},
        {"section":"Financing","amount":0.0},
        {"section":"Net Change in Cash","amount":cfo}
    ])
    return {"trial_balance":tb,"income_statement":is_summary.assign(net_profit=net_profit),
            "balance_sheet":bs,"cash_flow":cf,"period_start":period_start,"period_end":period_end,
            "revenue":float(revenue),"expenses":float(expenses),"net_profit":float(net_profit)}
