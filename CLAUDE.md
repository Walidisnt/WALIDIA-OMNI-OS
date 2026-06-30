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
l'utilisateur.** Si une session reprend ce projet, vérifier le statut
ci-dessous avant d'écrire la moindre ligne de code.

## Statut d'avancement

| Module | Nom | Statut |
|---|---|---|
| 1 | Enrichissement & Génération de messages | ⏳ en attente du feu vert utilisateur |
| 2 | Scoring | 🔒 pas commencé |
| 3 | Détection de signaux | 🔒 pas commencé |
| 4 | Infrastructure d'envoi (structure seulement) | 🔒 pas commencé |
| 5 | CRM / suivi (SQLite) | 🔒 pas commencé |
| 6 | Reporting | 🔒 pas commencé |

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
│   └── exemples/                   # fichiers CSV d'exemple pour tester chaque module
├── 01_enrichissement_messages/     # Module 1
│   ├── README.md
│   ├── enrichir.py                 # script CLI principal
│   └── (futurs fichiers de support)
├── 02_scoring/                     # Module 2
│   └── README.md
├── 03_detection_signaux/           # Module 3
│   └── README.md
├── 04_infrastructure_envoi/        # Module 4 (structure seulement pour l'instant)
│   └── README.md
├── 05_crm_suivi/                   # Module 5
│   └── README.md
└── 06_reporting/                   # Module 6
    └── README.md
```

### Module 1 — Enrichissement & Génération de messages

**Entrée** : CSV de prospects (`prenom, nom, entreprise, role, ville, email`).

**Traitement** :
1. Enrichissement basique avec des infos publiques (à définir précisément
   avant de coder — sources simples, pas de scraping agressif).
2. Appel à l'API Claude (modèle `claude-sonnet-4-6`) pour générer, pour
   chaque prospect, un message de prospection personnalisé : une version
   email et une version LinkedIn.

**Sortie** : CSV enrichi avec deux colonnes ajoutées : `message_email` et
`message_linkedin`.

**Prochaine étape** : attendre le feu vert utilisateur avant de coder ce
module.

### Module 2 — Scoring

Classe chaque prospect en chaud / tiède / froid à partir de critères simples
(complétude des données, rôle, ville, etc.) combinés à un appel IA pour
affiner le jugement. Sortie : CSV trié par score décroissant.

### Module 3 — Détection de signaux

Pour une liste d'entreprises, recherche des signaux d'achat (recrutements
IA/data, actualités pertinentes). Sortie : liste d'entreprises avec leurs
signaux et la date de détection.

### Module 4 — Infrastructure d'envoi

Le module le plus délicat (délivrabilité, réputation IP/domaine, limites
d'envoi). **Construit en dernier avant le reporting.** Pour l'instant : poser
uniquement la structure du dossier et la documentation, **ne pas coder
l'envoi réel d'emails**.

### Module 5 — CRM / suivi

Journal local en SQLite : qui a été contacté, quand, statut des réponses.
Sert de source de vérité pour le module 6.

### Module 6 — Reporting

Tableau de bord simple (texte ou HTML basique) résumant les résultats de la
chaîne complète : nombre de prospects traités, taux de réponse, etc.

## Conventions de code

- Commentaires en français, expliquant le **pourquoi** plus que le quoi.
- Chaque script CLI doit avoir un `--help` clair (via `argparse` ou
  équivalent simple).
- Pas de dépendance ajoutée sans raison directement liée au module en
  cours de construction.
- Aucune clé API en dur dans le code, jamais.

## Note sur le reste du dépôt

Ce dépôt contient aussi un `README.md` et un dossier `core/` issus d'une
vision antérieure et plus large du projet (scraping LinkedIn, intégrations
HubSpot/Slack, etc.) qui n'a pas encore été implémentée concrètement
(`core/orchestrator.py` n'existe pas). Le système décrit dans ce
`CLAUDE.md` est une reconstruction plus progressive et pragmatique, module
par module. Les deux visions ne sont pas encore réconciliées — à clarifier
avec l'utilisateur avant d'aller plus loin.
