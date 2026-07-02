"""
CRM minimal en SQLite : journal des prospects contactés et de leurs statuts.

Table unique "contacts" — un CRM plus riche viendra si le besoin se
confirme, mais on ne complexifie pas avant d'en avoir la preuve.
"""
import sqlite3
from datetime import date

SCHEMA = """
CREATE TABLE IF NOT EXISTS contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prenom TEXT,
    nom TEXT,
    entreprise TEXT,
    email TEXT,
    telephone_entreprise TEXT,
    score TEXT,
    base_legale TEXT,
    opt_out INTEGER DEFAULT 0,
    statut TEXT DEFAULT 'a_contacter',
    date_import TEXT,
    date_dernier_contact TEXT,
    notes TEXT
);
"""

STATUTS_VALIDES = {"a_contacter", "contacte", "repondu", "rdv_pris", "refus", "sans_reponse"}


def connecter(chemin_db):
    connexion = sqlite3.connect(chemin_db)
    connexion.execute(SCHEMA)
    connexion.commit()
    return connexion


def importer_prospects(connexion, df):
    """Insère les prospects d'un DataFrame (sortie module 1/2) dans le CRM."""
    aujourdhui = date.today().isoformat()
    curseur = connexion.cursor()
    for _, ligne in df.iterrows():
        opt_out_brut = str(ligne.get("opt_out", "")).strip().lower()
        curseur.execute(
            """INSERT INTO contacts
               (prenom, nom, entreprise, email, telephone_entreprise, score,
                base_legale, opt_out, statut, date_import)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'a_contacter', ?)""",
            (
                ligne.get("prenom", ""),
                ligne.get("nom", ""),
                ligne.get("entreprise", ""),
                ligne.get("email", ""),
                ligne.get("telephone_entreprise", ""),
                ligne.get("score", ""),
                ligne.get("base_legale", ""),
                1 if opt_out_brut in {"true", "1"} else 0,
                aujourdhui,
            ),
        )
    connexion.commit()
    return len(df)


def mettre_a_jour_statut(connexion, contact_id, nouveau_statut):
    if nouveau_statut not in STATUTS_VALIDES:
        raise ValueError(f"Statut inconnu : {nouveau_statut}. Valeurs possibles : {sorted(STATUTS_VALIDES)}")
    connexion.execute(
        "UPDATE contacts SET statut = ?, date_dernier_contact = ? WHERE id = ?",
        (nouveau_statut, date.today().isoformat(), contact_id),
    )
    connexion.commit()


def lister_contacts(connexion, statut=None):
    curseur = connexion.cursor()
    if statut:
        curseur.execute("SELECT * FROM contacts WHERE statut = ?", (statut,))
    else:
        curseur.execute("SELECT * FROM contacts")
    colonnes = [description[0] for description in curseur.description]
    return [dict(zip(colonnes, ligne)) for ligne in curseur.fetchall()]
