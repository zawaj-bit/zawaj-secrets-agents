# zawaj-secrets-agents

Système multi-agents Claude pour automatiser le contenu Instagram, les campagnes Klaviyo et les designs Canva de la marque **Zawaj Secret's** (articles de mariage et de luxe).

---

## Ce que font les agents

| Agent | Rôle |
|---|---|
| **Orchestrateur** | Reçoit ta demande, décide quel(s) agent(s) appeler |
| **Instagram Agent** | Rédige et publie posts, stories, reels + hashtags |
| **Klaviyo Agent** | Crée campagnes email/SMS, newsletters, flows automatisés |
| **Canva Agent** | Génère visuels, templates et designs aux bons formats |

---

## Installation (à faire une seule fois)

### 1. Cloner le repo
```bash
git clone https://github.com/zawaj-bit/zawaj-secrets-agents.git
cd zawaj-secrets-agents
```

### 2. Installer les dépendances
```bash
pip install -e ".[dev]"
```

### 3. Créer ton fichier `.env`
Copie `.env.example` en `.env` et remplis tes clés :
```bash
cp .env.example .env
```

Contenu du `.env` :
```
ANTHROPIC_API_KEY=sk-ant-...
INSTAGRAM_ACCESS_TOKEN=...
INSTAGRAM_ACCOUNT_ID=...
KLAVIYO_API_KEY=...
KLAVIYO_LIST_ID=...
CANVA_ACCESS_TOKEN=...
CANVA_BRAND_KIT_ID=...
```

---

## Utilisation

### Mode interactif
```bash
python -m zawaj.main
```

### Mode automatique (scheduler + interactif)
```bash
python -m zawaj.main --auto
```
Publie automatiquement : post Instagram 9h, story 19h, newsletter Klaviyo le lundi.

### Mode serveur (scheduler seul)
```bash
python -m zawaj.main --scheduler
```

### Tâche unique
```bash
python -m zawaj.main "Crée un post Instagram pour l'Aïd El-Fitr"
```

---

## Déploiement Railway

1. [railway.app](https://railway.app) → New Project → Deploy from GitHub
2. Ajoute les variables d'environnement
3. Start Command : `python -m zawaj.main --scheduler`

---

## Clés API à obtenir

- **Anthropic** : [console.anthropic.com](https://console.anthropic.com)
- **Instagram** : [developers.facebook.com](https://developers.facebook.com) → app Meta → Instagram Graph API
- **Klaviyo** : Account → Settings → API Keys
- **Canva** : [canva.dev](https://www.canva.dev) (accès Enterprise requis)

---

## Tests
```bash
pytest tests/ -v
```
