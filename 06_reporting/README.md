# Module 6 — Reporting

**Statut : codé et fonctionnel.**

## Ce que fait ce module

Lit la base SQLite du CRM (module 5) et calcule : nombre total de
prospects, nombre de prospects contactés, taux de réponse positive
(`repondu` + `rdv_pris`), répartition par statut et par score. Sort le
résultat en texte (console) ou en fichier HTML basique.

## Entrée

La base SQLite produite par le module 5 (`data/crm.db`).

## Sortie

Rapport texte affiché en console, ou fichier HTML si `--format html`.

## Utilisation

```bash
python run.py --db ../data/crm.db --format texte

python run.py --db ../data/crm.db --format html --output ../data/sorties/rapport.html
```
