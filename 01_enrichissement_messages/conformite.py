"""
Règles de conformité légale (RGPD) pour les coordonnées personnelles.

Une coordonnée perso (email, téléphone perso) n'est conservée que si elle
est rattachée à une base légale valide parmi les 3 autorisées. Sinon on la
vide et on trace la raison, pour pouvoir justifier la décision en cas de
contrôle. Le numéro de standard de l'entreprise n'est PAS concerné par ces
règles : ce n'est pas une donnée personnelle.
"""
from datetime import date

BASES_LEGALES_VALIDES = {
    "consentement",
    "fournisseur_conforme",
    "publication_pro_volontaire",
}

BASE_LEGALE_NON_COLLECTABLE = "non_collectable"

COLONNES_CONFORMITE = [
    "source_coordonnee",
    "base_legale",
    "date_collecte",
    "opt_out",
    "bloctel_verifie",
]


def base_legale_valide(valeur):
    """Vrai si la valeur correspond à une des 3 bases légales autorisées."""
    if valeur is None:
        return False
    return str(valeur).strip() in BASES_LEGALES_VALIDES


def appliquer_regles_conformite(df):
    """
    Applique la règle d'or : un email perso sans base légale valide est
    vidé et marqué "non_collectable". Ajoute les colonnes de conformité
    manquantes avec des valeurs par défaut sûres.
    """
    df = df.copy()

    if "source_coordonnee" not in df.columns:
        df["source_coordonnee"] = ""
    if "base_legale" not in df.columns:
        df["base_legale"] = ""
    if "date_collecte" not in df.columns:
        df["date_collecte"] = ""
    if "opt_out" not in df.columns:
        df["opt_out"] = False
    if "bloctel_verifie" not in df.columns:
        df["bloctel_verifie"] = False

    for i, ligne in df.iterrows():
        a_un_email = bool(str(ligne.get("email", "")).strip())

        if a_un_email and not base_legale_valide(ligne.get("base_legale")):
            df.at[i, "email"] = ""
            df.at[i, "base_legale"] = BASE_LEGALE_NON_COLLECTABLE
        elif not a_un_email and not str(ligne.get("base_legale", "")).strip():
            df.at[i, "base_legale"] = BASE_LEGALE_NON_COLLECTABLE

        if not str(df.at[i, "date_collecte"]).strip():
            df.at[i, "date_collecte"] = date.today().isoformat()

    df["opt_out"] = df["opt_out"].apply(lambda v: str(v).strip().lower() in {"true", "1"})
    df["bloctel_verifie"] = df["bloctel_verifie"].apply(lambda v: str(v).strip().lower() in {"true", "1"})

    return df
