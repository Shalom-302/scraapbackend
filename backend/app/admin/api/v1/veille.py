# backend/app/admin/endpoints/veille.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import asyncio
from celery import Task
# --- IMPORTS CORRIGÉS ---
# Les chemins sont simplifiés. Python va chercher à partir de la racine du projet (`backend/`).
from .....schemas import veille as veille_schema
from .....crud import veille as crud_veille
from .....database.db_postgres import get_async_db
from ...service import veille_service
from .....common.security.jwt import DependsJwtAuth # La vraie dépendance de sécurité
from ....tasks.veille import trigger_veille_task


# backend/app/admin/api/v1/veille.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, cast
import asyncio
from celery import Task


# --- IMPORTS CORRIGÉS ET COMPLETS ---

router = APIRouter()

# Applique la sécurité à toutes les routes de ce module
router.dependencies.append(DependsJwtAuth)


@router.post("/run", status_code=202, summary="Lancer une nouvelle veille en arrière-plan (Admin)")
def run_new_veille(
    query: str = Query(..., min_length=3, description="Le sujet de la veille, ex: 'Tendances Fintech'")
    # Note : cette route est maintenant `def` et non `async def` car elle est instantanée.
    # Elle n'a pas besoin de `Depends(get_async_db)` car elle ne touche pas à la DB.
):
    """
    Déclenche le processus de veille via Celery et répond immédiatement.
    Le travail lourd se fait en arrière-plan par un worker Celery.
    """
    try:
        print(f"Envoi de la tâche de veille pour '{query}' à Celery.")
        # On délègue le travail à Celery. `.delay()` envoie la tâche au broker (Redis).
        cast(Task,trigger_veille_task).delay(query)
        return {"message": "Tâche de veille lancée en arrière-plan. Les résultats seront disponibles via /articles dans ~30 minutes."}
    except Exception as e:
        # Gère le cas où le broker Celery/Redis est inaccessible
        print(f"ERREUR : Impossible de contacter le broker Celery. {e}")
        raise HTTPException(status_code=503, detail=f"Le service de tâches de fond est indisponible : {str(e)}")


@router.get("/articles", response_model=List[veille_schema.ArticleResponse], summary="Lister les articles analysés (Admin)")
async def get_articles(
    published: Optional[bool] = Query(None),
    score_min: Optional[int] = Query(None, ge=1, le=10),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Récupère les articles de la base de données. Rapide et sécurisé.
    """
    articles = await crud_veille.get_articles(db=db, published=published, score_min=score_min)
    return articles


@router.post("/articles/{article_id}/publish", response_model=veille_schema.ArticleResponse, summary="Publier un article (Admin)")
async def publish_article(
    article_id: int,
    status: veille_schema.PublishStatusUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Modifie le statut de publication d'un article. Rapide et sécurisé.
    """
    updated_article = await crud_veille.update_publish_status(db, article_id=article_id, published=status.published)
    if not updated_article:
        raise HTTPException(status_code=404, detail="Article non trouvé.")
        
    if status.published:
        print(f"INFO: L'article {article_id} est maintenant marqué comme publié. Déclenchement de la diffusion...")
        # C'est ici que vous pourriez lancer une AUTRE tâche Celery pour la publication sociale.
        # from app.tasks.social import post_article_task
        # post_article_task.delay(article_id)

    return updated_article