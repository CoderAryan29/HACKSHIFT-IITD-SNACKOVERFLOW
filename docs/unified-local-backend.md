# Unified local backend

The local development API is hosted by `workspace-app/core_api/main.py`. It mounts the market/prices, crop-disease, Firebase account, and agent-chat routes in one FastAPI process on port `8000`.

## Configure local credentials

From the repository root, make a private root `.env` based on `.env.example`. Configure:

- `DATABASE_URL` for the Supabase/PostgreSQL database used by the core API and agent.
- `GOOGLE_API_KEY` for Gemini agent responses.
- `FIREBASE_PROJECT_ID` and `FIREBASE_SERVICE_ACCOUNT_PATH` for backend verification of Firebase ID tokens. Keep the service-account JSON outside Git; `.gitignore` excludes common service-account filenames.
- Optional `KISANSETU_TFLITE_MODEL_PATH` and `KISANSETU_TFLITE_LABELS_PATH` only if the existing Hugging Face cache is not available to the server process. The API never downloads a model.

The Firebase service-account project must match the Firebase web project. In Firebase Console, enable Google as a sign-in provider and add `localhost` to authorized domains. Copy the Firebase **web app** configuration values into `workspace-frontend/.env.local` using `workspace-frontend/.env.example` as a template. Those `VITE_FIREBASE_*` values are browser configuration; the service-account credential is server-only.

Apply `workspace-app/supabase/migrations/002_agent_threads.sql` and `workspace-app/supabase/migrations/003_user_questionnaire.sql` to the configured Supabase database after the existing initial schema. The authenticated account setup endpoint creates the selected Farmer/Buyer row in `users`; chat threads reference that user. The optional questionnaire stores preferred name, phone, state/district, farmer crop and land details or buyer interests, and whether onboarding is complete.

Precise location is opt-in. The questionnaire only requests browser geolocation after the user presses its location button and grants permission. Coordinates are stored in the existing `users.lat` and `users.lng` columns; the user can skip location or remove saved coordinates. Location accuracy depends on the user's device and browser.

## Disease model details

The service reuses `animeshakr/plant-disease-efficientnetv2s` from the local Hugging Face cache: `model_float16_quant.tflite` and its `class_indices.json` label mapping. The current machine's cache resolves to `C:\Users\ASUS\.cache\huggingface\hub\models--animeshakr--plant-disease-efficientnetv2s\snapshots\5965b98c122f28b3154241e9d6d10b7a367cac0f\`; cache locations and snapshot IDs vary by machine.

The existing inference code converts the uploaded image to RGB, resizes it to `384 × 384`, converts pixels directly to a `float32` batch shaped `[1, 384, 384, 3]` (no additional scaling or normalization), and reads the model's `float32 [1, 38]` output scores. The script ranks those scores directly; it does not apply another softmax. The checked sample's output scores summed to approximately `1.0`. This is the model's score for that image, not a guarantee of real-world accuracy.

## Install and run

Run these in PowerShell from the repository root.

Terminal 1 — one FastAPI process:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements-unified.in
.\venv\Scripts\python.exe -m uvicorn core_api.main:app --app-dir workspace-app --host 127.0.0.1 --port 8000 --reload
```

If the root virtual environment does not exist yet:

```powershell
py -3.13 -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements-unified.in
```

Terminal 2 — frontend:

```powershell
Set-Location workspace-frontend
npm install
npm run dev
```

Open the Vite URL printed in the terminal (normally `http://localhost:5173`; port `5174` is also allowed by the default CORS configuration). For a different Vite port, add that exact origin to `KISANSETU_CORS_ORIGINS` in the root `.env` and restart the API. API documentation is at `http://127.0.0.1:8000/docs`.

## Unified route map

- `GET /health` — core status and agent/model readiness summary.
- `GET /health/db` — database connectivity check.
- `GET /health/ml` — disease-model readiness; returns `503` when the model or dependencies are unavailable.
- `POST /predict` — multipart image field `file`; keeps the existing TFLite prediction response.
- Existing `/prices`, `/mandis`, and market-data endpoints — mounted from `workspace-app/core_api`.
- `GET /auth/profile` and `PUT /auth/profile` — Firebase-ID-token-protected account lookup and Farmer/Buyer role setup.
- `PUT /auth/questionnaire` — save optional role-specific profile details and complete onboarding; GPS coordinates are only stored when the user explicitly requests location and submits the form.
- `POST /agent/v1/chat` — Firebase-ID-token-protected SSE chat; the server derives `user_uid` from the verified token, never from the request body.

The API starts in degraded mode if the local model assets cannot be loaded, so market and agent routes can remain available. The health response reports the model load error and `/predict` returns a clear `503`; no alternate model or fabricated prediction is used. Agent requests also require a working database and `GOOGLE_API_KEY`.
