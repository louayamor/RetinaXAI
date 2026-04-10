import argparse
import os
from pathlib import Path

os.chdir(Path(__file__).parent)

from loguru import logger

from app.pipeline.indexing_pipeline import IndexingPipeline


def run_reindex() -> None:
    logger.info("Starting RAG reindexing...")
    pipeline = IndexingPipeline()
    result = pipeline.run()
    logger.info(f"Reindexing complete: {result}")


def run_serve() -> None:
    import uvicorn

    logger.info("Starting LLMOps API server...")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
    )


def main():
    parser = argparse.ArgumentParser(description="RetinaXAI LLMOps Service")

    subparsers = parser.add_subparsers(dest="command", required=True)

    pipeline_parser = subparsers.add_parser("pipeline")
    pipeline_parser.add_argument(
        "--task",
        type=str,
        choices=["reindex"],
        default="reindex",
    )

    subparsers.add_parser("serve")

    args = parser.parse_args()

    if args.command == "pipeline":
        if args.task == "reindex":
            run_reindex()

    elif args.command == "serve":
        run_serve()


if __name__ == "__main__":
    main()