"""MODÈLE — logique applicative de BiblioIIT (membre D — feature/service).

Orchestre les règles (regles.py) et le dépôt (depot_sqlite.py).
Ne fait ni print() ni input() : c'est le rôle de la vue.
"""
from __future__ import annotations

from datetime import date
from typing import List, Optional, Tuple

from models import regles
from models.depot_sqlite import DepotSQLite
from models.modeles import Emprunt, Livre


class ErreurBibliotheque(Exception):
    """Erreur métier affichable telle quelle à l'utilisateur."""


class BibliothequeService:
    def __init__(self, depot: DepotSQLite) -> None:
        self._depot = depot

    def rechercher(self, mot_cle: str) -> List[Livre]:
        if not mot_cle.strip():
            raise ErreurBibliotheque("Le mot-clé ne peut pas être vide.")
        return [
            l for l in self._depot.lister_livres()
            if regles.correspond(mot_cle, l.titre, l.auteur)
        ]

    def emprunter(self, code: str, matricule: str,
                  aujourdhui: Optional[date] = None) -> Emprunt:
        aujourdhui = aujourdhui or date.today()
        code = regles.normaliser_code_livre(code)
        matricule = regles.normaliser_matricule(matricule)

        if not regles.code_livre_valide(code):
            raise ErreurBibliotheque("Code de livre invalide (format attendu : L002).")
        if not regles.matricule_valide(matricule):
            raise ErreurBibliotheque("Matricule invalide (format attendu : E2026-001).")

        livre = self._depot.obtenir_livre(code)
        if livre is None:
            raise ErreurBibliotheque(f"Le livre {code} n'existe pas.")
        if self._depot.emprunt_en_cours_du_livre(code) is not None:
            raise ErreurBibliotheque(f"Le livre « {livre.titre} » est déjà emprunté.")
        if not regles.peut_emprunter(self._depot.compter_emprunts_en_cours(matricule)):
            raise ErreurBibliotheque(
                f"{matricule} a déjà {regles.MAX_EMPRUNTS_PAR_ETUDIANT} emprunts en cours."
            )

        emprunt = Emprunt(
            id=None,
            code_livre=code,
            matricule=matricule,
            date_emprunt=aujourdhui,
            date_retour_prevue=regles.calculer_date_retour(aujourdhui),
        )
        return self._depot.enregistrer_emprunt(emprunt)

    def rendre(self, code: str, aujourdhui: Optional[date] = None) -> Tuple[Emprunt, int]:
        """Retourne (emprunt clôturé, nombre de jours de retard)."""
        aujourdhui = aujourdhui or date.today()
        code = regles.normaliser_code_livre(code)
        if not regles.code_livre_valide(code):
            raise ErreurBibliotheque("Code de livre invalide (format attendu : L002).")

        livre = self._depot.obtenir_livre(code)
        if livre is None:
            raise ErreurBibliotheque(f"Le livre {code} n'existe pas.")
        emprunt = self._depot.emprunt_en_cours_du_livre(code)
        if emprunt is None:
            raise ErreurBibliotheque(f"Le livre « {livre.titre} » n'est pas emprunté.")

        self._depot.cloturer_emprunt(emprunt.id, aujourdhui)
        emprunt.date_retour_effective = aujourdhui
        return emprunt, regles.jours_de_retard(emprunt.date_retour_prevue, aujourdhui)

    def retards(self, aujourdhui: Optional[date] = None) -> List[Tuple[Livre, Emprunt, int]]:
        aujourdhui = aujourdhui or date.today()
        resultat = []
        for e in self._depot.lister_emprunts_en_cours():
            if regles.est_en_retard(e.date_retour_prevue, aujourdhui):
                livre = self._depot.obtenir_livre(e.code_livre)
                resultat.append(
                    (livre, e, regles.jours_de_retard(e.date_retour_prevue, aujourdhui))
                )
        return resultat
