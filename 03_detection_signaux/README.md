# Module 3 — Détection de signaux

**Statut : codé et fonctionnel.**

## Ce que fait ce module

Pour chaque entreprise, récupère le contenu public de quelques pages de
son site (accueil, actualités, carrières) et demande à Claude d'en
extraire un signal d'achat B2B (recrutement IA/data, levée de fonds,
nouveau produit...). Si le site est inaccessible ou qu'aucun signal
n'est trouvé, la ligne est marquée explicitement (pas d'invention).

Pas de scraping agressif : quelques pages publiques, un seul passage,
aucun contournement de protection anti-bot.

## Entrée

CSV avec les colonnes : `nom, secteur, site_web`.

## Sortie

Le même CSV avec deux colonnes en plus : `signal`, `date_detection`.

## Utilisation

```bash
python run.py --input ../data/exemples/entreprises_exemple.csv \
              --output ../data/sorties/entreprises_signaux.csv
```

Nécessite `ANTHROPIC_API_KEY` dans `.env`.
