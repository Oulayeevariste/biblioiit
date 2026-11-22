import unittest
from datetime import date

from controllers.bibliotheque_controller import BibliothequeController
from models.depot_sqlite import DepotSQLite
from models.service import BibliothequeService
from views.console_view import ConsoleView


class VueEspion:
    """Fausse vue : le contrôleur se teste sans aucun print() ni input()."""
    def __init__(self, choix, saisies):
        self.choix, self.saisies, self.appels = iter(choix), iter(saisies), []

    def afficher_menu(self): pass
    def demander_choix(self): return next(self.choix)
    def demander_mot_cle(self): return next(self.saisies)
    def demander_code_livre(self): return next(self.saisies)
    def demander_matricule(self): return next(self.saisies)
    def afficher_choix_invalide(self): self.appels.append(("invalide",))
    def afficher_au_revoir(self): self.appels.append(("fin",))
    def afficher_erreur(self, m): self.appels.append(("erreur", m))
    def afficher_livres(self, l): self.appels.append(("livres", [x.code for x in l]))
    def afficher_emprunt_enregistre(self, e): self.appels.append(("emprunt", e.code_livre))
    def afficher_retour(self, j): self.appels.append(("retour", j))
    def afficher_retards(self, r): self.appels.append(("retards", len(r)))


class TestControleur(unittest.TestCase):
    def setUp(self):
        self.depot = DepotSQLite(":memory:")
        self.depot.initialiser_catalogue()
        self.modele = BibliothequeService(self.depot)

    def tearDown(self):
        self.depot.fermer()

    def test_aiguillage_vers_la_vue(self):
        vue = VueEspion(["1", "2", "2", "9", "0"],
                        ["Kourouma", "L002", "E2026-001", "L002", "E2026-002"])
        BibliothequeController(self.modele, vue, lambda: date(2026, 10, 1)).lancer()
        self.assertEqual(vue.appels[0], ("livres", ["L002", "L004"]))
        self.assertEqual(vue.appels[1], ("emprunt", "L002"))
        self.assertEqual(vue.appels[2][0], "erreur")
        self.assertIn("déjà emprunté", vue.appels[2][1])
        self.assertEqual(vue.appels[3:], [("invalide",), ("fin",)])

    def test_session_complete_du_cours(self):
        saisies = iter(["1", "Kourouma", "2", "L002", "E2026-001",
                        "2", "L002", "E2026-002", "0"])
        sortie = []
        vue = ConsoleView(entree=lambda _: next(saisies), sortie=sortie.append)
        BibliothequeController(self.modele, vue, lambda: date(2026, 10, 1)).lancer()
        texte = "\n".join(sortie)
        self.assertIn("L004 Allah n'est pas obligé — Ahmadou Kourouma (2000)", texte)
        self.assertIn("Emprunt enregistré. Retour prévu le 15/10/2026.", texte)
        self.assertIn("Impossible : Le livre « Les Soleils des indépendances » est déjà emprunté.", texte)

    def test_retard_au_retour(self):
        vue = VueEspion(["2", "3", "0"], ["L001", "E2026-001", "L001"])
        dates = iter([date(2026, 10, 1), date(2026, 10, 20)])
        BibliothequeController(self.modele, vue, lambda: next(dates)).lancer()
        self.assertIn(("retour", 5), vue.appels)
