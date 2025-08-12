import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from io import BytesIO

def export_pack_bytes(report_pack_id: str, raw_df: pd.DataFrame, statements, kpis, summary_text: str):
    artifacts = {}

    buf_csv = BytesIO()
    raw_df.to_csv(buf_csv, index=False)
    artifacts["raw.csv"] = buf_csv.getvalue()

    buf_xlsx = BytesIO()
    with pd.ExcelWriter(buf_xlsx, engine="xlsxwriter") as writer:
        raw_df.to_excel(writer, sheet_name="Raw", index=False)
        statements["trial_balance"].to_excel(writer, sheet_name="TrialBalance", index=False)
        statements["income_statement"].to_excel(writer, sheet_name="IncomeStatement", index=False)
        statements["balance_sheet"].to_excel(writer, sheet_name="BalanceSheet", index=False)
        statements["cash_flow"].to_excel(writer, sheet_name="CashFlow", index=False)
        pd.DataFrame([kpis]).to_excel(writer, sheet_name="KPIs", index=False)
    artifacts["financials.xlsx"] = buf_xlsx.getvalue()

    buf_pdf = BytesIO()
    _write_pdf_summary(buf_pdf, summary_text)
    artifacts["executive_summary.pdf"] = buf_pdf.getvalue()

    return artifacts

def _write_pdf_summary(buf, text: str):
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4; margin = 2*cm; x = margin; y = height - margin
    c.setFont("Helvetica-Bold", 14); c.drawString(x, y, "Executive Financial Summary (AI Draft)"); y -= 14*1.2
    c.setFont("Helvetica", 10)
    for line in text.splitlines():
        for chunk in _wrap(line, 100):
            if y < margin: c.showPage(); y = height - margin; c.setFont("Helvetica", 10)
            c.drawString(x, y, chunk); y -= 12
    c.showPage(); c.save()
    buf.seek(0)

def _wrap(s: str, width: int):
    words = s.split(); line = []; length = 0
    for w in words:
        if length + len(w) + 1 > width:
            yield " ".join(line); line = [w]; length = len(w) + 1
        else:
            line.append(w); length += len(w) + 1
    if line: yield " ".join(line)
