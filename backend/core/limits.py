import datetime
from fastapi import HTTPException
from core.supabase_db import get_memberships, get_subscription, get_or_init_usage, increment_usage

def current_month_range():
    today = datetime.date.today()
    start = today.replace(day=1)
    end = (start.replace(month=start.month % 12 + 1, day=1) - datetime.timedelta(days=1)) if start.month != 12 else start.replace(year=start.year+1, month=1, day=1) - datetime.timedelta(days=1)
    return start, end

async def enforce_quota(user_id: str):
    m = await get_memberships(user_id)
    if not m:
        raise HTTPException(status_code=403, detail="No organization membership")
    org_id = m[0]["org_id"]
    sub = await get_subscription(org_id)
    if not sub or sub.get("status") != "active":
        raise HTTPException(status_code=402, detail="Subscription inactive")
    limit = sub.get("monthly_reports_limit", 20)
    start, end = current_month_range()
    usage = await get_or_init_usage(org_id, str(start), str(end))
    if usage["reports_generated"] >= limit:
        raise HTTPException(status_code=402, detail="Monthly report limit reached")
    await increment_usage(org_id, str(start))
    return {"org_id": org_id, "plan_id": sub["plan_id"], "limit": limit, "period_start": str(start), "period_end": str(end)}
