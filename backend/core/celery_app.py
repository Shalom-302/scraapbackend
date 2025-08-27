# backend/app/core/celery_app.py

from celery import Celery
from backend.core.conf import settings
import os
# Construire les URLs du broker et du backend
broker_url = f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.CELERY_BROKER_REDIS_DATABASE}"
backend_url = f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.CELERY_BACKEND_REDIS_DATABASE}"
celery_app = Celery("worker", broker=broker_url, backend=backend_url)

from pydantic import SecretStr

if settings.LANGSMITH_TRACING_V2:
    os.environ["LANGCHAIN_TRACING_V2"] = settings.LANGSMITH_TRACING_V2
if settings.LANGSMITH_ENDPOINT:
    os.environ["LANGCHAIN_ENDPOINT"] = settings.LANGSMITH_ENDPOINT
if settings.LANGSMITH_API_KEY:
    os.environ["LANGCHAIN_API_KEY"] = settings.LANGSMITH_API_KEY
if settings.LANGSMITH_PROJECT:
    os.environ["LANGCHAIN_PROJECT"] = settings.LANGSMITH_PROJECT


celery_app.autodiscover_tasks(packages=['app'], related_name='tasks')
# Création de l'instance Celery
celery_app = Celery(
    "backend", # Nom du module principal
    broker=broker_url,
    backend=backend_url,
    # Dire à Celery où trouver les tâches
    include=["backend.app.tasks.veille"]
)

celery_app.conf.update(
    task_track_started=True,
)

if __name__ == "__main__":
    celery_app.start()