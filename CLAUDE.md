# Zawaj Secret's — Agents IA

## Présentation

Système multi-agents Claude pour automatiser le contenu Instagram, les campagnes Klaviyo et les designs Canva de la marque **Zawaj Secret's** — marque française de bien-être intime féminin fondée par Ourouata.

---

## Architecture

```
src/zawaj/
├── agents/
│   ├── orchestrator.py    # Orchestrateur principal (claude-opus-4-7, adaptive thinking)
│   ├── instagram_agent.py # Génération de posts/stories/reels
│   ├── klaviyo_agent.py   # Campagnes email et SMS
│   └── canva_agent.py     # Création de visuels
├── tools/
│   ├── instagram_tools.py # Instagram Graph API
│   ├── klaviyo_tools.py   # Klaviyo API
│   ├── canva_tools.py     # Canva Connect API
│   └── content_tools.py   # Outils contenu génériques
├── prompts/
│   ├── brand_voice.py     # Voix de marque complète (mis en cache TTL 1h)
│   ├── instagram_prompts.py # Expertise contenu Instagram
│   ├── klaviyo_prompts.py # Expertise email/SMS
│   └── canva_prompts.py   # Expertise design visuel
└── utils/                 # Logger, helpers
```

---

## Modèle

- **Orchestrateur** : claude-opus-4-7 avec thinking: {type: "adaptive"}
- **Agents spécialisés** : claude-opus-4-7
- **Prompt caching** : System prompt de marque mis en cache (TTL 1h) — économies de tokens significatives

---

## Connaissance Marque Zawaj Secret's

### Qui est Zawaj Secret's
Ourouata est la fondatrice. La marque vend des produits naturels de bien-être intime (Brume Intime, Gummies, Douchette, Khamaré, etc.) ciblant les femmes musulmanes et mariées françaises et franco-maghrébines, 25-40 ans.

**Mission** : Briser les tabous autour de l'intimité féminine, avec bienveillance et sans jugement.

### Produits
- Brume Intime 3en1 : 24,90€ (abonnement 22,90€) — bestseller
- Gummies Probiotiques : 27,90€
- Douchette Intime Nomade : 21,90€
- Gel Parfumé Musc Intime : 22,90€
- Parfum Attirance Afrodita : 22,90€
- Douceur Khamaré : 19,90€
- Mousse Nettoyante Intime : 19,90€
- Tablette Love Chocolat : 17,90€

### Ton & voix
Court, percutant, chargé émotionnellement. Sororité, bienveillance, franchise. Jamais neutre. Les agents parlent comme Ourouata — indiscernable.

### Équipe
- Lisa (CM) : vouvoiement, directives structurées
- Nok (UGC) : tutoiement, approche peer-to-peer
- Communauté "les perles" : sororité, sisterhood

### Plateformes
- Instagram (priorité) : 100% Reels, stories interactives, carrousels
- Klaviyo : welcome flow, abandon panier, post-achat, newsletter samedi
- ManyChat : trigger "CYCLE" → flow DM automatique
- Canva : visuels rose/blanc, hex #D4507A, #F2C4CE, #FFF5F5

---

## Commandes fréquentes

```bash
# Installer les dépendances
pip install -e ".[dev]"

# Lancer en mode interactif
python -m zawaj.main

# Mode automatique (scheduler + interactif)
python -m zawaj.main --auto

# Mode serveur (scheduler seul — pour déploiement)
python -m zawaj.main --scheduler

# Tâche unique
python -m zawaj.main "Crée un post Instagram pour l'Aïd"

# Tests
pytest tests/ -v

# Lint
ruff check src/ tests/
```

---

## Tâches automatiques planifiées (SCHEDULED_TASKS dans main.py)

- **9h00 quotidien** → Post Instagram (thème mariage, intimité, collection)
- **19h00 quotidien** → Story Instagram (interactif ou inspirant)
- **Lundi 10h** → Newsletter Klaviyo hebdomadaire (épanouissement féminin + actualité marque)

Pour modifier les horaires ou les tâches, éditer `SCHEDULED_TASKS` dans `src/zawaj/main.py`.

---

## Variables d'environnement requises (.env)

```
ANTHROPIC_API_KEY=          # claude.ai/settings → API Keys
INSTAGRAM_ACCESS_TOKEN=     # Meta Business → Instagram Graph API token
INSTAGRAM_ACCOUNT_ID=       # ID compte Instagram professionnel
KLAVIYO_API_KEY=            # Klaviyo → Account → Settings → API Keys
KLAVIYO_LIST_ID=            # ID de ta liste principale
CANVA_ACCESS_TOKEN=         # Canva Connect API (Enterprise)
CANVA_BRAND_KIT_ID=         # ID Brand Kit Canva
```
