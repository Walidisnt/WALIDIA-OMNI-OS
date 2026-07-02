#!/usr/bin/env python3
"""
Module 3 — Détection de signaux.

Pour une liste d'entreprises, cherche des signaux d'achat (recrutements
IA/data, actualités pertinentes) à partir du contenu public de leur site.

Usage :
    python run.py --input ../data/exemples/entreprises_exemple.csv \\
                   --output ../data/sorties/entreprises_signaux.csv
"""
import argparse
import logging
import sys
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent))
from signaux import detecter_signal  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def parser_arguments():
    parser = argparse.ArgumentParser(
        description="Recherche des signaux d'achat pour une liste d'entreprises."
    )
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main():
    load_dotenv()
    args = parser_arguments()

    chemin_sortie = Path(args.output)
    chemin_sortie.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(args.input, dtype=str).fillna("")

    signaux, dates = [], []
    for _, ligne in df.iterrows():
        resultat = detecter_signal(ligne.get("nom", ""), ligne.get("site_web", ""))
        signaux.append(resultat["signal"])
        dates.append(resultat["date_detection"])
        logger.info("%s : %s", ligne.get("nom", ""), resultat["signal"])

    df["signal"] = signaux
    df["date_detection"] = dates

    df.to_csv(chemin_sortie, index=False)
    logger.info("Terminé. Fichier écrit : %s (%s lignes)", chemin_sortie, len(df))


if __name__ == "__main__":
    main()
