"""
Enrichissement avec le numéro standard PUBLIC de l'entreprise.

Ce n'est pas une donnée personnelle : une entreprise qui publie son numéro
de standard sur son site le fait pour être contactée, donc toujours
collectable, quelle que soit la situation RGPD du prospect associé.

Approche volontairement simple (MVP) : on devine un nom de domaine probable
à partir du nom de l'entreprise, puis on va chercher un numéro de téléphone
sur la page d'accueil / page contact / mentions légales. Si rien n'est
trouvé, le champ reste vide - on ne bloque jamais le pipeline pour ça.

Limite connue : sans API de recherche (Google/Bing/societe.com), la
devinette de domaine est approximative. Pour un usage en production,
brancher ici une vraie source (ex: societe.com, Google Custom Search, ou
tout simplement une colonne "site_web" fournie en entrée).
"""
import logging
import re
import unicodedata

import requests

logger = logging.getLogger(__name__)

TIMEOUT_SECONDES = 6
PAGES_A_ESSAYER = ["", "contact", "contact/", "mentions-legales", "nous-contacter"]
EXTENSIONS_A_ESSAYER = [".fr", ".com"]

REGEX_TELEPHONE_FR = re.compile(r"(?:\+33|0)\s?[1-9](?:[\s.\-]?\d{2}){4}")


def deviner_domaine(nom_entreprise):
    """Transforme 'Acme SaaS' en 'acmesaas', sans espaces ni accents."""
    normalise = unicodedata.normalize("NFKD", nom_entreprise or "")
    sans_accents = normalise.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-zA-Z0-9]", "", sans_accents).lower()


def rechercher_telephone_entreprise(nom_entreprise, site_web=None, session=None):
    """
    Essaie de trouver le numéro de standard public de l'entreprise.
    Si un site_web est fourni, on l'utilise directement (plus fiable que
    la devinette de domaine). Retourne (telephone, source) ou ("", "").
    """
    session = session or requests.Session()

    urls_de_base = []
    if site_web and str(site_web).strip():
        urls_de_base.append(str(site_web).strip().rstrip("/"))
    else:
        slug = deviner_domaine(nom_entreprise)
        if not slug:
            return "", ""
        urls_de_base = [f"https://www.{slug}{ext}" for ext in EXTENSIONS_A_ESSAYER]

    for base_url in urls_de_base:
        for chemin in PAGES_A_ESSAYER:
            url = f"{base_url}/{chemin}".rstrip("/")
            try:
                reponse = session.get(url, timeout=TIMEOUT_SECONDES)
            except requests.RequestException:
                continue
            if reponse.status_code != 200:
                continue
            correspondance = REGEX_TELEPHONE_FR.search(reponse.text)
            if correspondance:
                return correspondance.group(0), url

    logger.info("Aucun numéro public trouvé pour %s", nom_entreprise)
    return "", ""
