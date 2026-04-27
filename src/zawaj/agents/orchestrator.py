"""Orchestrateur principal — décompose les demandes et délègue aux agents spécialisés."""

import json
import anthropic

from zawaj.config import get_settings
from zawaj.prompts.brand_voice import BRAND_VOICE_SYSTEM_PROMPT
from zawaj.utils.logger import get_logger

logger = get_logger(__name__)


# Définition des outils de délégation vers les agents spécialisés
ORCHESTRATOR_TOOLS = [
    {
        "name": "run_instagram_agent",
        "description": (
            "Délègue une tâche à l'agent Instagram. Utiliser pour : "
            "créer des posts/stories/reels, rédiger des légendes, "
            "planifier du contenu Instagram, gérer les hashtags."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "Description précise de la tâche Instagram à accomplir",
                },
                "context": {
                    "type": "string",
                    "description": "Contexte additionnel (collection, événement, cible, etc.)",
                },
            },
            "required": ["task"],
        },
    },
    {
        "name": "run_klaviyo_agent",
        "description": (
            "Délègue une tâche à l'agent Klaviyo. Utiliser pour : "
            "créer des campagnes email/SMS, rédiger des newsletters, "
            "configurer des flows automatisés, segmenter les audiences."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "Description précise de la tâche Klaviyo à accomplir",
                },
                "context": {
                    "type": "string",
                    "description": "Contexte (produit, segment, objectif de la campagne, etc.)",
                },
            },
            "required": ["task"],
        },
    },
    {
        "name": "run_canva_agent",
        "description": (
            "Délègue une tâche à l'agent Canva. Utiliser pour : "
            "créer des visuels, générer des templates, "
            "adapter des designs aux formats Instagram, email ou pub."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "Description précise du visuel ou design à créer",
                },
                "format": {
                    "type": "string",
                    "enum": ["post_instagram", "story_instagram", "email_header", "banniere", "autre"],
                    "description": "Format cible du visuel",
                },
                "context": {
                    "type": "string",
                    "description": "Contexte visuel (couleurs, mood, référence, etc.)",
                },
            },
            "required": ["task", "format"],
        },
    },
]


class OrchestratorAgent:
    """Agent orchestrateur — coordonne Instagram, Klaviyo et Canva."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = anthropic.Anthropic(api_key=self.settings.anthropic_api_key)

        # Import différé pour éviter les imports circulaires
        from zawaj.agents.instagram_agent import InstagramAgent
        from zawaj.agents.klaviyo_agent import KlaviyoAgent
        from zawaj.agents.canva_agent import CanvaAgent

        self._instagram = InstagramAgent()
        self._klaviyo = KlaviyoAgent()
        self._canva = CanvaAgent()

    async def run(self, user_request: str) -> str:
        """Traite une demande utilisateur et orchestre les agents."""
        logger.info("Orchestrateur — nouvelle demande : %s", user_request[:100])

        messages: list[dict] = [
            {"role": "user", "content": user_request}
        ]

        # Prompt caching sur le system prompt de marque (TTL 1h)
        system = [
            {
                "type": "text",
                "text": BRAND_VOICE_SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral", "ttl": "1h"},
            }
        ]

        while True:
            response = self.client.messages.create(
                model=self.settings.orchestrator_model,
                max_tokens=8192,
                thinking={"type": "adaptive"},
                system=system,
                tools=ORCHESTRATOR_TOOLS,
                messages=messages,
            )

            logger.debug("Stop reason : %s", response.stop_reason)

            # Ajouter la réponse de l'assistant à l'historique
            messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason == "end_turn":
                # Extraire le texte final
                for block in response.content:
                    if hasattr(block, "type") and block.type == "text":
                        return block.text
                return "Tâche accomplie."

            if response.stop_reason != "tool_use":
                break

            # Exécuter les appels d'outils
            tool_results = []
            for block in response.content:
                if not (hasattr(block, "type") and block.type == "tool_use"):
                    continue

                result = await self._dispatch_tool(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                })

            messages.append({"role": "user", "content": tool_results})

        return "Orchestration terminée."

    async def _dispatch_tool(self, tool_name: str, tool_input: dict) -> str:
        """Dispatche l'appel d'outil vers l'agent approprié."""
        task = tool_input.get("task", "")
        context = tool_input.get("context", "")
        full_task = f"{task}\n\nContexte : {context}" if context else task

        try:
            if tool_name == "run_instagram_agent":
                logger.info("→ Agent Instagram : %s", task[:80])
                return await self._instagram.run(full_task)

            elif tool_name == "run_klaviyo_agent":
                logger.info("→ Agent Klaviyo : %s", task[:80])
                return await self._klaviyo.run(full_task)

            elif tool_name == "run_canva_agent":
                fmt = tool_input.get("format", "autre")
                logger.info("→ Agent Canva [%s] : %s", fmt, task[:80])
                return await self._canva.run(full_task, visual_format=fmt)

            else:
                return json.dumps({"error": f"Outil inconnu : {tool_name}"})

        except Exception as e:
            logger.error("Erreur dans %s : %s", tool_name, e, exc_info=True)
            return json.dumps({"error": str(e)})
