# WALIDIA OMNI-OS — système de prospection B2B

Un outil qui prend une liste de prospects (CSV) et produit, pour chacun,
un message de prospection personnalisé, un score (chaud/tiède/froid), un
suivi dans un CRM local, et un rapport de résultats. Tout tourne sur ta
machine, en ligne de commande.

Ce guide est écrit pour quelqu'un qui ne code pas. Suis les étapes dans
l'ordre.

## 1. Installer (une seule fois)

Il te faut Python 3.11 ou plus installé sur ta machine. Ensuite, dans un
terminal, place-toi dans ce dossier et lance :

```bash
python3 -m venv venv
source venv/bin/activate        # sur Windows : venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Choisir comment l'IA génère les messages (100% gratuit possible)

L'outil détecte automatiquement, dans cet ordre, ce qui est disponible sur
ta machine — tu n'as rien à configurer si tu ne veux pas :

| Option | Coût | Qualité | Ce qu'il faut faire |
|---|---|---|---|
| **Ollama en local (recommandé si tu veux du gratuit)** | Gratuit à vie, aucun compte | Correcte | Installer un programme gratuit (5 min, voir ci-dessous) |
| **API Anthropic (Claude)** | Payant à l'usage | Meilleure | Créer un compte et une clé API |
| **Aucun des deux** | Gratuit | Pas de messages générés (juste le score par règles) | Rien à faire, c'est le mode par défaut |

### Option gratuite : installer Ollama (recommandé)

1. Va sur [ollama.com](https://ollama.com/download) et installe le
   programme pour ton système (Mac/Windows/Linux) — comme un logiciel
   classique, aucune carte bancaire ni compte demandé.
2. Une fois installé, ouvre un terminal et lance une seule fois :
   ```bash
   ollama pull llama3.2
   ```
   (télécharge le modèle IA gratuit, ~2 Go, une seule fois).
3. C'est tout. Ollama tourne en arrière-plan automatiquement après
   l'installation. La prochaine fois que tu lances `python lancer_tout.py`,
   il détectera Ollama tout seul et générera les messages avec, sans que
   tu aies rien à activer.

### Option payante : clé API Anthropic (si tu préfères la meilleure qualité)

1. Crée un compte sur [console.anthropic.com](https://console.anthropic.com/)
   et récupère une clé API.
2. Copie le fichier `.env.example` en `.env` :
   ```bash
   cp .env.example .env
   ```
3. Ouvre `.env` avec un éditeur de texte et colle ta clé après
   `ANTHROPIC_API_KEY=`.

Ne partage jamais ce fichier `.env` (il n'est pas suivi par git, c'est
normal). Si Ollama ET une clé Anthropic sont disponibles en même temps,
l'outil choisit Ollama en priorité (le gratuit).

## 3. Lancer l'outil

Avec le fichier d'exemple fourni (pour voir comment ça marche) :

```bash
python lancer_tout.py
```

Avec tes propres prospects :

```bash
python lancer_tout.py --prospects chemin/vers/mon_fichier.csv
```

Ton CSV doit avoir au minimum ces colonnes :
`prenom, nom, entreprise, role, ville, email, source_coordonnee, base_legale`

Les colonnes `source_coordonnee` et `base_legale` servent à respecter le
RGPD (voir section 5 ci-dessous) — laisse-les vides si tu ne sais pas
quoi mettre, l'outil videra automatiquement les emails non conformes
plutôt que de prendre un risque.

## 4. Voir le résultat

À la fin, le script t'indique où trouver :
- un **rapport HTML** (`data/sorties/rapport.html`) — ouvre-le dans ton
  navigateur,
- un **CSV détaillé** (`data/sorties/prospects_scores.csv`) — avec le
  score et les messages générés pour chaque prospect.

## 5. Ce que fait l'outil, en résumé

L'outil enchaîne 6 briques (« modules »), chacune dans son propre
dossier numéroté (`01_...` à `06_...`). Le détail technique complet est
dans `CLAUDE.md`, mais voici l'essentiel :

1. **Enrichissement & messages** — vérifie que chaque email a une base
   légale valide (sinon il est supprimé automatiquement), cherche le
   numéro de téléphone public de l'entreprise, génère un message email
   et un message LinkedIn personnalisés.
2. **Scoring** — classe chaque prospect en chaud / tiède / froid.
3. **Détection de signaux** — repère des signaux d'achat sur le site
   d'une entreprise (recrutement, actualité...).
4. **Infrastructure d'envoi** — **pas encore activée volontairement**.
   L'outil ne t'envoie aucun email à ta place pour l'instant (voir
   `04_infrastructure_envoi/README.md`).
5. **CRM** — garde en mémoire (base locale) qui a été contacté et avec
   quel résultat.
6. **Rapport** — résume les chiffres (combien de prospects, taux de
   réponse...).

Tu peux aussi lancer chaque module séparément si tu veux plus de
contrôle : chaque dossier a son propre `README.md` avec la commande
exacte.

## 6. Ce que l'outil ne fait PAS (encore)

- Il n'envoie aucun email ni message automatiquement — les messages
  générés sont à copier-coller toi-même, ou à activer plus tard une
  fois l'infrastructure d'envoi mise en place proprement.
- Il ne récupère pas de coordonnées personnelles sans base légale : un
  email sans justification valide est automatiquement supprimé.

## Besoin d'aller plus loin ?

`CLAUDE.md` contient la documentation technique complète (architecture,
conventions de code, statut de chaque module) — utile si tu reprends ce
projet avec Claude Code dans une prochaine session.
