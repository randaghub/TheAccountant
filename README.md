# TheAccountant — Free-Tier Online Deployment Patch

This adds a full **frontend + backend** to run on **Vercel (free)** + **Render (free)** with **Supabase Storage** (free).

## Deploy steps
- Create Supabase project, bucket `reports` (private). Grab `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`.
- Deploy `backend/` on Render:
  - Build: `pip install -r requirements.txt`
  - Start: `uvicorn api.main:app --host 0.0.0.0 --port 8000`
  - ENV: `APP_ENV=production`, `FRONTEND_ORIGIN=https://<vercel-app>`, `SUPABASE_URL=...`, `SUPABASE_SERVICE_ROLE_KEY=...`, `MAX_FILE_MB=25`
- Deploy `frontend/` on Vercel:
  - ENV: `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`, `NEXT_PUBLIC_BACKEND_URL=https://<render-backend>`
- Open Vercel app, upload CSV/PDF, download artifacts.

## Notes
- Processing is in-memory; artifacts are uploaded to Supabase and returned as **signed URLs**.
- PDF OCR via Tesseract is included in the backend image.
- Extend vendor rules in `backend/classification/rules.json`.
