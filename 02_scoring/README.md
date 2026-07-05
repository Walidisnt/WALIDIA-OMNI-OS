# Module 2 — Scoring

**Statut : codé et fonctionnel.**

## Ce que fait ce module

Calcule un score par des règles simples (email présent, téléphone
d'entreprise trouvé, rôle décisionnaire, ville cible), puis demande à un
moteur IA (Claude ou Ollama en local, gratuit) de confirmer ou corriger
la catégorie (`chaud` / `tiede` / `froid`). Si l'appel IA échoue, le
score des règles est conservé — le pipeline ne plante jamais pour ça.

## Entrée

Le CSV enrichi produit par le module 1
(`data/sorties/prospects_enrichis.csv`).

## Sortie

Le même CSV, trié par score décroissant (chaud → tiède → froid), avec deux
colonnes en plus : `score` et `score_raison`.

## Utilisation

```bash
python run.py --input ../data/sorties/prospects_enrichis.csv \
              --output ../data/sorties/prospects_scores.csv
```

Avec Ollama en local (gratuit) : ajouter `--moteur ollama`.

Sans aucune IA (règles seules) :

```bash
python run.py --input ../data/sorties/prospects_enrichis.csv \
              --output ../data/sorties/prospects_scores.csv \
              --sans-ia
```
