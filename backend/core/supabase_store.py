import os
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL","")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY","")

def _client() -> Client:
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise RuntimeError("Supabase not configured")
    return create_client(SUPABASE_URL, SUPABASE_KEY)

BUCKET = "reports"

def upload_bytes(key: str, data: bytes):
    s = _client().storage.from_(BUCKET)
    s.upload(key, data, {"content-type":"application/octet-stream", "upsert": True})
    return key

def make_signed_url(key: str, expires_in: int = 60*60):
    s = _client().storage.from_(BUCKET)
    res = s.create_signed_url(key, expires_in)
    return res.get("signedURL") or res.get("signedUrl")
