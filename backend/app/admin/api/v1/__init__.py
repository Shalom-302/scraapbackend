from fastapi import APIRouter

from backend.app.admin.api.v1.auth import router as auth_router
from backend.app.admin.api.v1.casbin import router as casbin_router
from backend.app.admin.api.v1.login_log import router as login_log_router
from backend.app.admin.api.v1.opera_log import router as opera_log_router
from backend.app.admin.api.v1.role import router as role_router
from backend.app.admin.api.v1.user import router as user_router
from backend.app.admin.api.v1.veille import router as veille_router

# Ce routeur va agréger toutes les routes de l'API v1
v1_router = APIRouter()

v1_router.include_router(auth_router, tags=["Auth"])
v1_router.include_router(casbin_router, tags=["Casbin"])
v1_router.include_router(login_log_router, tags=["Login Log"])
v1_router.include_router(opera_log_router, tags=["Opera Log"])
v1_router.include_router(role_router, tags=["Role"])
v1_router.include_router(user_router, tags=["User"])
v1_router.include_router(veille_router, prefix="/veille", tags=["Agent de Veille"])