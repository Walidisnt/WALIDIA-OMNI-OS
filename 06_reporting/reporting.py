"""
Calcule les statistiques de la chaîne complète à partir du CRM SQLite et
les met en forme (texte ou HTML).
"""
import sqlite3

STATUTS_CONTACTES = {"contacte", "repondu", "rdv_pris", "refus", "sans_reponse"}
STATUTS_REPONSE_POSITIVE = {"repondu", "rdv_pris"}


def calculer_statistiques(chemin_db):
    connexion = sqlite3.connect(chemin_db)
    curseur = connexion.cursor()

    curseur.execute("SELECT COUNT(*) FROM contacts")
    total = curseur.fetchone()[0]

    curseur.execute("SELECT statut, COUNT(*) FROM contacts GROUP BY statut")
    repartition_statuts = dict(curseur.fetchall())

    curseur.execute("SELECT score, COUNT(*) FROM contacts GROUP BY score")
    repartition_scores = dict(curseur.fetchall())

    connexion.close()

    nb_contactes = sum(v for k, v in repartition_statuts.items() if k in STATUTS_CONTACTES)
    nb_reponse_positive = sum(v for k, v in repartition_statuts.items() if k in STATUTS_REPONSE_POSITIVE)
    taux_reponse = (nb_reponse_positive / nb_contactes * 100) if nb_contactes else 0.0

    return {
        "total_prospects": total,
        "repartition_statuts": repartition_statuts,
        "repartition_scores": repartition_scores,
        "nb_contactes": nb_contactes,
        "nb_reponse_positive": nb_reponse_positive,
        "taux_reponse": round(taux_reponse, 1),
    }


def generer_rapport_texte(stats):
    lignes = [
        "=== Rapport WALIDIA-OMNI-OS ===",
        f"Prospects au total       : {stats['total_prospects']}",
        f"Prospects contactés      : {stats['nb_contactes']}",
        f"Taux de réponse positive : {stats['taux_reponse']}%",
        "",
        "Répartition par statut :",
    ]
    for statut, nb in stats["repartition_statuts"].items():
        lignes.append(f"  - {statut} : {nb}")
    lignes.append("")
    lignes.append("Répartition par score :")
    for score, nb in stats["repartition_scores"].items():
        lignes.append(f"  - {score} : {nb}")
    return "\n".join(lignes)


def generer_rapport_html(stats):
    lignes_statuts = "".join(f"<li>{statut} : {nb}</li>" for statut, nb in stats["repartition_statuts"].items())
    lignes_scores = "".join(f"<li>{score} : {nb}</li>" for score, nb in stats["repartition_scores"].items())
    return f"""<!DOCTYPE html>
<html lang="fr">
<head><meta charset="utf-8"><title>Rapport WALIDIA-OMNI-OS</title></head>
<body>
<h1>Rapport WALIDIA-OMNI-OS</h1>
<p>Prospects au total : {stats['total_prospects']}</p>
<p>Prospects contactés : {stats['nb_contactes']}</p>
<p>Taux de réponse positive : {stats['taux_reponse']}%</p>
<h2>Répartition par statut</h2>
<ul>{lignes_statuts}</ul>
<h2>Répartition par score</h2>
<ul>{lignes_scores}</ul>
</body>
</html>"""
