#!/usr/bin/env python
"""LLMOps CLI entry point."""
import os
import sys
from pathlib import Path

root = Path(__file__).parent
os.chdir(root / "llmops-service")
sys.path.insert(0, str(root / "llmops-service"))

import uvicorn


def serve():
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
    )


def reindex():
    from app.pipeline.indexing_pipeline import IndexingPipeline
    from loguru import logger

    logger.info("Starting RAG reindexing...")
    pipeline = IndexingPipeline()
    result = pipeline.run()
    logger.info(f"Reindexing complete: {result}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="RetinaXAI LLMOps Service")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("serve")
    subparsers.add_parser("pipeline").add_argument("--task", choices=["reindex"], default="reindex")

    args = parser.parse_args()

    if args.command == "serve":
        serve()
    elif args.command == "pipeline" and args.task == "reindex":
        reindex()


if __name__ == "__main__":
    main()