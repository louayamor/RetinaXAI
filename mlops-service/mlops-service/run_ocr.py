from app.pipeline.ocr_pipeline import OCRPipeline
import sys

if __name__ == "__main__":
    pipeline = OCRPipeline()
    reports = pipeline.run()
    sys.exit(0 if reports else 1)