# backend/app/schemas/veille.py

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# --- Schéma pour la sortie structurée du LLM ---
# C'est le contrat que l'on impose au LLM.
class ArticleAnalysisPydantic(BaseModel):
    resume_neutre: str = Field(description="Un résumé factuel et dense de l'article, style agence de presse, entre 700 et 800 caractères.")
    problematique_generale: str = Field(description="La problématique principale ou universelle soulevée.")
    impact_afrique: str = Field(description="L'impact direct ou indirect de cet événement sur l'Afrique.")
    problematique_africaine: str = Field(description="La problématique de fond que cela révèle pour le continent.")
    eveil_de_conscience: str = Field(description="La leçon critique, le 'wake-up call' pour l'Afrique.")
    piste_opportunite: str = Field(description="Une idée d'opportunité concrète pour l'écosystème tech africain.")
    score_pertinence: int = Field(description="Un score de 1 à 10 sur l'importance pour l'Afrique.", ge=1, le=10)

# --- Schémas pour les Endpoints de l'API ---

# Schéma de base partagé par la création et la lecture
class ArticleBase(BaseModel):
    url: str
    title: str
    source: str

# Schéma pour la réponse de l'API (ce que l'utilisateur voit)
# Il représente un objet Article lu depuis la base de données.
class ArticleResponse(ArticleBase):
    id: int # L'ID est un entier car on utilise id_key
    published: bool
    date: Optional[str] = None
    score_pertinence: Optional[int] = None
    analysis: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_time: datetime
    updated_time: Optional[datetime] = None

    # Permet de convertir automatiquement un objet SQLAlchemy en schéma Pydantic
    class Config:
        from_attributes = True

# Schéma pour la mise à jour du statut de publication
# C'est ce que l'admin envoie dans le corps de la requête POST.
class PublishStatusUpdate(BaseModel):
    published: bool