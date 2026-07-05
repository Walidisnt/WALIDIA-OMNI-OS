#!/usr/bin/env python3
"""
Lance toute la chaîne de prospection en une seule commande.

Enchaîne : Module 1 (enrichissement + messages) -> Module 2 (scoring) ->
Module 5 (import dans le CRM) -> Module 6 (rapport HTML).

Pensé pour quelqu'un qui ne veut pas taper une commande par module, ni
payer quoi que ce soit : ce script détecte automatiquement le meilleur
moteur IA disponible, gratuit en priorité :
1. Ollama en local (https://ollama.com) s'il est installé et lancé sur
   la machine : gratuit à vie, aucune clé, aucun compte.
2. Sinon, la clé ANTHROPIC_API_KEY dans .env si elle est configurée
   (payant, mais meilleure qualité).
3. Sinon, mode démo : les règles de scoring tournent normalement, mais
   aucun message n'est généré (le pipeline reste 100% gratuit et
   fonctionnel, juste sans IA).
"""
import argparse
import logging
import os
import subprocess
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

RACINE = Path(__file__).resolve().parent
DATA = RACINE / "data"
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def executer(commande):
    logger.info("Étape : %s", " ".join(str(c) for c in commande))
    resultat = subprocess.run(commande)
    if resultat.returncode != 0:
        logger.error("Échec de l'étape ci-dessus, arrêt de la chaîne.")
        sys.exit(resultat.returncode)


def ollama_disponible():
    try:
        reponse = requests.get(f"{OLLAMA_URL}/api/tags", timeout=2)
        return reponse.status_code == 200
    except requests.RequestException:
        return False


def detecter_moteur():
    """Priorité au gratuit : Ollama local d'abord, puis Claude, sinon aucun moteur."""
    if ollama_disponible():
        return "ollama"
    if os.getenv("ANTHROPIC_API_KEY", "").strip():
        return "claude"
    return None


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
    parser.add_argument(
        "--moteur", choices=["auto", "claude", "ollama", "aucun"], default="auto",
        help="Force un moteur précis au lieu de la détection automatique.",
    )
    args = parser.parse_args()

    moteur = detecter_moteur() if args.moteur == "auto" else (None if args.moteur == "aucun" else args.moteur)

    if moteur == "ollama":
        logger.info("Moteur IA détecté : Ollama en local (gratuit, aucune clé requise).")
    elif moteur == "claude":
        logger.info("Moteur IA détecté : Claude (clé ANTHROPIC_API_KEY trouvée, payant).")
    else:
        logger.warning(
            "Aucun moteur IA disponible (ni Ollama en local, ni clé "
            "ANTHROPIC_API_KEY) : la chaîne tourne en mode démo, gratuite, "
            "mais sans génération de messages ni affinage IA du score. "
            "Voir le README pour installer Ollama gratuitement."
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
    if moteur is None:
        commande_module1.append("--sans-messages")
    else:
        commande_module1 += ["--moteur", moteur]
    executer(commande_module1)

    commande_module2 = [
        sys.executable, str(RACINE / "02_scoring" / "run.py"),
        "--input", str(prospects_enrichis), "--output", str(prospects_scores),
    ]
    if moteur is None:
        commande_module2.append("--sans-ia")
    else:
        commande_module2 += ["--moteur", moteur]
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
