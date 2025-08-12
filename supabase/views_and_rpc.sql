create or replace view public.app_memberships_view as
  select m.org_id, m.role, u.user_id
  from app.memberships m
  join app.user_profiles u on u.user_id = m.user_id;

create or replace view public.app_subscriptions_view as
  select s.org_id, s.plan_id, s.status,
         p.monthly_reports_limit, s.current_period_start, s.current_period_end
  from app.subscriptions s
  join app.plans p on p.id = s.plan_id;

create or replace function public.increment_usage(p_org_id uuid, p_period_start date)
returns app.usage_reports
language plpgsql
as $$
declare rec app.usage_reports;
begin
  update app.usage_reports
  set reports_generated = reports_generated + 1
  where org_id = p_org_id and period_start = p_period_start
  returning * into rec;
  return rec;
end;
$$;
