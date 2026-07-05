#!/usr/bin/env python3
"""
Interface web locale du système de prospection WALIDIA.

Un petit serveur qui tourne sur ta machine (jamais sur internet) et
s'ouvre automatiquement dans ton navigateur. Il enchaîne les mêmes
modules que lancer_tout.py, mais pilotés par des boutons plutôt que des
commandes : importer un CSV, lancer la chaîne, voir le CRM, changer le
statut d'un contact.

Lancement : python app.py (depuis ce dossier, ou via le README racine).
"""
import logging
import os
import subprocess
import sys
import threading
import webbrowser
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, url_for

RACINE = Path(__file__).resolve().parent.parent
DATA = RACINE / "data"
CRM_DB = DATA / "crm.db"
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

sys.path.insert(0, str(RACINE / "05_crm_suivi"))
sys.path.insert(0, str(RACINE / "06_reporting"))
from crm import connecter, lister_contacts, mettre_a_jour_statut, STATUTS_VALIDES  # noqa: E402
from reporting import calculer_statistiques  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)

LIBELLES_STATUTS = {
    "a_contacter": "À contacter",
    "contacte": "Contacté",
    "repondu": "A répondu",
    "rdv_pris": "RDV pris",
    "refus": "Refus",
    "sans_reponse": "Sans réponse",
}


def ollama_disponible():
    try:
        reponse = requests.get(f"{OLLAMA_URL}/api/tags", timeout=2)
        return reponse.status_code == 200
    except requests.RequestException:
        return False


def detecter_moteur():
    if ollama_disponible():
        return "ollama"
    if os.getenv("ANTHROPIC_API_KEY", "").strip():
        return "claude"
    return None


def executer(commande):
    logger.info("Étape : %s", " ".join(str(c) for c in commande))
    resultat = subprocess.run(commande, capture_output=True, text=True)
    if resultat.returncode != 0:
        logger.error("Échec : %s", resultat.stderr[-2000:])
        raise RuntimeError(resultat.stderr[-2000:] or "Erreur inconnue pendant l'exécution.")
    return resultat.stdout


def lancer_chaine(chemin_csv_prospects):
    """Reproduit lancer_tout.py, mais pour un fichier donné par l'utilisateur."""
    moteur = detecter_moteur()

    dossier_sorties = DATA / "sorties"
    prospects_enrichis = dossier_sorties / "prospects_enrichis.csv"
    prospects_scores = dossier_sorties / "prospects_scores.csv"

    commande1 = [
        sys.executable, str(RACINE / "01_enrichissement_messages" / "run.py"),
        "--input", str(chemin_csv_prospects), "--output", str(prospects_enrichis),
    ]
    commande1 += ["--moteur", moteur] if moteur else ["--sans-messages"]
    executer(commande1)

    commande2 = [
        sys.executable, str(RACINE / "02_scoring" / "run.py"),
        "--input", str(prospects_enrichis), "--output", str(prospects_scores),
    ]
    commande2 += ["--moteur", moteur] if moteur else ["--sans-ia"]
    executer(commande2)

    executer([
        sys.executable, str(RACINE / "05_crm_suivi" / "run.py"),
        "importer", "--csv", str(prospects_scores), "--db", str(CRM_DB),
    ])

    return moteur


@app.route("/")
def tableau_de_bord():
    if not CRM_DB.exists():
        return render_template("vide.html")

    connexion = connecter(str(CRM_DB))
    contacts = lister_contacts(connexion)
    connexion.close()

    stats = calculer_statistiques(str(CRM_DB)) if contacts else None

    return render_template(
        "dashboard.html",
        contacts=contacts,
        stats=stats,
        libelles_statuts=LIBELLES_STATUTS,
        statuts_valides=sorted(STATUTS_VALIDES, key=list(LIBELLES_STATUTS).index),
    )


@app.route("/lancer", methods=["GET"])
def formulaire_lancer():
    exemple = DATA / "exemples" / "prospects_exemple.csv"
    moteur = detecter_moteur()
    return render_template("lancer.html", moteur=moteur, exemple=str(exemple), erreur=None)


@app.route("/lancer", methods=["POST"])
def lancer():
    fichier = request.files.get("fichier_csv")

    if fichier and fichier.filename:
        dossier_imports = DATA / "imports"
        dossier_imports.mkdir(parents=True, exist_ok=True)
        horodatage = datetime.now().strftime("%Y%m%d_%H%M%S")
        nom_fichier = Path(fichier.filename).name
        chemin_csv = dossier_imports / f"{horodatage}_{nom_fichier}"
        fichier.save(chemin_csv)
    else:
        chemin_csv = DATA / "exemples" / "prospects_exemple.csv"

    try:
        lancer_chaine(chemin_csv)
    except RuntimeError as erreur:
        moteur = detecter_moteur()
        return render_template(
            "lancer.html", moteur=moteur, exemple=str(DATA / "exemples" / "prospects_exemple.csv"),
            erreur=str(erreur),
        )

    return redirect(url_for("tableau_de_bord"))


@app.route("/contact/<int:contact_id>/statut", methods=["POST"])
def changer_statut(contact_id):
    nouveau_statut = request.form.get("statut")
    connexion = connecter(str(CRM_DB))
    mettre_a_jour_statut(connexion, contact_id, nouveau_statut)
    connexion.close()
    return redirect(url_for("tableau_de_bord"))


def ouvrir_navigateur():
    webbrowser.open("http://127.0.0.1:5000")


if __name__ == "__main__":
    load_dotenv()
    if not os.environ.get("WERKZEUG_RUN_MAIN"):
        threading.Timer(1.0, ouvrir_navigateur).start()
    app.run(host="127.0.0.1", port=5000, debug=False)
