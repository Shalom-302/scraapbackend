# backend/app/models/veille.py

from sqlalchemy import String, Text, Integer, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional

from ..common.model import Base, id_key

class Article(Base):
    """
    Modèle SQLAlchemy pour stocker les articles de veille analysés.
    """
    id: Mapped[id_key] = mapped_column(init=False)

    # --- Champs avec la taille des colonnes corrigée ---

    url: Mapped[str] = mapped_column(String(1024), unique=True, index=True, nullable=False, default=None)
    
    # Un titre peut parfois être long, le passer en TEXT est plus sûr.
    title: Mapped[str] = mapped_column(Text, nullable=False, default=None)
    
    source: Mapped[str] = mapped_column(String(100), nullable=False, default=None)
    
    published: Mapped[bool] = mapped_column(Boolean, default=False)
    
    date: Mapped[Optional[str]] = mapped_column(String(50), default=None)
    
    # Le contenu est déjà en TEXT, c'est parfait.
    content: Mapped[Optional[str]] = mapped_column(Text, default=None)
    
    score_pertinence: Mapped[Optional[int]] = mapped_column(Integer, index=True, default=None)
    
    # analysis (JSON) et error (TEXT) sont les plus importants à corriger.
    analysis: Mapped[Optional[dict]] = mapped_column(JSON, default=None)
    
    # Les messages d'erreur peuvent être très longs, TEXT est obligatoire ici.
    error: Mapped[Optional[str]] = mapped_column(Text, default=None)

    def __repr__(self) -> str:
        return f"<Article(id={self.id}, title='{self.title[:30]}...')>"