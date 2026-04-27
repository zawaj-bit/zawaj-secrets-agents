"""Agent Canva — création de visuels et designs."""

import json
import anthropic

from zawaj.config import get_settings
from zawaj.prompts.brand_voice import BRAND_VOICE_SYSTEM_PROMPT
from zawaj.prompts.canva_prompts import CANVA_SYSTEM_PROMPT
from zawaj.tools.canva_tools import (
    CANVA_TOOL_DEFINITIONS,
    execute_canva_tool,
)
from zawaj.utils.logger import get_logger

logger = get_logger(__name__)


class CanvaAgent:
    """Agent spécialisé Canva — designs, templates, exports."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = anthropic.Anthropic(api_key=self.settings.anthropic_api_key)

    async def run(self, task: str, visual_format: str = "post_instagram") -> str:
        """Exécute une tâche Canva."""
        logger.info("Agent Canva [%s] — tâche : %s", visual_format, task[:100])

        full_task = f"Format cible : {visual_format}\n\n{task}"

        system = [
            {
                "type": "text",
                "text": BRAND_VOICE_SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral", "ttl": "1h"},
            },
            {
                "type": "text",
                "text": CANVA_SYSTEM_PROMPT,
            },
        ]

        messages: list[dict] = [{"role": "user", "content": full_task}]

        while True:
            response = self.client.messages.create(
                model=self.settings.agent_model,
                max_tokens=4096,
                system=system,
                tools=CANVA_TOOL_DEFINITIONS,
                messages=messages,
            )

            messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason == "end_turn":
                for block in response.content:
                    if hasattr(block, "type") and block.type == "text":
                        return block.text
                return "Design Canva créé."

            if response.stop_reason != "tool_use":
                break

            tool_results = []
            for block in response.content:
                if not (hasattr(block, "type") and block.type == "tool_use"):
                    continue
                result = execute_canva_tool(block.name, block.input, self.settings)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result, ensure_ascii=False),
                })

            messages.append({"role": "user", "content": tool_results})

        return "Tâche Canva terminée."
