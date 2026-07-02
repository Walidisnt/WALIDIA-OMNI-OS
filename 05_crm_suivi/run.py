#!/usr/bin/env python3
"""
Module 5 — CRM / suivi (SQLite).

Journal local : qui a été importé, contacté, quand, et le statut de la
relation. Sert de source de vérité pour le module 6 (reporting).

Usage :
    python run.py importer --csv ../data/sorties/prospects_scores.csv --db ../data/crm.db
    python run.py statut --db ../data/crm.db --id 3 --nouveau-statut repondu
    python run.py liste --db ../data/crm.db
    python run.py liste --db ../data/crm.db --statut a_contacter
"""
import argparse
import logging
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from crm import connecter, importer_prospects, mettre_a_jour_statut, lister_contacts  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def parser_arguments():
    parser = argparse.ArgumentParser(description="CRM minimal en SQLite pour suivre les prospects contactés.")
    sous_parseurs = parser.add_subparsers(dest="commande", required=True)

    parseur_import = sous_parseurs.add_parser("importer", help="Importer un CSV de prospects dans le CRM")
    parseur_import.add_argument("--csv", required=True)
    parseur_import.add_argument("--db", default="../data/crm.db")

    parseur_statut = sous_parseurs.add_parser("statut", help="Mettre à jour le statut d'un contact")
    parseur_statut.add_argument("--db", default="../data/crm.db")
    parseur_statut.add_argument("--id", type=int, required=True)
    parseur_statut.add_argument(
        "--nouveau-statut", required=True,
        choices=["a_contacter", "contacte", "repondu", "rdv_pris", "refus", "sans_reponse"],
    )

    parseur_liste = sous_parseurs.add_parser("liste", help="Lister les contacts du CRM")
    parseur_liste.add_argument("--db", default="../data/crm.db")
    parseur_liste.add_argument("--statut", default=None)

    return parser.parse_args()


def main():
    args = parser_arguments()
    chemin_db = Path(args.db)
    chemin_db.parent.mkdir(parents=True, exist_ok=True)
    connexion = connecter(str(chemin_db))

    if args.commande == "importer":
        df = pd.read_csv(args.csv, dtype=str).fillna("")
        nb = importer_prospects(connexion, df)
        logger.info("%s contact(s) importé(s) dans %s", nb, chemin_db)

    elif args.commande == "statut":
        mettre_a_jour_statut(connexion, args.id, args.nouveau_statut)
        logger.info("Contact %s : statut mis à jour vers '%s'", args.id, args.nouveau_statut)

    elif args.commande == "liste":
        contacts = lister_contacts(connexion, args.statut)
        for contact in contacts:
            print(
                f"[{contact['id']}] {contact['prenom']} {contact['nom']} "
                f"({contact['entreprise']}) — score={contact['score']} — statut={contact['statut']}"
            )
        logger.info("%s contact(s) affiché(s)", len(contacts))

    connexion.close()


if __name__ == "__main__":
    main()
