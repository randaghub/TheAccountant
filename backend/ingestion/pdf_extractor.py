import pdfplumber, re, pandas as pd, fitz, pytesseract
from PIL import Image
from io import BytesIO

DATE_PATTERNS = [r"\b\d{4}-\d{2}-\d{2}\b", r"\b\d{2}/\d{2}/\d{4}\b", r"\b\d{2}-\d{2}-\d{4}\b"]
AMOUNT_PATTERN = r"[-+]?\d{1,3}(?:,\d{3})*(?:\.\d{2})?"

def _parse_lines_to_df(lines):
    rows = []
    for ln in lines:
        date_match = None
        for p in DATE_PATTERNS:
            m = re.search(p, ln)
            if m: date_match = m.group(0); break
        am = re.findall(AMOUNT_PATTERN, ln.replace(" ", ""))
        amt = None
        if am:
            try: amt = float(am[-1].replace(",",""))
            except: pass
        if date_match and amt is not None:
            desc = re.sub(AMOUNT_PATTERN, "", ln.replace(date_match, "")).strip()
            tx_date = pd.to_datetime(date_match, dayfirst=True, errors="coerce")
            if pd.notna(tx_date):
                rows.append({"tx_date": tx_date, "description": desc, "amount": amt})
    df = pd.DataFrame(rows)
    if not df.empty:
        df["direction"] = df["amount"].apply(lambda x: "credit" if x>0 else "debit")
    return df

def extract_pdf_transactions(file_obj) -> pd.DataFrame:
    try:
        lines = []
        with pdfplumber.open(file_obj) as pdf:
            for p in pdf.pages:
                t = p.extract_text() or ""
                for ln in t.splitlines():
                    if ln.strip(): lines.append(ln.strip())
        df = _parse_lines_to_df(lines)
        if not df.empty: return df
    except Exception:
        pass
    file_obj.seek(0)
    doc = fitz.open(stream=file_obj.read(), filetype="pdf")
    lines = []
    for page in doc:
        pix = page.get_pixmap(dpi=200)
        img = Image.open(BytesIO(pix.tobytes("png")))
        text = pytesseract.image_to_string(img)
        for ln in text.splitlines():
            if ln.strip(): lines.append(ln.strip())
    return _parse_lines_to_df(lines)
