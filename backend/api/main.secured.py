import os, uuid, io
from fastapi import FastAPI, UploadFile, File, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from core.pipeline import process_file
from core.supabase_store import upload_bytes, make_signed_url
from auth.supabase_jwt import verify_jwt
from core.limits import enforce_quota

APP_ENV = os.getenv("APP_ENV", "development")
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "*")

app = FastAPI(title="TheAccountant API (secured)", version="0.3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN, "*"] if APP_ENV!="production" else [FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ProcessRequest(BaseModel):
    file_id: str
    client_id: str
    period_start: Optional[str] = None
    period_end: Optional[str] = None
    bank_hint: Optional[str] = None

UPLOAD_CACHE = {}

async def get_user(authorization: str = Header(None)):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = authorization.split(" ",1)[1]
    claims = await verify_jwt(token)
    return claims

@app.get("/api/v1/me")
async def me(user=Depends(get_user)):
    return {"user_id": user.get("sub"), "email": user.get("email")}

@app.post("/api/v1/upload")
async def upload(file: UploadFile = File(...), user=Depends(get_user)):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".csv", ".pdf"]:
        raise HTTPException(status_code=400, detail="Only CSV and PDF allowed")
    data = await file.read()
    if len(data) > int(os.getenv("MAX_FILE_MB","25"))*1024*1024:
        raise HTTPException(status_code=400, detail="File too large for free tier")
    file_id = str(uuid.uuid4())
    UPLOAD_CACHE[file_id] = {"ext": ext, "data": data, "user_id": user.get("sub")}
    return {"file_id": file_id, "filename": file.filename}

@app.post("/api/v1/process")
async def process(req: ProcessRequest, user=Depends(get_user)):
    quota = await enforce_quota(user.get("sub"))

    if req.file_id not in UPLOAD_CACHE:
        raise HTTPException(status_code=404, detail="File not found")
    blob = UPLOAD_CACHE.pop(req.file_id)
    if blob["user_id"] != user.get("sub"):
        raise HTTPException(status_code=403, detail="Not your upload")

    report = process_file(
        file_bytes=blob["data"],
        ext=blob["ext"],
        file_id=req.file_id,
        client_id=req.client_id,
        period_start=req.period_start,
        period_end=req.period_end,
        bank_hint=req.bank_hint
    )
    files = {}
    for name, bytes_data in report["artifacts"].items():
        key = f"reports/{req.client_id}/{report['id']}/{name}"
        upload_bytes(key, bytes_data)
        files[name] = make_signed_url(key)
    return {"status":"done", "report_pack_id": report["id"], "downloads": files, "plan": quota["plan_id"]}
