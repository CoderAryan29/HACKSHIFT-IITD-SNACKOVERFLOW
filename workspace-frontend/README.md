# KisanSetu Frontend Prototype

A responsive React + Vite + TypeScript prototype focused on:
- Farmer/buyer marketplace and produce listings
- Buyer offer / bid UI
- Mandi price comparison and net proceeds estimator
- Personalized government scheme profile wizard
- My Farm / khata demo ledger
- Ask KisanSetu chat placeholder
- Crop Health and Legal Aid supporting tools
- Responsive desktop sidebar and mobile bottom navigation
- CSS design tokens, micro-interactions, and reduced-motion support

## Run locally

Requirements: Node.js 18+.

```bash
npm install
npm run dev
```

To check a production build:

```bash
npm run build
```

## Crop Health model API

Crop Health submits the selected image as a multipart `file` to the existing
TFLite inference API. Copy `.env.example` to `.env.local` if the API is not
running at `http://127.0.0.1:8000`, and set `VITE_API_BASE_URL` to the API base
URL. For local development, run the two services in separate PowerShell
terminals:

```powershell
Set-Location 'E:\HACKSHIFT-IITD-SNACKOVERFLOW\workspace-ml'
python -m pip install -r requirements.in
python -m uvicorn ml_service.api:app --host 127.0.0.1 --port 8000
```

```powershell
Set-Location 'E:\HACKSHIFT-IITD-SNACKOVERFLOW\workspace-frontend'
npm install
npm run dev
```

Open `http://127.0.0.1:5173`. The API uses the local Hugging Face cache and
does not download a model at startup. See
[`../workspace-ml/ml_service/README.md`](../workspace-ml/ml_service/README.md)
for model details, response format, cache configuration, and limitations.

## Important prototype notes

This is a frontend prototype, not a production-connected application. Marketplace listings, bids, price points, scheme matches, ledger entries, chat responses and profile details are illustrative demo data. Some official scheme links are provided as entry points, but the app does not verify eligibility or fetch live policy data. No real buyer bid, listing, deal or application is submitted.

Before using real data, integrate the existing KisanSetu API contracts, Firebase authentication and authorized backend routes. Never expose Supabase service-role keys in the browser. Confirm scheme rules and source dates through official sources.

## Existing repository integration

If adding this to the existing KisanSetu monorepo, inspect `workspace-app/web` first and merge the components/styles into that app rather than blindly overwriting existing files. The shared contract files and other teammates' workspace folders should not be modified without coordination.
