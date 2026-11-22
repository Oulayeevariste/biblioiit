"""VUE — tout ce qui touche à input() et print() (membre E — feature/menu).

La vue est « passive » : elle affiche et saisit, mais ne contient aucune règle
métier et ne connaît ni la base de données ni le service.
"""
from __future__ import annotations

from datetime import date
from typing import Callable, Iterable, Tuple

from models.modeles import Emprunt, Livre

MENU = (
    "\n=== BiblioIIT ===\n"
    "1. Rechercher un livre   2. Emprunter\n"
    "3. Rendre   4. Retards   0. Quitter"
)


def formater_date(d: date) -> str:
    return d.strftime("%d/%m/%Y")


class ConsoleView:
    def __init__(self, entree: Callable[[str], str] = input,
                 sortie: Callable[[str], None] = print) -> None:
        self._entree = entree
        self._sortie = sortie

    # --- saisies ----------------------------------------------------------
    def afficher_menu(self) -> None:
        self._sortie(MENU)

    def demander_choix(self) -> str:
        try:
            return self._entree("Votre choix : ").strip()
        except EOFError:
            return "0"

    def demander_mot_cle(self) -> str:
        return self._entree("Mot-clé : ")

    def demander_code_livre(self) -> str:
        return self._entree("Code du livre : ")

    def demander_matricule(self) -> str:
        return self._entree("Matricule : ")

    # --- affichages -------------------------------------------------------
    def afficher_livres(self, livres: Iterable[Livre]) -> None:
        livres = list(livres)
        if not livres:
            self._sortie("Aucun livre trouvé.")
        for livre in livres:
            self._sortie(f"  {livre}")

    def afficher_emprunt_enregistre(self, emprunt: Emprunt) -> None:
        self._sortie(
            "Emprunt enregistré. "
            f"Retour prévu le {formater_date(emprunt.date_retour_prevue)}."
        )

    def afficher_retour(self, jours_de_retard: int) -> None:
        if jours_de_retard:
            self._sortie(f"Retour enregistré avec {jours_de_retard} jour(s) de retard.")
        else:
            self._sortie("Retour enregistré. Merci !")

    def afficher_retards(self, retards: Iterable[Tuple[Livre, Emprunt, int]]) -> None:
        retards = list(retards)
        if not retards:
            self._sortie("Aucun retard.")
        for livre, emprunt, jours in retards:
            self._sortie(
                f"  {livre.code} {livre.titre} — {emprunt.matricule} : "
                f"{jours} jour(s) de retard "
                f"(prévu le {formater_date(emprunt.date_retour_prevue)})"
            )

    def afficher_choix_invalide(self) -> None:
        self._sortie("Choix invalide. Tapez 0, 1, 2, 3 ou 4.")

    def afficher_erreur(self, message: str) -> None:
        self._sortie(f"Impossible : {message}")

    def afficher_au_revoir(self) -> None:
        self._sortie("Au revoir !")
