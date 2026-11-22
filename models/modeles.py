"""MODÈLE — entités de BiblioIIT (membre B — feature/modeles)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass(frozen=True)
class Livre:
    code: str
    titre: str
    auteur: str
    annee: int

    def __str__(self) -> str:
        return f"{self.code} {self.titre} — {self.auteur} ({self.annee})"


@dataclass
class Emprunt:
    id: Optional[int]
    code_livre: str
    matricule: str
    date_emprunt: date
    date_retour_prevue: date
    date_retour_effective: Optional[date] = None

    @property
    def en_cours(self) -> bool:
        return self.date_retour_effective is None
