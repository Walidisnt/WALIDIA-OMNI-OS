#!/usr/bin/env python3
"""
Lance toute la chaîne de prospection en une seule commande.

Enchaîne : Module 1 (enrichissement + messages) -> Module 2 (scoring) ->
Module 5 (import dans le CRM) -> Module 6 (rapport HTML).

Pensé pour quelqu'un qui ne veut pas taper une commande par module : ce
script s'occupe de tout, avec des chemins de fichiers par défaut sous
data/. Si aucune clé ANTHROPIC_API_KEY n'est configurée dans .env, il
tourne quand même, en mode démo (sans génération de messages ni
affinage IA du score).
"""
import argparse
import logging
import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

RACINE = Path(__file__).resolve().parent
DATA = RACINE / "data"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def executer(commande):
    logger.info("Étape : %s", " ".join(str(c) for c in commande))
    resultat = subprocess.run(commande)
    if resultat.returncode != 0:
        logger.error("Échec de l'étape ci-dessus, arrêt de la chaîne.")
        sys.exit(resultat.returncode)


def main():
    load_dotenv()
    parser = argparse.ArgumentParser(
        description="Lance toute la chaîne de prospection en une commande : "
        "enrichissement + messages -> scoring -> CRM -> rapport."
    )
    parser.add_argument(
        "--prospects",
        default=str(DATA / "exemples" / "prospects_exemple.csv"),
        help="CSV de prospects en entrée (par défaut : le fichier d'exemple).",
    )
    args = parser.parse_args()

    a_une_cle = bool(os.getenv("ANTHROPIC_API_KEY", "").strip())
    if not a_une_cle:
        logger.warning(
            "Aucune clé ANTHROPIC_API_KEY trouvée dans .env : la chaîne va "
            "tourner en mode démo (pas de génération de messages, pas "
            "d'affinage IA du score). Voir le README pour configurer la clé."
        )

    dossier_sorties = DATA / "sorties"
    prospects_enrichis = dossier_sorties / "prospects_enrichis.csv"
    prospects_scores = dossier_sorties / "prospects_scores.csv"
    crm_db = DATA / "crm.db"
    rapport_html = dossier_sorties / "rapport.html"

    commande_module1 = [
        sys.executable, str(RACINE / "01_enrichissement_messages" / "run.py"),
        "--input", args.prospects, "--output", str(prospects_enrichis),
    ]
    if not a_une_cle:
        commande_module1.append("--sans-messages")
    executer(commande_module1)

    commande_module2 = [
        sys.executable, str(RACINE / "02_scoring" / "run.py"),
        "--input", str(prospects_enrichis), "--output", str(prospects_scores),
    ]
    if not a_une_cle:
        commande_module2.append("--sans-ia")
    executer(commande_module2)

    executer([
        sys.executable, str(RACINE / "05_crm_suivi" / "run.py"),
        "importer", "--csv", str(prospects_scores), "--db", str(crm_db),
    ])

    executer([
        sys.executable, str(RACINE / "06_reporting" / "run.py"),
        "--db", str(crm_db), "--format", "html", "--output", str(rapport_html),
    ])

    print(f"\nTerminé. Ouvre ce fichier dans ton navigateur pour voir le résultat :\n{rapport_html}\n")
    print(f"Le détail des prospects (scores, messages) est dans :\n{prospects_scores}\n")


if __name__ == "__main__":
    main()
