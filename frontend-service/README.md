<h1 align="center">RetinaXAI — Frontend Service</h1>

<div align="center">Explainable AI dashboard for diabetic retinopathy detection, built for clinicians.</div>

<br />

<div align="center">
  <img src="/public/shadcn-dashboard.png" alt="RetinaXAI Dashboard" style="max-width: 100%; border-radius: 8px;" />
</div>

<p align="center">
  <img src="https://img.shields.io/badge/Next.js-16-black" alt="Next.js" />
  <img src="https://img.shields.io/badge/TypeScript-5-blue" alt="TypeScript" />
  <img src="https://img.shields.io/badge/Tailwind_CSS-v4-38bdf8" alt="Tailwind CSS" />
  <img src="https://img.shields.io/badge/shadcn--ui-components-black" alt="shadcn/ui" />
  <img src="https://img.shields.io/badge/license-MIT-green" alt="MIT License" />
</p>

---

## Overview

RetinaXAI is a production-grade clinical dashboard for managing patients, uploading retinal scans, running ML-based diabetic retinopathy predictions, and generating LLM-powered diagnostic reports — all with Grad-CAM explainability baked in.

This frontend service connects to the [RetinaXAI Backend Service](../backend-service) — a FastAPI REST API backed by PostgreSQL, an ML inference service, and an LLM report generation service.

```
Doctor (Browser)
    │
    ▼
Next.js Frontend (this service)
    │
    ▼
FastAPI Backend ──► ML Service (predictions + Grad-CAM)
                ──► LLM Service (diagnostic reports)
                ──► PostgreSQL (patients, scans, predictions, reports)
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | Next.js 16 (App Router) |
| Language | TypeScript 5 |
| Auth | FastAPI JWT (Bearer tokens) |
| Styling | Tailwind CSS v4 |
| Components | shadcn/ui |
| Forms | React Hook Form + Zod |
| Tables | TanStack Table v8 + Nuqs |
| Charts | Recharts |
| State | Zustand |
| Command palette | kbar |
| Linting | ESLint + Prettier |
| Pre-commit | Husky |

---

## Pages

| Page | Route | Description |
|---|---|---|
| Sign In | `/auth` | JWT login wired to `POST /api/v1/auth/login` |
| Register | `/auth/register` | Doctor registration via `POST /api/v1/auth/register` |
| Overview | `/dashboard/overview` | Patient stats, prediction volume, severity distribution charts |
| Patients | `/dashboard/patients` | Patient list with search, filter, pagination |
| Patient Detail | `/dashboard/patients/[id]` | Patient info, scan history, linked predictions |
| Upload Scans | `/dashboard/patients/[id]/scans` | Upload left/right fundus scans |
| Predictions | `/dashboard/predictions` | All predictions with DR severity grades |
| Prediction Detail | `/dashboard/predictions/[id]` | Grad-CAM overlay, class probabilities, confidence scores |
| Reports | `/dashboard/reports/[id]` | LLM-generated diagnostic report per prediction |
| Monitoring | `/dashboard/monitoring` | Model performance metrics, data drift, Prometheus stats |
| Profile | `/dashboard/profile` | Doctor account settings |

---

## Project Structure

```
src/
├── app/
│   ├── auth/                        # Login + Register pages
│   ├── dashboard/
│   │   ├── overview/                # Parallel route charts (area, bar, pie)
│   │   ├── patients/                # Patient list + detail + scan upload
│   │   ├── predictions/             # Prediction list + Grad-CAM detail
│   │   ├── reports/                 # LLM report view
│   │   ├── monitoring/              # Model metrics + drift
│   │   └── profile/                 # User profile
│   └── layout.tsx
├── components/
│   ├── ui/                          # shadcn/ui primitives
│   └── layout/                      # Sidebar, header, page container
├── features/
│   ├── auth/                        # Login/register views + JWT form
│   ├── patients/                    # Patient table, form, detail
│   ├── predictions/                 # Prediction table, Grad-CAM viewer
│   ├── reports/                     # Report view + generate action
│   ├── monitoring/                  # Metrics charts + drift panels
│   └── overview/                    # Dashboard summary charts
├── lib/
│   ├── api.ts                       # FastAPI HTTP client
│   └── auth.ts                      # JWT token helpers
├── hooks/                           # Custom hooks
├── types/                           # TypeScript types matching backend schemas
└── middleware.ts                    # Protected route enforcement
```

---

## Getting Started

### Prerequisites

- Node.js 20+ or Bun
- RetinaXAI backend service running on `http://localhost:8000`

### Installation

```bash
git clone https://github.com/louayamor/retinaxai.git
cd retinaxai/frontend-service

bun install

```

### Environment Variables

Edit `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Run

```bash
bun dev
```

Open `http://localhost:3000`. The app will redirect to `/auth` if no JWT token is present.

---

## Authentication

This service uses **JWT Bearer token authentication** against the FastAPI backend — no third-party auth provider.

- Login sends `application/x-www-form-urlencoded` as required by FastAPI's `OAuth2PasswordRequestForm`
- Access token stored in `localStorage`, sent as `Authorization: Bearer <token>` on all API requests
- `middleware.ts` enforces protected routes at the Edge — unauthenticated requests are redirected to `/auth`

---

## Backend API

Full API reference is in the [backend-service README](../backend-service/README.md).

| Method | Endpoint | Used by |
|---|---|---|
| POST | `/api/v1/auth/register` | Register page |
| POST | `/api/v1/auth/login` | Login page |
| GET/POST | `/api/v1/patients/` | Patient list + create |
| GET | `/api/v1/patients/{id}` | Patient detail |
| POST | `/api/v1/patients/{id}/scans` | Scan upload |
| POST | `/api/v1/predictions/` | Run prediction |
| GET | `/api/v1/predictions/{id}` | Prediction detail + Grad-CAM |
| POST | `/api/v1/reports/` | Generate LLM report |
| GET | `/api/v1/reports/{id}` | View report |
| GET | `/metrics` | Monitoring page |
| GET | `/health` | Navbar status indicator |

---

## License

MIT