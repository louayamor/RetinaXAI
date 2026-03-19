# GitHub Secrets — MLOps Service

Configure these in: `Settings > Secrets and variables > Actions`

## Required Secrets

| Secret | Description | Where to get it |
|---|---|---|
| `DAGSHUB_TOKEN` | DagsHub personal access token | https://dagshub.com/user/settings/tokens |
| `DAGSHUB_USERNAME` | DagsHub username | `louayamor` |
| `MLFLOW_TRACKING_URI` | MLflow tracking URI | `https://dagshub.com/louayamor/retinaxai.mlflow` |
| `HF_TOKEN` | HuggingFace access token | https://huggingface.co/settings/tokens |

## Auto-provided Secrets

| Secret | Description |
|---|---|
| `GITHUB_TOKEN` | Auto-provided by GitHub Actions — used for ghcr.io login |

## Notes

- `GITHUB_TOKEN` requires `packages: write` permission in the workflow — already configured
- Never commit `.env` file — it is in `.gitignore` and `.dockerignore`
- DVC credentials use `--local` flag and are never written to `dvc/config`