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

En local, ce n'est pas un site public : rien n'est accessible depuis
internet, seulement depuis ton propre ordinateur (`127.0.0.1`,
c'est-à-dire "cette machine"). Tu peux aussi la déployer en ligne
gratuitement (section "Déployer en ligne" ci-dessous) — dans ce cas,
elle est protégée par un mot de passe (voir `.env.example`).

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

## Déployer en ligne (gratuit, avec tes vraies données)

Contrairement au site vitrine (`docs/`, une simple page de présentation
sans données réelles), ceci déploie l'app **qui fonctionne vraiment** :
tu peux y importer tes propres prospects et voir de vrais résultats,
accessible depuis n'importe où, pas seulement ta machine.

On utilise **[PythonAnywhere](https://www.pythonanywhere.com)**, pas
Vercel : son offre gratuite garde un stockage persistant (ton CRM ne se
vide pas à chaque redémarrage, contrairement à la plupart des
hébergeurs gratuits comme Render/Railway) et reste accessible en
permanence, sans jamais demander de carte bancaire.

**Limite honnête à connaître** : le compte gratuit de PythonAnywhere
restreint les connexions internet sortantes à une liste d'adresses
autorisées. Résultat : la recherche du numéro d'entreprise (module 1),
la détection de signaux (module 3) et les appels à l'API Claude
risquent de ne pas fonctionner une fois en ligne (ils échouent
proprement, sans planter l'app). Ce qui fonctionne à 100% en ligne :
import de tes prospects, conformité RGPD, scoring par règles, CRM,
tableau de bord, changement de statut.

### Étapes

1. Crée un compte gratuit sur [pythonanywhere.com](https://www.pythonanywhere.com/registration/register/beginner/).
2. Une fois connecté, ouvre un **Bash console** (bouton "Bash" sur le
   tableau de bord) et clone le dépôt :
   ```bash
   git clone https://github.com/Walidisnt/WALIDIA-OMNI-OS.git
   cd WALIDIA-OMNI-OS
   pip install --user -r requirements.txt
   ```
3. Crée ton fichier `.env` avec un mot de passe fort :
   ```bash
   cp .env.example .env
   nano .env
   ```
   Renseigne au minimum `WEB_USERNAME` et `WEB_PASSWORD` (choisis un
   mot de passe que toi seul connais).
4. Onglet **Web** → **Add a new web app** → **Flask** → Python 3.11.
5. Dans la section "Code", édite le fichier WSGI généré
   (`/var/www/tonpseudo_pythonanywhere_com_wsgi.py`) pour qu'il pointe
   vers l'app Flask de ce dépôt :
   ```python
   import sys
   path = '/home/tonpseudo/WALIDIA-OMNI-OS/interface_web'
   if path not in sys.path:
       sys.path.insert(0, path)
   from app import app as application
   ```
6. Section "Static files" : pas nécessaire (le CSS est servi par Flask
   directement).
7. Tape sur le gros bouton vert **Reload**.

Ton app est en ligne à `https://tonpseudo.pythonanywhere.com`, protégée
par le mot de passe que tu as choisi à l'étape 3.
