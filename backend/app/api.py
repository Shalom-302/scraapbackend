from fastapi import APIRouter

from backend.app.admin.api.v1 import v1_router

# Ceci est le routeur principal pour la sous-application /admin
admin_router = APIRouter()

# Inclure toutes les routes v1 sous le préfixe /api/v1
admin_router.include_router(v1_router, prefix="/api/v1")