FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /app

RUN pip install --no-cache-dir poetry
RUN poetry config virtualenvs.create false

# Copier les fichiers de dépendances du backend
COPY backend/pyproject.toml backend/poetry.lock ./
RUN poetry install --no-root --only main

# Copier tout le backend dans /app/backend
COPY backend/ /app/backend/

# Définir PYTHONPATH pour trouver les modules backend
ENV PYTHONPATH=/app/backend

EXPOSE 8000