.PHONY: help dvc-pull dvc-push dvc-repro dvc-status dvc-metrics imaging clinical clean setup-dvc

help:
	@echo "RetinaXAI MLOps Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  dvc-pull        Pull all DVC artifacts from remote"
	@echo "  dvc-push        Push all DVC artifacts to remote"
	@echo "  dvc-repro       Run full DVC pipeline"
	@echo "  dvc-status      Show DVC pipeline status"
	@echo "  dvc-metrics     Show current metrics"
	@echo "  imaging         Run imaging pipeline stages"
	@echo "  clinical        Run clinical pipeline stages"
	@echo "  clean           Clean DVC cache and outputs"
	@echo "  setup-dvc       Configure DVC remote credentials"

dvc-pull:
	dvc pull

dvc-push:
	dvc push

dvc-repro:
	dvc repro

dvc-status:
	dvc status

dvc-metrics:
	@echo "=== Imaging Metrics ==="
	@cat artifacts/model/imaging/metrics.json 2>/dev/null || echo "Not found"
	@echo ""
	@echo "=== Clinical Metrics ==="
	@cat artifacts/model/clinical/metrics.json 2>/dev/null || echo "Not found"

imaging:
	python main.py pipeline --stage ingest --pipeline imaging
	python main.py pipeline --stage clean --pipeline imaging
	python main.py pipeline --stage transform --pipeline imaging
	python main.py pipeline --stage train --pipeline imaging
	python main.py pipeline --stage evaluate --pipeline imaging

clinical:
	python main.py pipeline --stage ingest --pipeline clinical
	python main.py pipeline --stage clean --pipeline clinical
	python main.py pipeline --stage transform --pipeline clinical
	python main.py pipeline --stage train --pipeline clinical
	python main.py pipeline --stage evaluate --pipeline clinical

clean:
	dvc gc -f
	rm -rf artifacts/data/processed/*
	rm -rf artifacts/model/*
	rm -f artifacts/training_jobs.json

setup-dvc:
	@if [ -z "$$DVC_REMOTE_TOKEN" ]; then \
		echo "Usage: DVC_REMOTE_TOKEN=<token> make setup-dvc"; \
		exit 1; \
	fi
	dvc remote modify dagshub --local auth basic
	dvc remote modify dagshub --local user louayamor
	dvc remote modify dagshub --local password $$DVC_REMOTE_TOKEN
	@echo "DVC configured successfully"
