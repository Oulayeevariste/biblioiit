"""Point d'entrée de BiblioIIT : assemble Modèle, Vue et Contrôleur.

Usage :  python main.py [chemin_base.db]
"""
import sys

from controllers.bibliotheque_controller import BibliothequeController
from models.depot_sqlite import DepotSQLite
from models.service import BibliothequeService
from views.console_view import ConsoleView


def main() -> None:
    chemin = sys.argv[1] if len(sys.argv) > 1 else "biblioiit.db"
    depot = DepotSQLite(chemin)
    depot.initialiser_catalogue()
    try:
        modele = BibliothequeService(depot)
        vue = ConsoleView()
        BibliothequeController(modele, vue).lancer()
    finally:
        depot.fermer()


if __name__ == "__main__":
    main()
