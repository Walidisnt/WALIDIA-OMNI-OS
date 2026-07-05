# Module 5 — CRM / suivi

**Statut : codé et fonctionnel.**

## Ce que fait ce module

Journal local en SQLite (`crm.py`) qui enregistre les prospects importés,
leur score, et le statut de la relation (`a_contacter`, `contacte`,
`repondu`, `rdv_pris`, `refus`, `sans_reponse`). Sert de source de vérité
pour le module 6 (reporting).

Ce module ne contacte personne : il se contente d'enregistrer et de
suivre les statuts. L'envoi effectif reste du ressort du module 4 (non
implémenté).

## Fichiers

- `run.py` — CLI avec 3 sous-commandes : `importer`, `statut`, `liste`.
- `crm.py` — création du schéma SQLite et fonctions d'accès.

## Utilisation

```bash
# Importer les prospects scorés dans le CRM
python run.py importer --csv ../data/sorties/prospects_scores.csv --db ../data/crm.db

# Mettre à jour le statut d'un contact après une réponse
python run.py statut --db ../data/crm.db --id 1 --nouveau-statut repondu

# Lister tous les contacts (ou filtrer par statut)
python run.py liste --db ../data/crm.db
python run.py liste --db ../data/crm.db --statut a_contacter
```
