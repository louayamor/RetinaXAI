# RetinaXAI

![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=fff)
![Next.js](https://img.shields.io/badge/Next.js-000000?logo=next.js&logoColor=fff)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=fff)
![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?logo=kubernetes&logoColor=fff)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-38B2AC?logo=tailwind-css&logoColor=fff)

---

## Project Overview

**RetinaXAI** is a modular AI platform designed for **automated diabetic retinopathy detection and analysis**.
It combines **MLOps pipelines** for image-based diagnostics with **LLMOps** for generating contextual medical insights.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           RetinaXAI Architecture                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐              │
│  │   Frontend   │────▶│   Backend    │────▶│  PostgreSQL  │              │
│  │  (Next.js)   │     │  (FastAPI)   │     │  (Database)  │              │
│  │   :3000      │     │    :8000     │     │    :5432     │              │
│  └──────────────┘     └──────┬───────┘     └──────────────┘              │
│                              │                                             │
│            ┌─────────────────┼─────────────────┐                         │
│            │                 │                 │                          │
│            ▼                 ▼                 ▼                          │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐            │
│  │  MLOps Svc   │     │  LLMOps Svc  │     │   Shared/    │            │
│  │   :8001      │     │    :8002     │     │   (Blobs)    │            │
│  └──────────────┘     └──────────────┘     └──────────────┘            │
│                                                         │                 │
│  shared/                                               │                 │
│  ├── uploads/fundus/   ← Images                       │                 │
│  ├── uploads/oct/      ← OCT Scans                    │                 │
│  ├── outputs/gradcam/  ← Visualizations               │                 │
│  ├── models/           ← Model weights                │                 │
│  └── vectorstore/      ← ChromaDB                     │                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Upload**: Frontend → Backend saves image to `shared/uploads/`
2. **Predict**: Backend → MLOps reads image, returns prediction
3. **Store**: Backend → PostgreSQL stores structured prediction record
4. **Generate**: Backend → LLMOps generates report from prediction
5. **Output**: MLOps → Grad-CAM saved to `shared/outputs/`

---

## Folder Structure

```
retinaxai/
├── backend-service/        # FastAPI REST API (port 8000)
├── frontend-service/       # Next.js dashboard (port 3000)
├── mlops-service/         # ML training & inference (port 8001)
├── llmops-service/        # RAG/LLM report generation (port 8002)
├── shared/                # Shared blob storage
│   ├── uploads/           # Raw input images
│   ├── outputs/           # Generated artifacts
│   ├── models/            # Trained model weights
│   └── vectorstore/       # ChromaDB vector embeddings
├── infra/                 # Docker, Kubernetes configs
│   ├── docker-compose.yml
│   └── k8s/
└── README.md
```

---

## Storage Strategy

| Data Type | Storage | Reason |
|-----------|---------|--------|
| Raw images | `shared/uploads/` | Large binaries |
| Grad-CAM outputs | `shared/outputs/` | Generated artifacts |
| Model weights | `shared/models/` | Large files |
| Vector embeddings | `shared/vectorstore/` | ChromaDB collection |
| Predictions | PostgreSQL | Structured, queryable |
| Reports | PostgreSQL | Audit trail, searchable |
| Patient records | PostgreSQL | Relational data |

**Database is source of truth. File system holds blobs.**

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI, Python, Pydantic v2, SQLAlchemy |
| Frontend | Next.js 16, TypeScript, Tailwind CSS, shadcn/ui |
| ML | PyTorch, timm, XGBoost, MLflow, DVC |
| LLM | LangChain, ChromaDB, Ollama |
| Database | PostgreSQL 16 |
| Infrastructure | Docker, Docker Compose, Kubernetes |

---

## Getting Started

### Docker Compose (Recommended)

```bash
cd infra/infra
docker-compose up -d
```

Services will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- MLOps API: http://localhost:8001
- LLMOps API: http://localhost:8002
- API Docs: http://localhost:8000/docs

### Manual Setup

```bash
# Backend
cd backend-service/backend-service
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# MLOps
cd mlops-service
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.api.main:app --reload --port 8001

# LLMOps
cd llmops-service
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8002

# Frontend
cd frontend-service
npm install
npm run dev
```

---

## Environment Variables

### Backend (`backend-service/.env`)
```env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/retinaxai
SECRET_KEY=your-secret-key
ML_SERVICE_URL=http://localhost:8001
LLM_SERVICE_URL=http://localhost:8002
ML_SERVICE_API_KEY=your-ml-api-key
LLM_SERVICE_API_KEY=your-llm-api-key
```

### MLOps (`mlops-service/.env`)
```env
SHARED_DIR=/home/louay/RetinaXAI/shared
FUNDUS_DIR=/home/louay/RetinaXAI/shared/uploads/fundus
MODEL_DIR=/home/louay/RetinaXAI/shared/models
```

---

## Contributing

1. Create a branch from `dev` for your feature
2. Implement your feature in the relevant service
3. Open a pull request to `dev`
4. Ensure tests pass and code is linted

### Branch Naming
```
feat/backend-scan-endpoint
fix/mlops-ordinal-loss
chore/infra-postgres-healthcheck
```

### Commit Format
```
<type>(<scope>): <description>

feat(mlops): add ordinal transformation stage
fix(backend): resolve JWT expiration handling
```

---

## License

This project is licensed under the MIT License.

---

## Contact

**Louay Amor** – [GitHub](https://github.com/louayamor) – [Email](mailto:amor.louay20@gmail.com)
