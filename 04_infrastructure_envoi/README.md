# Module 4 — Infrastructure d'envoi

**Statut : structure seulement. L'envoi réel d'emails n'est PAS codé.**

## Pourquoi ce module reste vide de code

C'est le module le plus délicat de la chaîne (délivrabilité, réputation
IP/domaine, limites de volume, respect des désinscriptions). Il sera
construit en dernier, une fois que les modules 1, 2, 3 et 5 tournent
correctement et que la question de l'infrastructure d'envoi (domaine
dédié, SPF/DKIM/DMARC, fournisseur SMTP) aura été validée avec
l'utilisateur. Coder un envoi automatisé avant d'avoir réglé ces points
créerait un risque réel (spam, domaine blacklisté, non-respect des
opt-out déjà enregistrés dans le CRM).

## Ce qui existe déjà (documentation / gabarits, pas de code d'envoi)

- `templates/` — gabarits d'emails statiques, à réutiliser plus tard avec
  un moteur de templates (Jinja2) une fois le module codé.
- `parametres_prevus.md` — liste des paramètres qui devront être réglés
  avant tout envoi réel (limites, délais, domaine expéditeur...).

## Prérequis avant de coder ce module

1. Domaine d'envoi dédié (pas le domaine principal de l'entreprise).
2. Enregistrements SPF, DKIM, DMARC configurés et vérifiés.
3. Montée en charge progressive planifiée (warm-up IP/domaine).
4. Vérification systématique de `opt_out` (et `bloctel_verifie` pour les
   appels) dans le CRM avant tout envoi — jamais de contact direct sans
   ce contrôle.
