"""
Détection de signaux d'achat pour une liste d'entreprises.

Approche MVP : on récupère le contenu texte de quelques pages publiques du
site de l'entreprise (accueil, actualités, carrières), puis on demande à
un modèle IA d'en extraire un signal d'achat pertinent (recrutement
IA/data, levée de fonds, nouveau produit...). Pas de scraping agressif :
une poignée de pages publiques, un seul passage, pas de contournement de
protections anti-bot.

Deux moteurs IA possibles (voir detecter_signal) : "claude" (payant) ou
"ollama" (modèle gratuit en local, voir ollama.com).
"""
import json
import logging
import os
from datetime import date

import requests
from anthropic import Anthropic, APIError

logger = logging.getLogger(__name__)

TIMEOUT_SECONDES = 6
PAGES_A_ESSAYER = ["", "actualites", "news", "blog", "carrieres", "careers", "jobs"]
LONGUEUR_MAX_TEXTE = 4000

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_TIMEOUT_SECONDES = 120

PROMPT_SYSTEME = """Tu analyses le contenu public du site d'une entreprise pour repérer des
signaux d'achat B2B : recrutements liés à l'IA/la data, levée de fonds,
lancement de produit, expansion, changement de direction. Si tu ne vois
rien de probant dans le texte fourni, dis-le clairement, n'invente rien.

Réponds en JSON strict : {"signal_detecte": true|false, "description": "..."}
"description" : une phrase courte, factuelle, basée uniquement sur le texte fourni."""


def recuperer_texte_site(site_web, session=None):
    session = session or requests.Session()
    site_web = str(site_web).strip().rstrip("/")
    textes = []
    for chemin in PAGES_A_ESSAYER:
        url = f"{site_web}/{chemin}".rstrip("/")
        try:
            reponse = session.get(url, timeout=TIMEOUT_SECONDES)
        except requests.RequestException:
            continue
        if reponse.status_code == 200:
            textes.append(reponse.text)
    return "\n".join(textes)[:LONGUEUR_MAX_TEXTE]


def _appeler_claude(contenu, client=None):
    client = client or Anthropic()
    modele = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")
    reponse = client.messages.create(
        model=modele,
        max_tokens=300,
        system=PROMPT_SYSTEME,
        messages=[{"role": "user", "content": contenu}],
    )
    return reponse.content[0].text


def _appeler_ollama(contenu):
    modele = os.getenv("OLLAMA_MODEL", "llama3.2")
    reponse = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={
            "model": modele,
            "system": PROMPT_SYSTEME,
            "prompt": contenu,
            "stream": False,
            "format": "json",
        },
        timeout=(2, OLLAMA_TIMEOUT_SECONDES),
    )
    reponse.raise_for_status()
    return reponse.json()["response"]


def detecter_signal(entreprise, site_web, moteur="claude", client=None):
    """Retourne {"signal": str, "date_detection": str (ISO)}."""
    aujourdhui = date.today().isoformat()

    if not str(site_web).strip():
        return {"signal": "aucun signal détecté (pas de site renseigné)", "date_detection": aujourdhui}

    texte = recuperer_texte_site(site_web)
    if not texte.strip():
        return {"signal": "aucun signal détecté (site inaccessible)", "date_detection": aujourdhui}

    contenu = f"Entreprise : {entreprise}\n\nContenu du site :\n{texte}"

    try:
        texte_reponse = _appeler_ollama(contenu) if moteur == "ollama" else _appeler_claude(contenu, client=client)
        debut, fin = texte_reponse.find("{"), texte_reponse.rfind("}")
        resultat = json.loads(texte_reponse[debut : fin + 1])
        if resultat.get("signal_detecte"):
            return {"signal": resultat.get("description", ""), "date_detection": aujourdhui}
        return {"signal": "aucun signal détecté", "date_detection": aujourdhui}
    except (APIError, ValueError, json.JSONDecodeError, IndexError, requests.RequestException) as erreur:
        logger.warning("Détection IA échouée pour %s (moteur=%s) : %s", entreprise, moteur, erreur)
        return {"signal": "erreur lors de la détection", "date_detection": aujourdhui}
