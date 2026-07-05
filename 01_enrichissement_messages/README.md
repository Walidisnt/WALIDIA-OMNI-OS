# Module 1 — Enrichissement & Génération de messages

**Statut : codé et fonctionnel.**

## Ce que fait ce module

1. Charge le CSV de prospects.
2. Applique les règles de conformité RGPD (`conformite.py`) : un email
   perso sans base légale valide (`consentement`, `fournisseur_conforme`
   ou `publication_pro_volontaire`) est vidé et marqué
   `base_legale=non_collectable`.
3. Cherche le **numéro standard public de l'entreprise**
   (`enrichissement_entreprise.py`) — donnée d'entreprise, pas donnée
   perso, donc toujours collectable. Approche MVP : devine un nom de
   domaine probable (ou utilise la colonne `site_web` si fournie) et
   cherche un numéro sur la page d'accueil / contact / mentions légales.
4. Génère un `message_email` et un `message_linkedin` personnalisés par
   prospect (`generation_messages.py`), via Claude (payant) ou Ollama en
   local (gratuit, voir `--moteur` ci-dessous). L'email inclut toujours
   une mention d'opt-out (ajoutée automatiquement si le modèle l'a
   oubliée).

## Entrée

CSV avec au minimum les colonnes :
`prenom, nom, entreprise, role, ville, email, source_coordonnee, base_legale`

Colonne optionnelle : `site_web` (accélère et fiabilise la recherche du
numéro d'entreprise).

## Sortie

Le même CSV, avec les colonnes de conformité complétées
(`date_collecte`, `opt_out`, `bloctel_verifie`) et ajout de
`telephone_entreprise`, `message_email`, `message_linkedin`.

## Fichiers

- `run.py` — script CLI principal, orchestre les 3 étapes ci-dessus.
- `conformite.py` — validation de la base légale, purge des coordonnées
  non conformes.
- `enrichissement_entreprise.py` — recherche du numéro standard public.
- `generation_messages.py` — appels au moteur IA (Claude ou Ollama) avec retry.

## Utilisation

Avec Claude (nécessite `ANTHROPIC_API_KEY` dans `.env`) :

```bash
python run.py --input ../data/exemples/prospects_exemple.csv \
              --output ../data/sorties/prospects_enrichis.csv
```

Avec Ollama en local (gratuit, voir le README racine pour l'installer) :

```bash
python run.py --input ../data/exemples/prospects_exemple.csv \
              --output ../data/sorties/prospects_enrichis.csv \
              --moteur ollama
```

Pour tester sans aucune IA (conformité + enrichissement entreprise
seulement, messages vides) :

```bash
python run.py --input ../data/exemples/prospects_exemple.csv \
              --output ../data/sorties/prospects_enrichis.csv \
              --sans-messages
```
