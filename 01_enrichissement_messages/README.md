# Module 1 — Enrichissement & Génération de messages

**Statut : structure posée, code pas encore écrit (en attente du feu vert).**

## Ce que fait ce module

Prend un CSV de prospects (`prenom, nom, entreprise, role, ville, email`),
ajoute quelques infos publiques basiques, puis demande à Claude de générer
pour chaque prospect un message email et une variante LinkedIn,
personnalisés.

## Entrée

CSV avec les colonnes : `prenom, nom, entreprise, role, ville, email`.

## Sortie

Le même CSV, avec deux colonnes en plus : `message_email`,
`message_linkedin`.

## Utilisation (une fois codé)

```bash
python enrichir.py --entree prospects.csv --sortie prospects_enrichis.csv
```
