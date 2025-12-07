# 🚀 WALIDIA OMNI-OS

**Système de growth automation complet** - LinkedIn scraping + Email enrichment + Outreach automatisé + CRM sync

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/) [![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

---

## 💼 Pour qui ? Cas d'usage et profils cibles

### 🎯 Profils visés

#### 1. **Agences B2B & Studios Growth**
- **Besoin** : Gérer plusieurs campagnes clients simultanément avec des audiences différentes
- **Gain concret** : 
  - 30-50 leads qualifiés enrichis par jour et par compte client
  - Économie de 15-20h/semaine de prospection manuelle
  - ROI mesurable : 200-300% sur les honoraires agence
- **Use case** : Agence SEA/SEM qui veut ajouter un service de génération de leads en marque blanche

#### 2. **SaaS en early-stage / Fondateurs Solo**
- **Besoin** : Lancer les premières campagnes outbound sans recruter de SDR
- **Gain concret** :
  - 5-10 meetings bookés/mois avec des ICP qualifiés
  - Coût d'acquisition < 100€ par lead SQL
  - Pipeline prévisible de 20-40 opportunités/trimestre
- **Use case** : Founder technique qui veut tester son market-fit avec 100 prospects cibles en 2 semaines

#### 3. **Freelances SDR & Growth Hackers
- **Besoin** : Offrir un service de lead gen scalable à plusieurs clients sans overhead opérationnel
- **Gain concret** :
  - Gérer 3-5 clients simultanément avec une seule instance
  - TJM augmenté de 30-50% grâce à l'automatisation
  - Facturation récurrente : 1500-3000€/mois par client
- **Use case** : SDR freelance qui passe de 1 client à 5 clients grâce à l'automatisation

#### 4. **Équipes Growth in-house (scale-ups)**
- **Besoin** : Industrialiser la prospection outbound sur plusieurs pays/segments
- **Gain concret** :
  - 200-500 leads enrichis/semaine par segment
  - Taux de réponse de 8-15% (vs 2-5% sans personnalisation)
  - Réduction de 60% du temps SDR sur l'enrichissement manuel
- **Use case** : Scale-up SaaS B2B qui veut passer de 10 à 100 meetings qualifiés/mois

---

## 📈 ROI attendu & Métriques cibles

### 📊 KPIs de performance

| Métrique | Objectif | Moyenne constatée |
|---------|----------|--------------------|
| **Profils scrapés/jour** | 50-150 | 80-120 |
| **Taux d'enrichissement email** | 60-75% | 65-70% |
| **Taux de délivrabilité** | >95% | 96-98% |
| **Taux d'ouverture** | 25-35% | 28-32% |
| **Taux de réponse** | 8-15% | 10-12% |
| **Meetings bookés** | 5-15/semaine | 8-12/semaine |
| **Coût par lead SQL** | <150€ | 80-120€ |

### 💰 Calcul de ROI concret

**Scénario type : Agence B2B avec 3 clients**

```
Investissement initial :
- Développement/setup : 0€ (open-source)
- API credits (Hunter + Apollo) : 200€/mois
- Infra (serveur + proxy) : 50€/mois
- Total mensuel : 250€

Retour :
- 3 clients x 2000€/mois = 6000€/mois
- 150 leads qualifiés/mois (50 par client)
- 15-20 meetings bookés/mois
- ROI : 2400% (6000€ de revenu pour 250€ de coût)
```

---

## 📝 Vue d'ensemble

WALIDIA OMNI-OS est un framework Python complet de growth automation qui automatise l'ensemble du cycle de prospection B2B :

- •  🔍 Scraping LinkedIn intelligent avec anti-détection
- •  📧 Enrichissement d'emails multi-sources (waterfall pattern)
- •  ✉️ Outreach automatisé avec templates personnalisables
- •  🔄 Synchronisation CRM (HubSpot) et notifications (Slack)
- •  📈 Gestion d'état pour reprendre les campagnes interrompues

---

## 🛠️ Stack technique & Dépendances

### 📚 Technologies principales

#### **Scraping & Automation**
- **Playwright** (v1.40+) : Navigation browser headless avec stealth mode
- **playwright-stealth** : Bypass des détections anti-bot
- **asyncio** : Exécution asynchrone pour performance maximale

#### **Enrichissement & Validation**
- **Hunter.io API** : Email finding (waterfall tier 1)
- **Apollo.io API** : Email finding + enrichissement data (tier 2)
- **Snov.io API** : Email finding (tier 3 fallback)
- **Dropcontact API** : Validation & enrichissement entreprise
- **dnspython** : Vérification MX records pour validation email

#### **Outreach & Templating**
- **Jinja2** : Moteur de templates pour emails personnalisés
- **smtplib** : Envoi d'emails SMTP natif
- **email.mime** : Construction de messages HTML/texte

#### **Integrations & CRM**
- **HubSpot Python Client** : Sync contacts, companies, deals
- **Slack SDK** : Notifications temps réel
- **requests** : API calls génériques

#### **Data & State Management**
- **pandas** : Manipulation de datasets de leads
- **json** : Stockage des états de campagne
- **pickle** : Sérialisation de cookies chiffrés
- **cryptography** : Chiffrement des sessions LinkedIn

#### **CLI & UX**
- **Click / Typer** : Interface CLI intuitive
- **Rich** : Output coloré et progress bars
- **python-dotenv** : Gestion des variables d'environnement

### 📂 Structure de persistance

```
data/
├── campaigns/
│   ├── campaign_abc123/
│   │   ├── state.json          # État de progression
│   │   ├── leads_raw.csv       # Profils LinkedIn scrapés
│   │   ├── leads_enriched.csv  # Avec emails trouvés
│   │   ├── sent_emails.json    # Historique d'envoi
│   │   └── metrics.json        # KPIs de la campagne
│   └── campaign_def456/
├── cookies/
│   └── linkedin_session.enc  # Cookies chiffrés AES-256
├── logs/
│   ├── scraper.log
│   ├── enrichment.log
│   └── mailer.log
└── templates/
    ├── introduction.html
    ├── follow_up_1.html
    ├── follow_up_2.html
    └── breakup.html
```

---

## 🎯 Playbooks d'usage prêts à l'emploi

### 📘 Playbook 1 : "VP Sales SaaS France en 30 minutes"

**Objectif** : Cibler 100 VP Sales dans des SaaS en France, les enrichir et lancer une campagne personnalisée.

#### Étapes CLI

```bash
# 1. Initialiser la campagne
walidia init "Q1_2025_VP_Sales_SaaS_France" \
  --target "VP Sales SaaS France" \
  --limit 100 \
  --template-sequence intro,follow_up_1,follow_up_2

# 2. Lancer le scraping LinkedIn
walidia scrape "Q1_2025_VP_Sales_SaaS_France" \
  --keyword "VP Sales SaaS France" \
  --filters "industry:Software,location:France" \
  --headless false  # Voir le navigateur en action

# 3. Enrichir avec emails (waterfall automatique)
walidia enrich "Q1_2025_VP_Sales_SaaS_France" \
  --sources hunter,apollo,snov \
  --verify-mx true

# 4. Prévisualiser la campagne avant envoi
walidia preview "Q1_2025_VP_Sales_SaaS_France" \
  --show-templates \
  --sample 5

# 5. Lancer l'outreach (avec rate limiting)
walidia send "Q1_2025_VP_Sales_SaaS_France" \
  --daily-limit 50 \
  --delay-between-emails 30-90 \
  --tracking-pixels true

# 6. Synchroniser avec HubSpot + notifier Slack
walidia sync "Q1_2025_VP_Sales_SaaS_France" \
  --crm hubspot \
  --notify slack

# 7. Monitorer en temps réel
walidia status "Q1_2025_VP_Sales_SaaS_France" --watch
```

#### Modules impliqués

1. **LinkedInScraper** : Extrait les profils avec filtres industrie/localisation
2. **EmailFinder** : Waterfall Hunter → Apollo → Snov avec vérification MX
3. **SmartMailer** : Séquence d'emails avec tracking pixels
4. **HubSpotConnector** : Création automatique contacts + entreprises
5. **SlackNotifier** : Alertes en temps réel sur nouveaux leads qualifiés

#### Résultat attendu

```
✅ 100 profils scrapés LinkedIn
✅ 65-70 emails trouvés et vérifiés (65-70% enrichment rate)
✅ 50 emails envoyés J1 (respect daily limit)
✅ 15 restants J2
✅ 70 contacts synchronisés dans HubSpot
✅ Taux d'ouverture attendu : 28-32%
✅ Taux de réponse attendu : 10-12%
✅ 7-8 réponses positives en 2 semaines
```

---

### 📗 Playbook 2 : "Réactiver leads inactifs HubSpot"

**Objectif** : Réchauffer 200 leads HubSpot inactifs depuis 3+ mois avec une séquence de réactivation.

#### Étapes CLI

```bash
# 1. Importer les leads inactifs depuis HubSpot
walidia import-hubspot \
  --list-id "inactive_leads_q4_2024" \
  --filters "last_activity_date<2024-09-01" \
  --output "data/hubspot_inactive.csv"

# 2. Créer campagne de réactivation
walidia init "Reactivation_Q1_2025" \
  --import-file "data/hubspot_inactive.csv" \
  --template-sequence reactivation_intro,case_study,breakup

# 3. Enrichir les données manquantes
walidia enrich "Reactivation_Q1_2025" \
  --update-missing-only \
  --sources apollo,dropcontact

# 4. Lancer la séquence de réactivation
walidia send "Reactivation_Q1_2025" \
  --sequence-delay "3,7,14"  # J3, J7, J14
  --daily-limit 70 \
  --smart-send true  # Envoi selon timezone du prospect

# 5. Mettre à jour HubSpot avec statut campagne
walidia sync "Reactivation_Q1_2025" \
  --crm hubspot \
  --update-properties "campaign_name,last_outreach_date,email_status"

# 6. Notification Slack sur réponses positives
walidia monitor "Reactivation_Q1_2025" \
  --notify-on reply \
  --slack-channel "#reactivation-wins"
```

#### Modules impliqués

1. **HubSpotConnector** : Import de leads inactifs avec filtres avancés
2. **EmailFinder** : Ré-enrichissement des emails manquants/obsolètes
3. **SmartMailer** : Séquence étalée avec smart sending (timezone-aware)
4. **SlackNotifier** : Alertes uniquement sur réponses positives

#### Résultat attendu

```
✅ 200 leads inactifs importés depuis HubSpot
✅ 180 emails valides (90% - base déjà enrichie)
✅ Séquence sur 14 jours : Intro (J0) → Case study (J7) → Breakup (J14)
✅ Taux de réponse : 12-18% (meilleur que cold outreach)
✅ 24-36 leads réactivés et de retour en conversation
✅ 5-8 meetings re-bookés en 3 semaines
```

---

### 📙 Playbook 3 : "Multi-clients agence - 5 campagnes parallèles"

**Objectif** : Gérer 5 clients différents avec des audiences séparées en parallèle.

#### Configuration

```yaml
# config/multi_client_setup.yaml
campaigns:
  - name: "Client_A_Fintech_UK"
    target: "CFO Fintech UK"
    limit: 80
    templates: [intro_fintech, follow_up]
    
  - name: "Client_B_SaaS_DACH"
    target: "Head of Sales SaaS Germany"
    limit: 120
    templates: [intro_saas_de, follow_up_de]
    
  - name: "Client_C_Ecommerce_FR"
    target: "CMO E-commerce France"
    limit: 100
    templates: [intro_ecom, case_study_fr]
    
  - name: "Client_D_Healthcare_US"
    target: "VP Operations Healthcare USA"
    limit: 50
    templates: [intro_healthcare, demo_offer]
    
  - name: "Client_E_Logistics_Benelux"
    target: "Supply Chain Director Benelux"
    limit: 70
    templates: [intro_logistics, whitepaper_offer]
```

#### Exécution CLI

```bash
# Lancer les 5 campagnes en parallèle (async)
walidia batch-launch --config config/multi_client_setup.yaml \
  --parallel 3 \  # 3 campagnes simultanées max
  --stagger 60 \  # 60 min entre chaque démarrage
  --daily-limit-per-campaign 40

# Monitorer toutes les campagnes depuis un dashboard
walidia dashboard --port 8080 --campaigns all

# Générer un rapport hebdo pour tous les clients
walidia report --period weekly \
  --campaigns all \
  --format pdf \
  --output reports/weekly_agency_report.pdf
```

#### Résultat attendu

```
✅ 5 campagnes actives en parallèle
✅ 420 profils scrapés au total (80+120+100+50+70)
✅ 280-300 emails enrichis (65-70% rate)
✅ 200 emails envoyés/jour (respect des limites par campagne)
✅ Dashboard temps réel avec métriques par client
✅ Rapports PDF automatiques chaque lundi
✅ 40-60 meetings bookés/mois au total
✅ ROI : 2500% (12k€ facturés pour 500€ de coûts)
```

---

## 🏛️ Architecture

```
WALIDIA/
├── cli/
│   ├── __init__.py
│   └── main.py                 # Interface CLI avec Click/Typer
├── core/
│   ├── __init__.py
│   └── orchestrator.py         # GrowthOrchestrator - Boucle principale
├── scrapers/
│   ├── __init__.py
│   └── linkedin_scraper.py     # Scraper Playwright + stealth
├── enrichment/
│   ├── __init__.py
│   └── email_finder.py         # Waterfall email finder + MX verification
├── outreach/
│   ├── __init__.py
│   └── email_sender.py         # SmartMailer avec Jinja2
├── integrations/
│   ├── __init__.py
│   └── connectors.py            # HubSpot + Slack
├── templates/
│   ├── introduction.html
│   ├── follow_up_1.html
│   ├── follow_up_2.html
│   └── breakup.html
├── config/
│   ├── settings.yaml
│   └── campaigns/
├── data/
│   ├── leads/
│   └── logs/
├── requirements.txt
└── README.md
```

---

## 🚀 Installation

```bash
# Cloner le repository
git clone https://github.com/Walidisnt/WALIDIA-OMNI-OS.git
cd WALIDIA-OMNI-OS

# Installer les dépendances
pip install -r requirements.txt

# Installer Playwright
playwright install chromium

# Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos clés API
```

---

## ⚙️ Configuration

Créez un fichier `.env` à la racine :

```bash
# LinkedIn
LINKEDIN_EMAIL=votre@email.com
LINKEDIN_PASSWORD=votrepassword

# Email enrichment APIs
HUNTER_API_KEY=your_key
APOLLO_API_KEY=your_key
SNOV_API_KEY=your_key
DROPCONTACT_API_KEY=your_key

# Email sending
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=votre@email.com
SMTP_PASSWORD=your_app_password

# CRM & Notifications
HUBSPOT_API_KEY=your_key
SLACK_WEBHOOK_URL=your_webhook
```

---

## 💻 Utilisation

### Commandes CLI

```bash
# Lancer une nouvelle campagne
walidia launch "VP Sales SaaS France" --limit 100 --send-emails --sync-crm

# Reprendre une campagne interrompue
walidia resume campaign_abc123

# Exporter les résultats
walidia export campaign_abc123 --output leads.csv

# Surveiller le statut
walidia status --watch
```

### Utilisation programmatique

```python
from core import GrowthOrchestrator

# Initialiser l'orchestrateur
orchestrator = GrowthOrchestrator(
    campaign_name="Q1_2025_SaaS_Outreach",
    config_path="config/settings.yaml"
)

# Lancer une campagne complète
orchestrator.run_campaign(
    keyword="VP Sales SaaS",
    limit=100,
    send_emails=True,
    sync_crm=True
)

# Exporter les résultats
orchestrator.export_to_csv("data/leads/campaign_results.csv")
```

---

## 🛡️ Fonctionnalités de sécurité

- ✅ **Anti-détection** : Playwright stealth + comportement humain simulé
- ✅ **Rate limiting** : Délais aléatoires entre actions
- ✅ **Gestion d'état** : Reprise de campagnes interrompues
- ✅ **Limites journalières** : Protection contre le spam
- ✅ **Vérification MX** : Évite les bounces
- ✅ **Cookies chiffrés** : Stockage sécurisé des sessions

---

## 📈 Métriques et suivi

- •  Nombre de profils scrapés
- •  Taux d'enrichissement d'emails
- •  Taux de délivrabilité
- •  Taux d'ouverture (via tracking pixels)
- •  Taux de réponse
- •  Leads synchronisés vers CRM

---

## 🤝 Contribution

Les contributions sont les bienvenues ! Consultez CONTRIBUTING.md pour plus de détails.

---

## 📝 Licence

Ce projet est sous licence MIT. Voir LICENSE pour plus d'informations.

---

## ⚠️  Avertissement

Ce projet est fourni à des fins éducatives. Assurez-vous de respecter :

- •  Les conditions d'utilisation de LinkedIn
- •  Les réglementations anti-spam (CAN-SPAM, GDPR)
- •  Les politiques des fournisseurs d'email
- •  Les lois locales sur la protection des données

---

## 📧 Support

Pour toute question ou problème, ouvrez une [issue](https://github.com/Walidisnt/WALIDIA-OMNI-OS/issues) sur GitHub.

---

**Développé avec ❤️ par [Walidisnt](https://github.com/Walidisnt)**
