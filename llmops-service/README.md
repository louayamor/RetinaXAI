# RetinaXAI LLMOps Service

LLMOps service for report generation with RAG, built for RetinaXAI.

## Installation

```bash
pip install -e .
```

## Usage

```bash
# Start server
python main.py serve

# Run reindex
python main.py pipeline
```

## API Endpoints

- `GET /health` - Health check
- `GET /api/rag/status` - RAG index status
- `POST /api/rag/reindex` - Trigger RAG reindex
- `POST /api/generate` - Generate report