#!/usr/bin/env python3
"""
Module 1 — Enrichissement & Génération de messages.

Charge un CSV de prospects, applique les règles de conformité RGPD,
enrichit avec le numéro standard public de l'entreprise, puis génère un
message email et un message LinkedIn personnalisés via l'API Claude.

Usage :
    python run.py --input ../data/exemples/prospects_exemple.csv \\
                   --output ../data/sorties/prospects_enrichis.csv
"""
import argparse
import logging
import sys
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent))
from conformite import appliquer_regles_conformite  # noqa: E402
from enrichissement_entreprise import rechercher_telephone_entreprise  # noqa: E402
from generation_messages import generer_messages  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

COLONNES_ATTENDUES = ["prenom", "nom", "entreprise", "role", "ville", "email"]


def parser_arguments():
    parser = argparse.ArgumentParser(
        description="Enrichit un CSV de prospects (conformité RGPD + numéro "
        "d'entreprise) et génère des messages de prospection personnalisés "
        "(email + LinkedIn) via l'API Claude."
    )
    parser.add_argument("--input", required=True, help="CSV de prospects en entrée")
    parser.add_argument("--output", required=True, help="CSV enrichi en sortie")
    parser.add_argument(
        "--sans-messages", action="store_true",
        help="N'appelle pas l'API Claude : applique juste la conformité et "
        "l'enrichissement entreprise (utile pour tester sans clé API).",
    )
    return parser.parse_args()


def valider_colonnes(df):
    manquantes = [c for c in COLONNES_ATTENDUES if c not in df.columns]
    if manquantes:
        raise ValueError(f"Colonnes manquantes dans le CSV d'entrée : {manquantes}")


def main():
    load_dotenv()
    args = parser_arguments()

    chemin_entree = Path(args.input)
    chemin_sortie = Path(args.output)
    chemin_sortie.parent.mkdir(parents=True, exist_ok=True)

    logger.info("Lecture de %s", chemin_entree)
    df = pd.read_csv(chemin_entree, dtype=str).fillna("")
    valider_colonnes(df)

    logger.info("Application des règles de conformité RGPD")
    df = appliquer_regles_conformite(df)
    nb_non_collectables = (df["base_legale"] == "non_collectable").sum()
    if nb_non_collectables:
        logger.warning(
            "%s email(s) vidé(s) faute de base légale valide (base_legale=non_collectable)",
            nb_non_collectables,
        )

    logger.info("Recherche du numéro standard public de chaque entreprise")
    telephones = []
    for _, ligne in df.iterrows():
        site_web = ligne.get("site_web", "") if "site_web" in df.columns else ""
        telephone, source = rechercher_telephone_entreprise(ligne["entreprise"], site_web)
        telephones.append(telephone)
        if telephone:
            logger.info("Numéro trouvé pour %s : %s (%s)", ligne["entreprise"], telephone, source)
    df["telephone_entreprise"] = telephones

    if args.sans_messages:
        df["message_email"] = ""
        df["message_linkedin"] = ""
        logger.info("Génération des messages ignorée (--sans-messages)")
    else:
        logger.info("Génération des messages de prospection (%s prospects)", len(df))
        messages_email, messages_linkedin = [], []
        for _, ligne in df.iterrows():
            resultat = generer_messages(ligne.to_dict())
            messages_email.append(resultat["message_email"])
            messages_linkedin.append(resultat["message_linkedin"])
            logger.info("Messages générés pour %s %s", ligne["prenom"], ligne["nom"])
        df["message_email"] = messages_email
        df["message_linkedin"] = messages_linkedin

    df.to_csv(chemin_sortie, index=False)
    logger.info("Terminé. Fichier écrit : %s (%s lignes)", chemin_sortie, len(df))


if __name__ == "__main__":
    main()
