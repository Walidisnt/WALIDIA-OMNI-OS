# CLAUDE.md — Système d'acquisition B2B automatisé

Ce fichier décrit l'architecture complète du projet pour garder le fil entre
les sessions de travail avec Claude Code. À lire en premier avant toute
modification.

## Contexte

Projet construit pour un Business Developer (pas développeur senior). Tout le
code est en Python pur, commenté en français, et organisé en **6 modules
indépendants** qui forment une chaîne de prospection B2B. Chaque module :

- a son propre dossier numéroté (`01_...` à `06_...`),
- a un `README.md` court expliquant ce qu'il fait,
- s'exécute en ligne de commande, prend un fichier en entrée, écrit un
  fichier en sortie,
- doit fonctionner seul, indépendamment des autres, avant de passer au
  module suivant.

## Règle d'or : un seul module à la fois

**Ne pas coder un module tant que le précédent n'est pas validé par
l'utilisateur.** Cette règle a été explicitement levée par l'utilisateur
le 2026-07-02 ("Fait toute l'app"), qui a demandé que les 6 modules
soient codés d'un coup plutôt que validés un par un. Si une nouvelle
session reprend ce projet, vérifier le statut ci-dessous avant d'écrire
la moindre ligne de code — la prudence "un module à la fois" reste le
comportement par défaut sauf instruction explicite contraire.

## Statut d'avancement

| Module | Nom | Statut |
|---|---|---|
| 1 | Enrichissement & Génération de messages (+ conformité RGPD) | ✅ codé et testé |
| 2 | Scoring | ✅ codé et testé |
| 3 | Détection de signaux | ✅ codé et testé |
| 4 | Infrastructure d'envoi (structure seulement) | ✅ structure posée, **aucun code d'envoi réel** (volontaire) |
| 5 | CRM / suivi (SQLite) | ✅ codé et testé |
| 6 | Reporting | ✅ codé et testé |

Testé de bout en bout localement : module 1 (`--sans-messages`) → module 2
(`--sans-ia`) → module 5 (`importer`, `statut`) → module 6 (`texte` et
`html`). Les appels réels à l'API Claude (modules 1/2/3 sans les
drapeaux `--sans-*`) n'ont pas pu être testés dans cet environnement
(pas de clé `ANTHROPIC_API_KEY`) — à vérifier par l'utilisateur avec sa
propre clé.

## Conformité légale (RGPD) — règle transversale

Ajoutée avant le module 1, s'applique à toute la chaîne : un email/tel
personnel n'est conservé que s'il est rattaché à une base légale valide
(`consentement`, `fournisseur_conforme`, `publication_pro_volontaire`),
sinon il est vidé et marqué `base_legale=non_collectable`
(`01_enrichissement_messages/conformite.py`). Le numéro de standard
d'entreprise n'est pas concerné (donnée d'entreprise, pas donnée perso).
Chaque prospect porte les colonnes `source_coordonnee`, `base_legale`,
`date_collecte`, `opt_out`, `bloctel_verifie`.

## Stack technique

- Python 3.11+, environnement virtuel (`venv`)
- `anthropic` — SDK officiel pour les appels au modèle Claude
  (`claude-sonnet-4-6`)
- `pandas` — manipulation des CSV
- `python-dotenv` — chargement des clés depuis `.env`
- `requests` / `httpx` — appels web pour l'enrichissement
- `sqlite3` (standard) — base CRM locale, à partir du module 5

Clés API et secrets : toujours dans `.env` (jamais en dur dans le code).
`.env.example` documente les variables attendues sans valeurs réelles.

## Architecture des modules

```
WALIDIA-OMNI-OS/
├── CLAUDE.md                       # ce fichier
├── .env.example                    # variables d'environnement attendues
├── .env                            # vraies clés (ignoré par git)
├── requirements.txt                # dépendances Python du système
├── data/
│   ├── exemples/                   # CSV d'exemple pour tester chaque module
│   └── sorties/                    # fichiers générés par les scripts (ignoré par git)
├── 01_enrichissement_messages/     # Module 1
│   ├── README.md
│   ├── run.py                      # script CLI principal
│   ├── conformite.py               # validation RGPD des coordonnées
│   ├── enrichissement_entreprise.py  # recherche du numéro standard public
│   └── generation_messages.py      # appels API Claude (messages)
├── 02_scoring/                     # Module 2
│   ├── README.md
│   ├── run.py
│   └── scoring.py
├── 03_detection_signaux/           # Module 3
│   ├── README.md
│   ├── run.py
│   └── signaux.py
├── 04_infrastructure_envoi/        # Module 4 (structure seulement, pas d'envoi réel)
│   ├── README.md
│   ├── parametres_prevus.md
│   └── templates/introduction.html
├── 05_crm_suivi/                   # Module 5
│   ├── README.md
│   ├── run.py
│   └── crm.py
└── 06_reporting/                   # Module 6
    ├── README.md
    ├── run.py
    └── reporting.py
```

### Module 1 — Enrichissement & Génération de messages

**Entrée** : CSV de prospects (`prenom, nom, entreprise, role, ville, email,
source_coordonnee, base_legale`), colonne `site_web` optionnelle.

**Traitement** :
1. Conformité RGPD (`conformite.py`) : un email sans base légale valide
   (`consentement`, `fournisseur_conforme`, `publication_pro_volontaire`)
   est vidé et marqué `non_collectable`.
2. Recherche du numéro standard public de l'entreprise
   (`enrichissement_entreprise.py`) — donnée d'entreprise, toujours
   collectable. MVP : devine un domaine ou utilise `site_web`, cherche un
   numéro sur les pages accueil/contact/mentions légales.
3. Appel à l'API Claude (modèle `claude-sonnet-4-6`, avec retry) pour
   générer `message_email` (avec mention d'opt-out garantie) et
   `message_linkedin` (`generation_messages.py`).

**Sortie** : CSV enrichi avec les colonnes de conformité complétées, plus
`telephone_entreprise`, `message_email`, `message_linkedin`.

**Commande** : `python 01_enrichissement_messages/run.py --input ... --output ...`
(`--sans-messages` pour tester sans clé API).

### Module 2 — Scoring

Classe chaque prospect en chaud / tiède / froid : un score par règles
(`scoring.py::score_regles`, filet de sécurité toujours actif) affiné par
un appel Claude (`scoring.py::affiner_avec_ia`). Sortie : CSV trié par
score décroissant. `--sans-ia` pour n'utiliser que les règles.

### Module 3 — Détection de signaux

Pour une liste d'entreprises (`nom, secteur, site_web`), récupère le
contenu public de quelques pages du site et demande à Claude d'en
extraire un signal d'achat (`signaux.py`). Aucune invention si le site
est inaccessible ou muet. Sortie : CSV avec `signal` et `date_detection`.

### Module 4 — Infrastructure d'envoi

Le module le plus délicat (délivrabilité, réputation IP/domaine, limites
d'envoi). **Toujours pas de code d'envoi réel** — structure, gabarit
d'email statique et liste des paramètres à valider avant implémentation
(`parametres_prevus.md`). Prérequis avant de coder l'envoi : domaine
dédié, SPF/DKIM/DMARC, warm-up progressif, vérification systématique
d'`opt_out`/`bloctel_verifie`.

### Module 5 — CRM / suivi

Journal local en SQLite (`crm.py`, table `contacts`) : statut
(`a_contacter`, `contacte`, `repondu`, `rdv_pris`, `refus`,
`sans_reponse`), score, base légale. CLI (`run.py`) : sous-commandes
`importer`, `statut`, `liste`. Sert de source de vérité pour le module 6.

### Module 6 — Reporting

Lit la base SQLite du module 5 et calcule les stats (total, contactés,
taux de réponse positive, répartition statut/score). Sortie texte
(console) ou HTML (`reporting.py`, `run.py --format html --output ...`).

## Conventions de code

- Commentaires en français, expliquant le **pourquoi** plus que le quoi.
- Chaque script CLI doit avoir un `--help` clair (via `argparse` ou
  équivalent simple).
- Pas de dépendance ajoutée sans raison directement liée au module en
  cours de construction.
- Aucune clé API en dur dans le code, jamais.

## Script tout-en-un pour utilisateur non technique

`lancer_tout.py` (racine du dépôt) enchaîne les modules 1 → 2 → 5 → 6 en
une seule commande (`python lancer_tout.py`), avec des chemins par défaut
sous `data/`. Il détecte l'absence de `ANTHROPIC_API_KEY` et bascule alors
automatiquement les modules 1 et 2 en mode démo (`--sans-messages`,
`--sans-ia`) plutôt que d'échouer. Le `README.md` racine est écrit pour un
utilisateur non développeur (Business Developer) et pointe vers ce script
en premier ; ce fichier (`CLAUDE.md`) reste la référence technique.

## Historique : ancienne vision du dépôt (résolu le 2026-07-02)

Le dépôt contenait à l'origine un `README.md` (vision growth automation
plus large : scraping LinkedIn, HubSpot/Slack) et un dossier `core/` avec
un stub cassé (`core/__init__.py` importait un `core/orchestrator.py` qui
n'a jamais existé). L'utilisateur a demandé le 2026-07-02 ("Je veux que tu
fasses tout moi je sais rien") de trancher cette ambiguïté sans lui
redemander : le dossier `core/` a été supprimé (code mort, non utilisé
par les 6 modules) et le `README.md` a été réécrit pour décrire le
système réellement construit. L'ancienne version reste consultable dans
l'historique git si besoin.
