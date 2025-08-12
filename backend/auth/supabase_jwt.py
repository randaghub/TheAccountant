import os, httpx, time
from jose import jwt

SUPABASE_URL = os.getenv("SUPABASE_URL","").rstrip("/")
JWKS_CACHE = {"exp": 0, "keys": None}

async def _get_jwks():
    global JWKS_CACHE
    now = int(time.time())
    if JWKS_CACHE["keys"] and JWKS_CACHE["exp"] > now:
        return JWKS_CACHE["keys"]
    url = f"{SUPABASE_URL}/auth/v1/keys"
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(url)
    r.raise_for_status()
    data = r.json()
    JWKS_CACHE = {"exp": now + 3600, "keys": data}
    return data

async def verify_jwt(token: str):
    jwks = await _get_jwks()
    header = jwt.get_unverified_header(token)
    kid = header.get("kid")
    key = next((k for k in jwks["keys"] if k["kid"] == kid), None)
    if not key:
        raise ValueError("JWKS key not found")
    claims = jwt.decode(token, key, algorithms=[key.get("alg","RS256")], audience=None, options={"verify_aud": False})
    return claims
