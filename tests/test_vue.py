import unittest
from datetime import date

from models.modeles import Emprunt, Livre
from views.console_view import ConsoleView


class TestVue(unittest.TestCase):
    def setUp(self):
        self.sortie = []
        self.vue = ConsoleView(entree=lambda _: "  2 ", sortie=self.sortie.append)

    def test_choix_nettoye(self):
        self.assertEqual(self.vue.demander_choix(), "2")

    def test_fin_de_saisie_quitte(self):
        def eof(_):
            raise EOFError
        self.assertEqual(ConsoleView(entree=eof).demander_choix(), "0")

    def test_affichage_livre_et_emprunt(self):
        self.vue.afficher_livres([Livre("L004", "Allah n'est pas obligé", "Ahmadou Kourouma", 2000)])
        self.vue.afficher_emprunt_enregistre(
            Emprunt(1, "L004", "E2026-001", date(2026, 10, 1), date(2026, 10, 15)))
        self.assertEqual(self.sortie[0], "  L004 Allah n'est pas obligé — Ahmadou Kourouma (2000)")
        self.assertEqual(self.sortie[1], "Emprunt enregistré. Retour prévu le 15/10/2026.")

    def test_listes_vides(self):
        self.vue.afficher_livres([])
        self.vue.afficher_retards([])
        self.assertEqual(self.sortie, ["Aucun livre trouvé.", "Aucun retard."])
