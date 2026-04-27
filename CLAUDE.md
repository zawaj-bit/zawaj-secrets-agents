# Zawaj Secret's — Agents IA

## Présentation

Système multi-agents Claude pour automatiser le contenu Instagram, les campagnes Klaviyo et les designs Canva de la marque **Zawaj Secret's** (articles de mariage et de luxe).

## Architecture

```
src/zawaj/
├── agents/          # Agents Claude spécialisés
│   ├── orchestrator.py    # Orchestrateur principal (claude-opus-4-7, adaptive thinking)
│   ├── instagram_agent.py # Génération de posts/stories/reels
│   ├── klaviyo_agent.py   # Campagnes email et SMS
│   └── canva_agent.py     # Création de visuels
├── tools/           # Wrappers API (tool use)
│   ├── instagram_tools.py
│   ├── klaviyo_tools.py
│   ├── canva_tools.py
│   └── content_tools.py
├── prompts/         # System prompts avec cache
│   ├── brand_voice.py     # Voix de marque (cachée)
│   ├── instagram_prompts.py
│   ├── klaviyo_prompts.py
│   └── canva_prompts.py
└── utils/           # Logger, helpers
```

## Modèle

- **Orchestrateur** : `claude-opus-4-7` avec `thinking: {type: "adaptive"}`
- **Agents spécialisés** : `claude-opus-4-7`
- **Prompt caching** : System prompt de marque mis en cache (TTL 1h)

## Commandes fréquentes

```bash
# Installer les dépendances
pip install -e ".[dev]"

# Lancer l'orchestrateur
python -m zawaj.main

# Tests
pytest tests/ -v

# Lint
ruff check src/ tests/
```

## Variables d'environnement

Copier `.env.example` → `.env` et remplir les clés API.

## Flux principal

1. L'orchestrateur reçoit une demande (ex: "Créer une campagne pour le Ramadan")
2. Il décompose en sous-tâches avec adaptive thinking
3. Il délègue à chaque agent spécialisé via tool use
4. Chaque agent appelle les APIs (Instagram/Klaviyo/Canva) via ses outils
5. L'orchestrateur consolide et retourne le rapport

## Brand voice

La marque Zawaj Secret's est positionnée sur le luxe discret, la féminité élégante et l'authenticité marocaine. Ton : chaleureux, raffiné, intime.
