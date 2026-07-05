"""
Règles de scoring simples + un appel IA pour affiner le jugement.

Le score final est une catégorie : chaud, tiede, froid. Les règles seules
servent de filet de sécurité si l'appel IA échoue (ou si --sans-ia est
utilisé) : elles doivent donc rester correctes toutes seules.

Deux moteurs IA possibles (voir affiner_avec_ia) : "claude" (payant) ou
"ollama" (modèle gratuit en local, voir ollama.com).
"""
import json
import logging
import os

import requests
from anthropic import Anthropic, APIError

logger = logging.getLogger(__name__)

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_TIMEOUT_SECONDES = 60

MOTS_ROLES_DECIDEURS = [
    "ceo", "cto", "cmo", "coo", "cfo", "vp", "chief", "head of",
    "directeur", "directrice", "fondateur", "fondatrice", "founder",
]

VILLES_CIBLES = {"paris", "lyon", "bordeaux", "toulouse", "nantes", "marseille", "lille"}

CATEGORIES_VALIDES = {"chaud", "tiede", "froid"}


def score_regles(prospect):
    """Score de 0 à 5 basé sur des critères simples et vérifiables."""
    points = 0

    if str(prospect.get("email", "")).strip():
        points += 1
    if str(prospect.get("telephone_entreprise", "")).strip():
        points += 1

    role = str(prospect.get("role", "")).lower()
    if any(mot in role for mot in MOTS_ROLES_DECIDEURS):
        points += 2

    ville = str(prospect.get("ville", "")).lower()
    if ville in VILLES_CIBLES:
        points += 1

    return points


def categorie_depuis_points(points):
    if points >= 4:
        return "chaud"
    if points >= 2:
        return "tiede"
    return "froid"


PROMPT_SYSTEME = """Tu es un(e) SDR B2B expérimenté(e). On te donne un prospect et un
score de base calculé par des règles simples. Ton travail : dire si ce
score de base te semble juste, ou s'il faut le corriger d'un cran (plus
chaud ou plus froid), en te basant sur le rôle et le profil décrits.

Réponds en JSON strict : {"categorie": "chaud"|"tiede"|"froid", "raison": "..."}
"raison" : une phrase courte expliquant le jugement."""


def _appeler_claude(contenu, client=None):
    client = client or Anthropic()
    modele = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")
    reponse = client.messages.create(
        model=modele,
        max_tokens=200,
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


def affiner_avec_ia(prospect, categorie_regles, moteur="claude", client=None):
    """
    Demande au moteur IA choisi ("claude" ou "ollama") de confirmer ou
    corriger la catégorie des règles. En cas d'échec (API, JSON
    invalide...), on garde la catégorie des règles plutôt que de faire
    planter le pipeline.
    """
    contenu = (
        f"Prospect : {prospect.get('role', '')} chez {prospect.get('entreprise', '')}, "
        f"ville : {prospect.get('ville', '')}.\n"
        f"Score de base (règles) : {categorie_regles}.\n"
        "Confirme ou corrige cette catégorie."
    )

    try:
        texte = _appeler_ollama(contenu) if moteur == "ollama" else _appeler_claude(contenu, client=client)
        debut, fin = texte.find("{"), texte.rfind("}")
        resultat = json.loads(texte[debut : fin + 1])
        categorie = resultat.get("categorie", categorie_regles)
        if categorie not in CATEGORIES_VALIDES:
            categorie = categorie_regles
        return categorie, resultat.get("raison", "")
    except (APIError, ValueError, json.JSONDecodeError, IndexError, requests.RequestException) as erreur:
        logger.warning("Affinage IA échoué (moteur=%s), on garde le score des règles : %s", moteur, erreur)
        return categorie_regles, "affinage IA indisponible, score des règles conservé"
