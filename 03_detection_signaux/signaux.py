"""
Détection de signaux d'achat pour une liste d'entreprises.

Approche MVP : on récupère le contenu texte de quelques pages publiques du
site de l'entreprise (accueil, actualités, carrières), puis on demande à
Claude d'en extraire un signal d'achat pertinent (recrutement IA/data,
levée de fonds, nouveau produit...). Pas de scraping agressif : une
poignée de pages publiques, un seul passage, pas de contournement de
protections anti-bot.
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


def detecter_signal(entreprise, site_web, client=None):
    """Retourne {"signal": str, "date_detection": str (ISO)}."""
    aujourdhui = date.today().isoformat()

    if not str(site_web).strip():
        return {"signal": "aucun signal détecté (pas de site renseigné)", "date_detection": aujourdhui}

    texte = recuperer_texte_site(site_web)
    if not texte.strip():
        return {"signal": "aucun signal détecté (site inaccessible)", "date_detection": aujourdhui}

    client = client or Anthropic()
    modele = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")

    try:
        reponse = client.messages.create(
            model=modele,
            max_tokens=300,
            system=PROMPT_SYSTEME,
            messages=[{"role": "user", "content": f"Entreprise : {entreprise}\n\nContenu du site :\n{texte}"}],
        )
        texte_reponse = reponse.content[0].text
        debut, fin = texte_reponse.find("{"), texte_reponse.rfind("}")
        resultat = json.loads(texte_reponse[debut : fin + 1])
        if resultat.get("signal_detecte"):
            return {"signal": resultat.get("description", ""), "date_detection": aujourdhui}
        return {"signal": "aucun signal détecté", "date_detection": aujourdhui}
    except (APIError, ValueError, json.JSONDecodeError, IndexError) as erreur:
        logger.warning("Détection IA échouée pour %s : %s", entreprise, erreur)
        return {"signal": "erreur lors de la détection", "date_detection": aujourdhui}
