# BiblioIIT — gestion de bibliothèque (console, architecture MVC)

Python 3.9+, aucune dépendance externe.

## Lancer / tester
    python main.py                      # base : biblioiit.db (créée automatiquement)
    python -m unittest discover -v

## Architecture MVC
    main.py                                  assemble les trois couches
    models/        MODÈLE      données + règles + persistance
        regles.py                 règles pures (14 jours, 3 emprunts max, formats)   A
        modeles.py                Livre, Emprunt                                      B
        depot_sqlite.py           SQLite, aucune règle métier                         C
        service.py                cas d'usage (rechercher, emprunter, rendre, retards) D
    views/         VUE         input() / print() uniquement                           E
        console_view.py
    controllers/   CONTRÔLEUR  relie la vue au modèle                                 E
        bibliotheque_controller.py
    tests/                                    chacun ses tests

Flux : utilisateur → Vue → Contrôleur → Modèle → Contrôleur → Vue → utilisateur.
Dépendances : la Vue ne connaît pas le Modèle (sauf ses entités pour l'affichage),
le Modèle ne connaît ni la Vue ni le Contrôleur.
