import unittest
from datetime import date

from models import regles


class TestRegles(unittest.TestCase):
    def test_date_retour_14_jours(self):
        self.assertEqual(regles.calculer_date_retour(date(2026, 10, 1)), date(2026, 10, 15))

    def test_retard(self):
        prevue = date(2026, 10, 15)
        self.assertFalse(regles.est_en_retard(prevue, date(2026, 10, 15)))
        self.assertTrue(regles.est_en_retard(prevue, date(2026, 10, 16)))
        self.assertEqual(regles.jours_de_retard(prevue, date(2026, 10, 20)), 5)
        self.assertEqual(regles.jours_de_retard(prevue, date(2026, 10, 1)), 0)

    def test_formats(self):
        self.assertTrue(regles.matricule_valide("E2026-001"))
        self.assertFalse(regles.matricule_valide("2026-001"))
        self.assertTrue(regles.code_livre_valide("L002"))
        self.assertFalse(regles.code_livre_valide("L2"))

    def test_quota(self):
        self.assertTrue(regles.peut_emprunter(2))
        self.assertFalse(regles.peut_emprunter(3))

    def test_recherche_sans_accents(self):
        self.assertTrue(regles.correspond("independances", "Les Soleils des indépendances"))
        self.assertTrue(regles.correspond("KOUROUMA", "Ahmadou Kourouma"))
        self.assertFalse(regles.correspond("", "Peu importe"))
