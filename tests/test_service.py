import unittest
from datetime import date

from models.depot_sqlite import DepotSQLite
from models.service import BibliothequeService, ErreurBibliotheque

JOUR = date(2026, 10, 1)


class TestService(unittest.TestCase):
    def setUp(self):
        self.depot = DepotSQLite(":memory:")
        self.depot.initialiser_catalogue()
        self.service = BibliothequeService(self.depot)

    def tearDown(self):
        self.depot.fermer()

    def test_recherche_kourouma(self):
        codes = [l.code for l in self.service.rechercher("Kourouma")]
        self.assertEqual(codes, ["L002", "L004"])

    def test_emprunt_ok(self):
        e = self.service.emprunter("L002", "E2026-001", JOUR)
        self.assertEqual(e.date_retour_prevue, date(2026, 10, 15))

    def test_livre_deja_emprunte(self):
        self.service.emprunter("L002", "E2026-001", JOUR)
        with self.assertRaises(ErreurBibliotheque) as ctx:
            self.service.emprunter("L002", "E2026-002", JOUR)
        self.assertIn("« Les Soleils des indépendances » est déjà emprunté", str(ctx.exception))

    def test_quota_de_trois(self):
        for code in ("L001", "L002", "L003"):
            self.service.emprunter(code, "E2026-001", JOUR)
        with self.assertRaises(ErreurBibliotheque):
            self.service.emprunter("L004", "E2026-001", JOUR)

    def test_livre_inconnu_et_formats(self):
        with self.assertRaises(ErreurBibliotheque):
            self.service.emprunter("L999", "E2026-001", JOUR)
        with self.assertRaises(ErreurBibliotheque):
            self.service.emprunter("002", "E2026-001", JOUR)
        with self.assertRaises(ErreurBibliotheque):
            self.service.emprunter("L002", "abc", JOUR)

    def test_rendre_et_reemprunter(self):
        self.service.emprunter("L002", "E2026-001", JOUR)
        _, retard = self.service.rendre("L002", date(2026, 10, 10))
        self.assertEqual(retard, 0)
        self.service.emprunter("L002", "E2026-002", date(2026, 10, 11))

    def test_rendre_livre_non_emprunte(self):
        with self.assertRaises(ErreurBibliotheque):
            self.service.rendre("L001", JOUR)

    def test_retards(self):
        self.service.emprunter("L002", "E2026-001", JOUR)
        self.assertEqual(self.service.retards(date(2026, 10, 15)), [])
        (livre, _, jours), = self.service.retards(date(2026, 10, 18))
        self.assertEqual((livre.code, jours), ("L002", 3))
        _, retard = self.service.rendre("L002", date(2026, 10, 18))
        self.assertEqual(retard, 3)
