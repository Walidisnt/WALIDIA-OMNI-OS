#!/usr/bin/env python3
"""
Module 6 — Reporting.

Résume les résultats de la chaîne complète à partir du CRM SQLite :
nombre de prospects traités, répartition par statut/score, taux de
réponse.

Usage :
    python run.py --db ../data/crm.db --format texte
    python run.py --db ../data/crm.db --format html --output ../data/sorties/rapport.html
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from reporting import calculer_statistiques, generer_rapport_texte, generer_rapport_html  # noqa: E402


def parser_arguments():
    parser = argparse.ArgumentParser(description="Génère un rapport résumant les résultats de la chaîne.")
    parser.add_argument("--db", default="../data/crm.db")
    parser.add_argument("--format", choices=["texte", "html"], default="texte")
    parser.add_argument("--output", default=None, help="Requis si --format html")
    return parser.parse_args()


def main():
    args = parser_arguments()
    stats = calculer_statistiques(args.db)

    if args.format == "texte":
        print(generer_rapport_texte(stats))
    else:
        if not args.output:
            raise SystemExit("--output est requis avec --format html")
        chemin_sortie = Path(args.output)
        chemin_sortie.parent.mkdir(parents=True, exist_ok=True)
        chemin_sortie.write_text(generer_rapport_html(stats), encoding="utf-8")
        print(f"Rapport HTML écrit : {chemin_sortie}")


if __name__ == "__main__":
    main()
