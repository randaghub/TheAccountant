import uuid, pandas as pd, io

from ingestion.detect import detect_ext
from ingestion.csv_parser import parse_csv_bytes
from ingestion.pdf_extractor import extract_pdf_transactions
from normalization.normalizer import normalize_df
from classification.classifier import classify_transactions
from coa.mapper import apply_coa
from statements.builder import build_statements
from kpi.engine import compute_kpis
from narrative.writer import build_summary_text
from export.exporter_mem import export_pack_bytes

def process_file(file_bytes: bytes, ext: str, file_id: str, client_id: str, period_start: str|None, period_end: str|None, bank_hint: str|None=None):
    if detect_ext(ext) == "csv":
        df = parse_csv_bytes(file_bytes, bank_hint=bank_hint)
    elif detect_ext(ext) == "pdf":
        df = extract_pdf_transactions(io.BytesIO(file_bytes))
    else:
        raise ValueError("Unsupported file type")

    df = normalize_df(df)
    classified = classify_transactions(df, client_id=client_id)
    ledger = apply_coa(classified)
    statements = build_statements(ledger, period_start, period_end)
    kpis = compute_kpis(statements, ledger)
    summary_text = build_summary_text(statements, kpis)

    report_pack_id = str(uuid.uuid4())
    artifacts = export_pack_bytes(report_pack_id, df, statements, kpis, summary_text)
    return {"id": report_pack_id, "artifacts": artifacts}
