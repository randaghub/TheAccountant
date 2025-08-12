# TheAccountant — Secured SaaS (Auth + Subscriptions + Limits)

## Supabase
Run `supabase/schema.sql` and `supabase/views_and_rpc.sql` in the SQL Editor. Create bucket `reports` (Private).

## Backend (Render)
Start: `uvicorn api.main.secured:app --host 0.0.0.0 --port 8000`  
Env: `APP_ENV=production`, `FRONTEND_ORIGIN=https://<vercel app>`, `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `MAX_FILE_MB=25`

## Frontend (Vercel)
Env: `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`, `NEXT_PUBLIC_BACKEND_URL`

## Seed one org (SQL)
insert into app.organizations (name) values ('Demo Org') returning id;
insert into app.user_profiles (user_id, email) values ('<user_id>', '<you@email>');
insert into app.memberships (org_id, user_id, role) values ('<org_id>','<user_id>','owner');
insert into app.subscriptions (org_id, plan_id) values ('<org_id>','free')
  on conflict (org_id) do update set plan_id='free', status='active';
