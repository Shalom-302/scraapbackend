from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime


class ArticleAnalysis(BaseModel):
    resume_neutre: str = Field(description="Un résumé factuel et dense de l'article, style agence de presse, entre 700 et 800 caractères.")
    problematique_generale: str = Field(description="La problématique principale ou universelle soulevée.")
    impact_afrique: str = Field(description="L'impact direct ou indirect de cet événement sur l'Afrique.")
    problematique_africaine: str = Field(description="La problématique de fond que cela révèle pour le continent.")
    eveil_de_conscience: str = Field(description="La leçon critique, le 'wake-up call' pour l'Afrique.")
    piste_opportunite: str = Field(description="Une idée d'opportunité concrète pour l'écosystème tech africain.")
    type_evenement: str = Field(description="Ex: 'Faillite', 'Lancement de produit', 'Tendance'")
    resume_strategique: str = Field(description="Résumé de l'événement et son importance.")
    lecon_a_retenir: str = Field(description="Le conseil principal à tirer de cet événement.")
    impact_potentiel: str = Field(description="L'impact potentiel sur l'industrie.")
    score_pertinence: int = Field(description="Un score de 1 à 10 sur l'importance pour l'Afrique.", ge=1, le=10)


class ArticleBase(BaseModel):
    url: str
    title: str
    source: str


class ArticleResponse(ArticleBase):
    id: int
    published: bool
    type_evenement: Optional[str] = None
    date: Optional[str] = None
    score_pertinence: Optional[int] = None
    analysis: Optional[ArticleAnalysis] = None
    error: Optional[str] = None
    created_time: datetime
    updated_time: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class PublishStatusUpdate(BaseModel):
    published: bool


class TriggerVeilleRequest(BaseModel):
    query: str