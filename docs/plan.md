# RetinaXAI Remaining Plan

## LLMOps

### #1 Add RAG ingestion pipeline with offline/online separation
- Add an offline ingestion job that builds or updates the vector store from approved source documents.
- Add an online retrieval path for report generation.
- Keep ingestion and serving separate.
- Expose FastAPI endpoints for reindex/status if needed.
- Add tests for chunking, embeddings, retrieval, and prompt assembly.

## Observability

### #12 Observability: Integrate Metrics & Tracing
- Add Prometheus counters/histograms for request counts, latency, and failures.
- Add OpenTelemetry traces across backend, mlops, and llmops request paths.
- Export metrics and traces from service startup.
- Add health/readiness endpoints where missing.
- Add tests for metric registration and tracing startup.

### #40 Add OpenTelemetry tracing setup
- Add tracing middleware/instrumentation to the backend FastAPI app.
- Add span propagation for service-to-service HTTP calls.
- Configure the exporter through env vars.
- Make tracing work locally without production-only infrastructure.
- Add a smoke test for tracer initialization.

## QA / Testing

### #13 QA: Write Unit & Integration Test Suite
- Fill missing unit tests for backend services and API routes.
- Add integration tests for the main request flows.
- Add shared fixtures for DB/session/client mocking.
- Run lint and tests in CI for all services.
- Document test data and env setup.

### #41 Add shared pytest fixtures
- Done: shared fixtures added in backend and MLOps `tests/conftest.py`.
- Added fixtures for auth/session, API client, temp dirs, and sample payloads.
- Reused the fixtures in backend auth/report tests and MLOps OCR pipeline tests.

### #90 Pytest fixtures for config and dataset mocks
- Add fixtures for config objects, temp paths, and synthetic datasets.
- Mock external services once in a shared location.
- Reuse the fixtures across OCR and training tests.
- Keep fixture names stable and descriptive.

### #91 Unit tests for data ingestion
- Test ingestion stage entrypoints.
- Verify dataset download/copy/skip logic.
- Mock file system and remote dataset access.
- Assert expected output paths and logs.

### #92 Unit tests for preprocessing
- Test preprocessing transforms on sample inputs.
- Cover empty, malformed, and low-quality inputs.
- Assert output schema, shape, and saved artifacts.
- Mock image and file I/O.

### #93 Unit tests for model trainer
- Test model initialization and config wiring.
- Verify logging, checkpointing, and early stopping.
- Mock the training loop to keep tests fast.
- Assert MLflow logging calls and artifact paths.

### #122 Unit tests for ML trainer and feature engineering
- Add tests for structured feature engineering outputs.
- Verify the trainer consumes engineered features correctly.
- Cover feature importance, label mapping, and artifact export.
- Mock fit/predict to keep tests fast.

## Frontend

### #53 Reconfigure sidebar nav and rewire overview dashboard
- Update navigation to match current backend, mlops, and llmops routes.
- Remove dead links and show only working pages.
- Make the overview dashboard show real service status and latest results.
- Ensure sidebar labels match the current product areas.
- Add UI tests or snapshots for nav rendering.

### #54 Build patient management pages
- Build the patient list page from backend `/patients`.
- Add a patient detail view with predictions, reports, and scans.
- Add the scan upload flow tied to backend ingestion.
- Handle empty, loading, and error states.
- Add route guards and permissions.

### #55 Build predictions and Grad-CAM pages
- Build predictions list/detail pages.
- Add Grad-CAM visualization display from backend or MLOps outputs.
- Show model metadata, confidence, and explanation artifacts.
- Handle missing artifacts cleanly.
- Add UI tests for rendered data.

### #56 Build LLM reports and model monitoring pages
- Build a report list/detail page for generated LLM outputs.
- Add a model monitoring page for drift/performance metrics.
- Pull metrics from backend or MLOps endpoints, not local files.
- Show report generation status and history.
- Add loading, error, and empty states.

## Infra / Project Hygiene

- Keep service-local `data/` directories ignored in git.
- Keep docs and templates aligned with actual directory layouts.
- Prefer env-backed paths and service-to-service API calls over shared filesystem coupling.
