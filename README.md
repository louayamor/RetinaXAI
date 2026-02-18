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

The platform includes:

- **FastAPI backend**: Handles admin and patient management, JWT authentication, and service orchestration  
- **Next.js frontend**: Responsive dashboards and interfaces for clinicians and patients  
- **MLOps service**: Preprocessing, training, and inference pipelines for medical imaging  
- **LLMOps service**: RAG-style LLM pipelines for medical report generation  
- **Infrastructure**: Docker Compose and Kubernetes manifests for scalable deployment  

---

## Features

- Upload and manage patient data and medical images  
- Automated image analysis for diabetic retinopathy  
- Contextual medical report generation using LLMs  
- Modular microservices architecture for independent development  
- CI/CD-ready monorepo for rapid iteration  

---

## Tech Stack

| Layer           | Technology |
|-----------------|------------|
| Backend         | FastAPI, Python, Pydantic |
| Frontend        | Next.js, TypeScript, Tailwind CSS |
| Machine Learning| Python, TensorFlow / PyTorch, MLflow, DVC |
| LLMOps          | LangChain, FAISS, HuggingFace Transformers |
| Infrastructure  | Docker, Docker Compose, Kubernetes, NGINX |
| Database        | PostgreSQL / SQLite / Firebase |

---

## Folder Structure (Monorepo)

```
retinaxai/
├── mlops-service/
├── llmops-service/
├── web-backend/
├── frontend/
├── infra/
│   ├── docker-compose.yml
│   ├── k8s/
│   └── scripts/
└── README.md
```

---

## Getting Started

### Clone the repository
```bash
git clone https://github.com/<username>/RetinaXAI.git
cd retinaxai
```

### Backend
```bash
cd web-backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### MLOps / LLMOps Services
```bash
cd mlops-service
pip install -r requirements.txt
python main.py

cd llmops-service
pip install -r requirements.txt
python main.py
```

---

## Contributing

1. Create a branch from `dev` for your feature  
2. Implement your feature in the relevant service  
3. Open a pull request to `dev`  
4. Ensure tests pass and code is linted  

---

## License

This project is licensed under the MIT License.  

---

## Contact

**Louay Amor** – [GitHub](https://github.com/louayamor) – [Email](mailto:amor.louay20@gmail.com)

