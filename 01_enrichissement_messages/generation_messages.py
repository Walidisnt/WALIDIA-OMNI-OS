"""
Génération des messages de prospection (email + LinkedIn) via l'API Claude.

Un seul appel par prospect (les deux messages sont demandés dans le même
prompt) pour limiter le coût et la latence. Retry simple en cas d'erreur
transitoire, et repli sur des messages vides plutôt qu'un plantage complet
du pipeline si l'API reste indisponible.
"""
import json
import logging
import os
import time

from anthropic import Anthropic, APIError

logger = logging.getLogger(__name__)

NB_TENTATIVES_MAX = 3
DELAI_ENTRE_TENTATIVES_SECONDES = 2

MENTION_OPT_OUT_PAR_DEFAUT = (
    '\n\nSi vous préférez ne plus recevoir de message de ma part, '
    'répondez simplement "STOP".'
)
MOTS_CLES_OPT_OUT = ["stop", "désabonn", "désinscri", "ne plus recevoir"]

PROMPT_SYSTEME = """Tu es un(e) commercial(e) B2B francophone qui écrit des messages de
prospection à froid courts, naturels et directs. Pas de superlatifs vides
("révolutionnaire", "incroyable"), pas de ton robotique, pas de formule
toute faite. Une phrase d'accroche construite sur l'entreprise ou le rôle
du destinataire, puis une proposition de valeur claire, puis une question
ouverte simple pour engager la conversation.

Tu dois toujours répondre en JSON strict avec exactement ces deux clés :
{"message_email": "...", "message_linkedin": "..."}

message_email : 60 à 120 mots, sans ligne d'objet séparée, doit se
terminer par une mention claire d'opt-out ("répondez STOP pour ne plus
recevoir de message").
message_linkedin : 300 caractères maximum, ton encore plus direct et
informel, sans mention d'opt-out (pas nécessaire sur LinkedIn)."""


def construire_prompt_utilisateur(prospect):
    return (
        f"Prospect : {prospect.get('prenom', '')} {prospect.get('nom', '')}\n"
        f"Rôle : {prospect.get('role', '')}\n"
        f"Entreprise : {prospect.get('entreprise', '')}\n"
        f"Ville : {prospect.get('ville', '')}\n\n"
        "Rédige les deux messages de prospection pour ce prospect."
    )


def _extraire_json(texte):
    debut, fin = texte.find("{"), texte.rfind("}")
    if debut == -1 or fin == -1:
        raise ValueError("Réponse du modèle sans JSON exploitable")
    return json.loads(texte[debut : fin + 1])


def generer_messages(prospect, client=None):
    """
    Appelle Claude pour générer message_email et message_linkedin.
    Retourne {"message_email": ..., "message_linkedin": ...}. En cas
    d'échec après plusieurs tentatives, retourne des messages vides.
    """
    client = client or Anthropic()
    modele = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")

    resultat = None
    for tentative in range(1, NB_TENTATIVES_MAX + 1):
        try:
            reponse = client.messages.create(
                model=modele,
                max_tokens=600,
                system=PROMPT_SYSTEME,
                messages=[{"role": "user", "content": construire_prompt_utilisateur(prospect)}],
            )
            resultat = _extraire_json(reponse.content[0].text)
            break
        except (APIError, ValueError, json.JSONDecodeError, IndexError) as erreur:
            logger.warning(
                "Tentative %s/%s échouée pour %s %s : %s",
                tentative, NB_TENTATIVES_MAX,
                prospect.get("prenom"), prospect.get("nom"), erreur,
            )
            if tentative == NB_TENTATIVES_MAX:
                logger.error(
                    "Abandon de la génération pour %s %s après %s tentatives",
                    prospect.get("prenom"), prospect.get("nom"), NB_TENTATIVES_MAX,
                )
                return {"message_email": "", "message_linkedin": ""}
            time.sleep(DELAI_ENTRE_TENTATIVES_SECONDES * tentative)

    message_email = str(resultat.get("message_email", "")).strip()
    message_linkedin = str(resultat.get("message_linkedin", "")).strip()

    if message_email and not any(mot in message_email.lower() for mot in MOTS_CLES_OPT_OUT):
        message_email += MENTION_OPT_OUT_PAR_DEFAUT

    return {"message_email": message_email, "message_linkedin": message_linkedin}
