"""MODÈLE — règles métier de BiblioIIT (membre A — feature/regles).

Aucune dépendance vers la base de données ni vers la console :
uniquement des fonctions pures, faciles à tester.
"""
from __future__ import annotations

import re
import unicodedata
from datetime import date, timedelta

DUREE_EMPRUNT_JOURS = 14
MAX_EMPRUNTS_PAR_ETUDIANT = 3

_RE_CODE_LIVRE = re.compile(r"^L\d{3}$")
_RE_MATRICULE = re.compile(r"^E\d{4}-\d{3}$")


def normaliser_code_livre(saisie: str) -> str:
    return saisie.strip().upper()


def normaliser_matricule(saisie: str) -> str:
    return saisie.strip().upper()


def code_livre_valide(code: str) -> bool:
    return bool(_RE_CODE_LIVRE.match(code))


def matricule_valide(matricule: str) -> bool:
    return bool(_RE_MATRICULE.match(matricule))


def calculer_date_retour(date_emprunt: date) -> date:
    return date_emprunt + timedelta(days=DUREE_EMPRUNT_JOURS)


def jours_de_retard(date_retour_prevue: date, aujourdhui: date) -> int:
    return max(0, (aujourdhui - date_retour_prevue).days)


def est_en_retard(date_retour_prevue: date, aujourdhui: date) -> bool:
    return jours_de_retard(date_retour_prevue, aujourdhui) > 0


def peut_emprunter(nb_emprunts_en_cours: int) -> bool:
    return nb_emprunts_en_cours < MAX_EMPRUNTS_PAR_ETUDIANT


def normaliser_texte(texte: str) -> str:
    """Minuscules sans accents, pour une recherche tolérante."""
    decompose = unicodedata.normalize("NFD", texte)
    sans_accents = "".join(c for c in decompose if unicodedata.category(c) != "Mn")
    return sans_accents.lower().strip()


def correspond(mot_cle: str, *champs: str) -> bool:
    mot = normaliser_texte(mot_cle)
    return bool(mot) and any(mot in normaliser_texte(c) for c in champs)

