# backend/app/tasks/veille.py
import asyncio

# L'IMPORT FONCTIONNE MAINTENANT !
from backend.core.celery_app import celery_app
from celery import Task
from backend.database.db_postgres import async_db_session
from backend.app.admin.service import veille_service


@celery_app.task(name="veille.run_workflow")
async def _run_veille_workflow_with_session(query: str):
    """Fonction asynchrone pour gérer le cycle de vie de la session."""
    async with async_db_session() as session:
        await veille_service.run_veille_workflow(db=session, query=query)

@celery_app.task(name="veille.trigger_workflow")
def trigger_veille_task(query: str):
  
    try:
        print(f"--- Tâche Celery Démarrée : Veille pour '{query}' ---")
        # Exécute la fonction wrapper asynchrone qui gère la session
        asyncio.run(_run_veille_workflow_with_session(query=query))
        print(f"--- Tâche de veille pour '{query}' terminée. ---")
        return {"status": "SUCCESS", "message": "Veille terminée."}
    except Exception as e:
        error_message = f"La tâche de veille a échoué : {str(e)}"
        print(f"--- ERREUR Tâche Celery : {error_message} ---")
        return {"status": "FAILURE", "error": error_message}
    