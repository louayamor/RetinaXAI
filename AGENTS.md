# RetinaXAI Repository Guide

## Purpose
RetinaXAI is a modular diabetic retinopathy platform with four services:
- `backend-service`: FastAPI API, PostgreSQL, auth, persistence, orchestration
- `frontend-service`: Next.js dashboard
- `mlops-service`: imaging + clinical ML pipelines, OCR, training, evaluation
- `llmops-service`: RAG/report generation

## Core Architecture Rules
- Database is the source of truth for structured data.
- `shared/` holds blobs only: images, outputs, model artifacts, vectorstore.
- Never commit patient data from `shared/ocr_reports/`.
- Prompts belong in `prompts/`, not inline in Python.
- DR grades are ordinal (0-4); do not use plain `CrossEntropyLoss` for grade modeling.
- Keep ingestion and retrieval separate in RAG workflows.

## Repo Layout
- `backend-service/backend-service/`
- `frontend-service/`
- `mlops-service/mlops-service/`
- `llmops-service/llmops-service/`
- `shared/`
- `infra/infra/`

## Build, Lint, Test

### Backend
```bash
cd backend-service/backend-service
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
pytest
pytest tests/test_auth.py
pytest tests/test_auth.py -k login
```

### MLOps
```bash
cd mlops-service/mlops-service
python -m venv .venv
source .venv/bin/activate
pip install -r ../requirements.txt
python main.py pipeline
python main.py serve
pytest
pytest tests/test_ocr_pipeline.py
pytest tests/test_ocr_pipeline.py -k report
```

### LLMOps
```bash
cd llmops-service/llmops-service
python -m venv .venv
source .venv/bin/activate
pip install -r ../requirements.txt
uvicorn app.main:app --reload --port 8002
pytest
pytest tests/test_retriever.py
pytest tests/test_retriever.py -k ingest
```

### Frontend
```bash
cd frontend-service
npm install
npm run dev
npm run build
npm run lint
npm run lint:strict
npm run format:check
```

## Single-Test Patterns
- Pytest file: `pytest path/to/test_file.py`
- Pytest test function: `pytest path/to/test_file.py -k test_name`
- Async tests: ensure `pytest-asyncio` is available and use `@pytest.mark.asyncio`.
- Frontend single file lint: `npx eslint src/path/file.tsx`

## Python Style
For detailed tooling commands (pyright, ruff, pytest, debugging), see `python-dev-tools` skill.

- Prefer ASCII unless existing files already use Unicode.
- Use explicit imports; avoid wildcard imports.
- Keep imports ordered: stdlib, third-party, local.
- Use `pathlib.Path` instead of string paths.
- Type all public functions, return values, and config objects.
- Prefer `Optional[T]` / `T | None` only when a value can truly be absent.
- Use Pydantic for request/response schemas and config validation.
- Use dataclasses for pipeline config objects.
- Use `loguru` for service logs; keep messages structured and concise.
- Raise service-specific exceptions; avoid bare `except:`.
- Never hide failures with silent fallback unless the behavior is intentional and logged.

## Python Naming Conventions
- Modules/files: `snake_case.py`
- Classes: `PascalCase`
- Functions/variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Use descriptive names for ML artifacts and paths (`checkpoint_path`, `feature_file`).

## Backend Conventions
- Use FastAPI dependency injection.
- Keep routes thin; move business logic into services.
- Repositories should own database access.
- Use async SQLAlchemy sessions correctly; no global session objects.
- Put auth-sensitive data in the database, not in the frontend.

## MLOps Conventions
- Keep stage scripts separate by pipeline phase.
- Use config-driven paths from `config/config.yaml`, `params.yaml`, `schema.yaml`.
- Do not hardcode artifact paths in stage logic.
- Persist metadata required for inference alongside model artifacts.
- Imaging uses pretrained EfficientNet-B3 via `timm` for transfer learning.
- Clinical modeling uses XGBoost on tabular OCR features.
- OCR patient identity comes from the report folder name, not OCR text.
- Save region outputs per patient and eye, and keep report-level idempotency.

## Clinical Data Rules
- Standardize gender to `M`/`F`.
- Keep `ocr_patient_id` on backend patient records for linkage.
- Do not infer missing DR grades from silence unless explicitly documented.
- Handle imbalanced classes with weights/sampling, but keep train/eval metadata aligned.

## Frontend Conventions
- Preserve the existing Next.js + shadcn/ui pattern.
- Keep API calls typed and centralized.
- Prefer route names `login` and `register`.
- Avoid introducing a second auth scheme if one already exists.

## File/Data Rules
- Never commit `shared/ocr_reports/`.
- `shared/models/` is for model weights only.
- `shared/outputs/` is for generated artifacts like Grad-CAM.
- `shared/vectorstore/` is for retrieval indexes.
- Keep patient blobs out of the database unless the schema explicitly requires them.

## Change Discipline
- Make the smallest correct change.
- Do not refactor unrelated code while fixing a bug.
- Do not revert user changes unless explicitly asked.
- If a change affects training/inference parity, update both sides.
- Prefer fixing the pipeline stage that creates bad data rather than patching downstream consumers.

## Verification Checklist
- Run the narrowest test that exercises the change.
- Check model/config paths after any refactor.
- Verify OCR outputs and report counts after pipeline changes.
- Verify training metadata and inference metadata match exactly.
- For ML changes, confirm artifacts still load in inference/evaluation.

## Current Important Paths
- Backend app: `backend-service/backend-service/app/`
- MLOps app: `mlops-service/mlops-service/app/`
- LLMOps app: `llmops-service/llmops-service/app/`
- OCR outputs: `mlops-service/mlops-service/artifacts/ocr/output/`
- Shared storage: `/home/louay/RetinaXAI/shared/`

## Notes for Agents
- Prefer `glob`, `grep`, `read`, and `apply_patch` over ad hoc shell parsing.
- Use direct, minimal edits.
- Keep explanations factual and brief.
- If a command or path is uncertain, inspect the repo instead of guessing.

## Skills
Skills are installed globally in `~/.config/opencode/skills/`. Use the `skill` tool to load them on demand.

### Python Development
- `python-dev-tools`: pyright, ruff, pytest, debugging workflows (triggers on: "pyright", "ruff", "pytest", "test", "debug", "type check")

### RetinaXAI Skills
- `retinaxai-development`: core implementation patterns and repo-specific constraints
- `retinaxai-review`: review checklist for security, DR grading, and HIPAA-sensitive data
- `retinaxai-debug`: troubleshooting for backend, MLOps, and LLMOps failures
- `retinaxai-git`: branch, commit, and PR conventions
- `retinaxai-testing`: test structure, fixtures, mocking, and single-test commands
- `retinaxai-deploy`: Docker, Kubernetes, environment, and secrets guidance

### General Skills
- `humanizer`: remove AI writing patterns from text
- `csv-data-summarizer`: analyze CSV files and generate visualizations
- `web-ui`: AI SDK 6 patterns for chat interfaces and agent UIs

When a task matches one of these workflows, consult the matching skill before making changes.

## MCP Servers
MCP servers are configured globally in `~/.config/opencode/opencode.json`. Agents can call these tools directly.

### ui-ux-pro
AI-powered UI/UX design intelligence with 1,920+ curated design resources.

**Available tools:**
- `search_ui_styles`: UI design styles (Glassmorphism, Minimalism, etc.)
- `search_colors`: Color palettes by industry
- `search_typography`: Font pairings with Google Fonts
- `search_charts`: Chart types for dashboards
- `search_ux_guidelines`: UX best practices, WCAG
- `search_icons`: Lucide icons
- `search_landing`: Landing page patterns
- `search_products`: Product design by industry
- `search_prompts`: AI prompt templates
- `search_stack`: Framework-specific guidelines (React, Vue, Next.js, etc.)
- `search_all`: Unified search across all domains
- `get_design_system`: Generate complete design systems

**Use when:** building or styling frontend components, choosing colors/fonts/layouts, or implementing UI/UX best practices.
