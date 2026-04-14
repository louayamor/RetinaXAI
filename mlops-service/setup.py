import setuptools

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

__version__ = "0.0.1"
REPO_NAME = "retinaxai"
AUTHOR_USER_NAME = "louayamor"
SRC_REPO = "retinaxai-mlops"
AUTHOR_EMAIL = "amor.louay20@gmail.com"

setuptools.setup(
    name=SRC_REPO,
    version=__version__,
    author=AUTHOR_USER_NAME,
    author_email=AUTHOR_EMAIL,
    description="MLOps service for diabetic retinopathy classification - RetinaXAI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=f"https://github.com/{AUTHOR_USER_NAME}/{REPO_NAME}",
    project_urls={
        "Bug Tracker": f"https://github.com/{AUTHOR_USER_NAME}/{REPO_NAME}/issues",
    },
    packages=setuptools.find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "torch",
        "torchvision",
        "timm",
        "datasets",
        "transformers",
        "numpy",
        "pandas",
        "scikit-learn",
        "Pillow",
        "opencv-python-headless",
        "albumentations",
        "mlflow",
        "dvc",
        "evidently",
        "prometheus-client",
        "fastapi",
        "uvicorn",
        "httpx",
        "pydantic",
        "pydantic-settings",
        "python-dotenv",
        "PyYAML",
        "python-box",
        "loguru",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
