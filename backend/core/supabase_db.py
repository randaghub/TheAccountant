import os, datetime, httpx

SUPABASE_URL = os.getenv("SUPABASE_URL","").rstrip("/")
SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY","")

def _headers():
    if not SERVICE_KEY or not SUPABASE_URL:
        raise RuntimeError("Supabase not configured (SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY)")
    return {"apikey": SERVICE_KEY, "Authorization": f"Bearer {SERVICE_KEY}", "Content-Type": "application/json"}

def _rest(path):
    return f"{SUPABASE_URL}/rest/v1{path}"

async def get_memberships(user_id: str):
    url = _rest("/app_memberships_view")
    params = {"select": "org_id,role", "user_id": f"eq.{user_id}"}
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(url, headers=_headers(), params=params)
    r.raise_for_status()
    return r.json()

async def get_subscription(org_id: str):
    url = _rest("/app_subscriptions_view")
    params = {"select": "org_id,plan_id,monthly_reports_limit,status,current_period_start,current_period_end", "org_id": f"eq.{org_id}"}
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(url, headers=_headers(), params=params)
    r.raise_for_status()
    arr = r.json()
    return arr[0] if arr else None

async def get_or_init_usage(org_id: str, period_start: str, period_end: str):
    url = _rest("/app_usage_reports")
    params = {"org_id": f"eq.{org_id}", "period_start": f"eq.{period_start}"}
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(url, headers=_headers(), params=params)
    r.raise_for_status()
    items = r.json()
    if items:
        return items[0]
    payload = {"org_id": org_id, "period_start": period_start, "period_end": period_end, "reports_generated": 0}
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.post(url, headers=_headers(), json=payload)
    r.raise_for_status()
    return r.json()[0]

async def increment_usage(org_id: str, period_start: str):
    url = _rest("/rpc/increment_usage")
    payload = {"p_org_id": org_id, "p_period_start": period_start}
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.post(url, headers=_headers(), json=payload)
    r.raise_for_status()
    return r.json()
