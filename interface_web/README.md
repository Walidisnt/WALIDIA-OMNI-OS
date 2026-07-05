# Interface web

**Statut : codé et fonctionnel.**

## Ce que fait ce composant

Un petit serveur qui tourne sur ta machine (jamais sur internet) et
s'ouvre automatiquement dans ton navigateur par défaut. Il pilote les
modules 1, 2, 5 et 6 par des boutons plutôt que des commandes :

- un formulaire pour importer ton CSV de prospects (ou utiliser
  l'exemple fourni) et lancer la chaîne complète,
- un tableau de bord listant chaque prospect avec son score, ses
  messages générés (si un moteur IA est disponible), et un menu pour
  changer son statut de suivi (à contacter, contacté, répondu...).

Ce n'est pas un site public : rien n'est accessible depuis internet,
seulement depuis ton propre ordinateur (`127.0.0.1`, c'est-à-dire "cette
machine").

## Fichiers

- `app.py` — serveur Flask, réutilise directement `05_crm_suivi/crm.py`
  et `06_reporting/reporting.py`, et appelle les modules 1/2/5 en
  sous-processus (comme `lancer_tout.py`) pour importer de nouveaux
  prospects.
- `templates/` — pages HTML (tableau de bord, formulaire d'import, état
  vide).
- `static/style.css` — habillage visuel, cohérent avec le rapport HTML
  du module 6.

## Utilisation

```bash
python interface_web/app.py
```

Le navigateur s'ouvre automatiquement sur `http://127.0.0.1:5000`. Pour
arrêter le serveur : `Ctrl+C` dans le terminal.
