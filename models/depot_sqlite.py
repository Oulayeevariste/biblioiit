"""MODÈLE — persistance SQLite de BiblioIIT (membre C — feature/base).

Cette couche ne contient AUCUNE règle métier : elle lit et écrit seulement.
"""
from __future__ import annotations

import sqlite3
from datetime import date
from typing import List, Optional

from models.modeles import Emprunt, Livre

CATALOGUE_INITIAL = [
    ("L001", "Les Bouts de bois de Dieu", "Sembène Ousmane", 1960),
    ("L002", "Les Soleils des indépendances", "Ahmadou Kourouma", 1968),
    ("L003", "Une si longue lettre", "Mariama Bâ", 1979),
    ("L004", "Allah n'est pas obligé", "Ahmadou Kourouma", 2000),
    ("L005", "Le Vieux Nègre et la médaille", "Ferdinand Oyono", 1956),
]

_SCHEMA = """
CREATE TABLE IF NOT EXISTS livres (
    code   TEXT PRIMARY KEY,
    titre  TEXT NOT NULL,
    auteur TEXT NOT NULL,
    annee  INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS emprunts (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    code_livre            TEXT NOT NULL REFERENCES livres(code),
    matricule             TEXT NOT NULL,
    date_emprunt          TEXT NOT NULL,
    date_retour_prevue    TEXT NOT NULL,
    date_retour_effective TEXT
);
"""


class DepotSQLite:
    def __init__(self, chemin: str = ":memory:") -> None:
        self._conn = sqlite3.connect(chemin)
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(_SCHEMA)
        self._conn.commit()

    def fermer(self) -> None:
        self._conn.close()

    # --- livres -----------------------------------------------------------
    def initialiser_catalogue(self) -> None:
        """Insère le catalogue de démonstration si la table est vide."""
        (nb,) = self._conn.execute("SELECT COUNT(*) FROM livres").fetchone()
        if nb == 0:
            self._conn.executemany(
                "INSERT INTO livres (code, titre, auteur, annee) VALUES (?, ?, ?, ?)",
                CATALOGUE_INITIAL,
            )
            self._conn.commit()

    def ajouter_livre(self, livre: Livre) -> None:
        self._conn.execute(
            "INSERT INTO livres (code, titre, auteur, annee) VALUES (?, ?, ?, ?)",
            (livre.code, livre.titre, livre.auteur, livre.annee),
        )
        self._conn.commit()

    def lister_livres(self) -> List[Livre]:
        lignes = self._conn.execute("SELECT * FROM livres ORDER BY code").fetchall()
        return [Livre(l["code"], l["titre"], l["auteur"], l["annee"]) for l in lignes]

    def obtenir_livre(self, code: str) -> Optional[Livre]:
        l = self._conn.execute("SELECT * FROM livres WHERE code = ?", (code,)).fetchone()
        return Livre(l["code"], l["titre"], l["auteur"], l["annee"]) if l else None

    # --- emprunts ---------------------------------------------------------
    @staticmethod
    def _vers_emprunt(l: sqlite3.Row) -> Emprunt:
        retour = l["date_retour_effective"]
        return Emprunt(
            id=l["id"],
            code_livre=l["code_livre"],
            matricule=l["matricule"],
            date_emprunt=date.fromisoformat(l["date_emprunt"]),
            date_retour_prevue=date.fromisoformat(l["date_retour_prevue"]),
            date_retour_effective=date.fromisoformat(retour) if retour else None,
        )

    def enregistrer_emprunt(self, e: Emprunt) -> Emprunt:
        curseur = self._conn.execute(
            "INSERT INTO emprunts (code_livre, matricule, date_emprunt, date_retour_prevue) "
            "VALUES (?, ?, ?, ?)",
            (e.code_livre, e.matricule, e.date_emprunt.isoformat(),
             e.date_retour_prevue.isoformat()),
        )
        self._conn.commit()
        e.id = curseur.lastrowid
        return e

    def emprunt_en_cours_du_livre(self, code_livre: str) -> Optional[Emprunt]:
        l = self._conn.execute(
            "SELECT * FROM emprunts WHERE code_livre = ? AND date_retour_effective IS NULL",
            (code_livre,),
        ).fetchone()
        return self._vers_emprunt(l) if l else None

    def compter_emprunts_en_cours(self, matricule: str) -> int:
        (nb,) = self._conn.execute(
            "SELECT COUNT(*) FROM emprunts WHERE matricule = ? AND date_retour_effective IS NULL",
            (matricule,),
        ).fetchone()
        return nb

    def lister_emprunts_en_cours(self) -> List[Emprunt]:
        lignes = self._conn.execute(
            "SELECT * FROM emprunts WHERE date_retour_effective IS NULL "
            "ORDER BY date_retour_prevue"
        ).fetchall()
        return [self._vers_emprunt(l) for l in lignes]

    def cloturer_emprunt(self, id_emprunt: int, date_retour: date) -> None:
        self._conn.execute(
            "UPDATE emprunts SET date_retour_effective = ? WHERE id = ?",
            (date_retour.isoformat(), id_emprunt),
        )
        self._conn.commit()
