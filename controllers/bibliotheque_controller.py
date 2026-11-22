"""CONTRÔLEUR — fait le lien entre la vue et le modèle (membre E).

Il demande les saisies à la vue, appelle le service (modèle), puis redonne
le résultat à la vue. Il ne fait ni print() ni SQL.
"""
from __future__ import annotations

from datetime import date
from typing import Callable

from models.service import BibliothequeService, ErreurBibliotheque


class BibliothequeController:
    def __init__(self, service: BibliothequeService, vue,
                 aujourdhui: Callable[[], date] = date.today) -> None:
        self._service = service
        self._vue = vue
        self._aujourdhui = aujourdhui
        self._actions = {
            "1": self._rechercher,
            "2": self._emprunter,
            "3": self._rendre,
            "4": self._retards,
        }

    def lancer(self) -> None:
        while True:
            self._vue.afficher_menu()
            choix = self._vue.demander_choix()
            if choix == "0":
                self._vue.afficher_au_revoir()
                return
            action = self._actions.get(choix)
            if action is None:
                self._vue.afficher_choix_invalide()
                continue
            try:
                action()
            except ErreurBibliotheque as erreur:
                self._vue.afficher_erreur(str(erreur))

    def _rechercher(self) -> None:
        mot_cle = self._vue.demander_mot_cle()
        self._vue.afficher_livres(self._service.rechercher(mot_cle))

    def _emprunter(self) -> None:
        code = self._vue.demander_code_livre()
        matricule = self._vue.demander_matricule()
        emprunt = self._service.emprunter(code, matricule, self._aujourdhui())
        self._vue.afficher_emprunt_enregistre(emprunt)

    def _rendre(self) -> None:
        code = self._vue.demander_code_livre()
        _, retard = self._service.rendre(code, self._aujourdhui())
        self._vue.afficher_retour(retard)

    def _retards(self) -> None:
        self._vue.afficher_retards(self._service.retards(self._aujourdhui()))
