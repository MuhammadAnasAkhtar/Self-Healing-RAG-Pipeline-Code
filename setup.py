from setuptools import setup, find_packages

setup(
    name="self_healing_rag",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "python-multipart",
        "sentence-transformers",
        "faiss-cpu",
        "transformers",
        "torch",
        "pypdf",
        "pydantic",
        "aiofiles"
    ],
)