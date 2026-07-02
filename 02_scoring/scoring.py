"""
Règles de scoring simples + un appel Claude pour affiner le jugement.

Le score final est une catégorie : chaud, tiede, froid. Les règles seules
servent de filet de sécurité si l'appel IA échoue (ou si --sans-ia est
utilisé) : elles doivent donc rester correctes toutes seules.
"""
import json
import logging
import os

from anthropic import Anthropic, APIError

logger = logging.getLogger(__name__)

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


def affiner_avec_ia(prospect, categorie_regles, client=None):
    """
    Demande à Claude de confirmer ou corriger la catégorie des règles.
    En cas d'échec (API, JSON invalide...), on garde la catégorie des
    règles plutôt que de faire planter le pipeline.
    """
    client = client or Anthropic()
    modele = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")

    contenu = (
        f"Prospect : {prospect.get('role', '')} chez {prospect.get('entreprise', '')}, "
        f"ville : {prospect.get('ville', '')}.\n"
        f"Score de base (règles) : {categorie_regles}.\n"
        "Confirme ou corrige cette catégorie."
    )

    try:
        reponse = client.messages.create(
            model=modele,
            max_tokens=200,
            system=PROMPT_SYSTEME,
            messages=[{"role": "user", "content": contenu}],
        )
        texte = reponse.content[0].text
        debut, fin = texte.find("{"), texte.rfind("}")
        resultat = json.loads(texte[debut : fin + 1])
        categorie = resultat.get("categorie", categorie_regles)
        if categorie not in CATEGORIES_VALIDES:
            categorie = categorie_regles
        return categorie, resultat.get("raison", "")
    except (APIError, ValueError, json.JSONDecodeError, IndexError) as erreur:
        logger.warning("Affinage IA échoué, on garde le score des règles : %s", erreur)
        return categorie_regles, "affinage IA indisponible, score des règles conservé"
