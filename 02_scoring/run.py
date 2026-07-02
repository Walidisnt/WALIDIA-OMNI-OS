#!/usr/bin/env python3
"""
Module 2 — Scoring.

Classe chaque prospect en chaud / tiède / froid à partir de critères
simples, affinés par un appel à l'API Claude. Trie le CSV par score
décroissant (chaud en premier).

Usage :
    python run.py --input ../data/sorties/prospects_enrichis.csv \\
                   --output ../data/sorties/prospects_scores.csv
"""
import argparse
import logging
import sys
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scoring import score_regles, categorie_depuis_points, affiner_avec_ia  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def parser_arguments():
    parser = argparse.ArgumentParser(
        description="Classe chaque prospect en chaud/tiède/froid (règles + IA)."
    )
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument(
        "--sans-ia", action="store_true",
        help="N'utilise que les règles simples, sans appel API Claude "
        "(plus rapide, ne nécessite pas de clé API).",
    )
    return parser.parse_args()


def main():
    load_dotenv()
    args = parser_arguments()

    chemin_sortie = Path(args.output)
    chemin_sortie.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(args.input, dtype=str).fillna("")

    categories, raisons = [], []
    for _, ligne in df.iterrows():
        points = score_regles(ligne.to_dict())
        categorie_regles = categorie_depuis_points(points)

        if args.sans_ia:
            categories.append(categorie_regles)
            raisons.append("règles seules (--sans-ia)")
        else:
            categorie, raison = affiner_avec_ia(ligne.to_dict(), categorie_regles)
            categories.append(categorie)
            raisons.append(raison)
        logger.info("%s %s -> %s", ligne.get("prenom", ""), ligne.get("nom", ""), categories[-1])

    df["score"] = categories
    df["score_raison"] = raisons

    ordre = {"chaud": 0, "tiede": 1, "froid": 2}
    df["_ordre_tri"] = df["score"].map(ordre)
    df = df.sort_values("_ordre_tri", kind="stable").drop(columns="_ordre_tri")

    df.to_csv(chemin_sortie, index=False)
    logger.info("Terminé. Fichier écrit : %s (%s lignes)", chemin_sortie, len(df))


if __name__ == "__main__":
    main()
