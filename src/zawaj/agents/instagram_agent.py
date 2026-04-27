"""Agent Instagram — création et publication de contenu."""

import json
import anthropic

from zawaj.config import get_settings
from zawaj.prompts.brand_voice import BRAND_VOICE_SYSTEM_PROMPT
from zawaj.prompts.instagram_prompts import INSTAGRAM_SYSTEM_PROMPT
from zawaj.tools.instagram_tools import (
    INSTAGRAM_TOOL_DEFINITIONS,
    execute_instagram_tool,
)
from zawaj.utils.logger import get_logger

logger = get_logger(__name__)


class InstagramAgent:
    """Agent spécialisé Instagram — posts, stories, reels, hashtags."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = anthropic.Anthropic(api_key=self.settings.anthropic_api_key)

    async def run(self, task: str) -> str:
        """Exécute une tâche Instagram."""
        logger.info("Agent Instagram — tâche : %s", task[:100])

        system = [
            {
                "type": "text",
                "text": BRAND_VOICE_SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral", "ttl": "1h"},
            },
            {
                "type": "text",
                "text": INSTAGRAM_SYSTEM_PROMPT,
            },
        ]

        messages: list[dict] = [{"role": "user", "content": task}]

        while True:
            response = self.client.messages.create(
                model=self.settings.agent_model,
                max_tokens=4096,
                system=system,
                tools=INSTAGRAM_TOOL_DEFINITIONS,
                messages=messages,
            )

            messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason == "end_turn":
                for block in response.content:
                    if hasattr(block, "type") and block.type == "text":
                        return block.text
                return "Contenu Instagram créé."

            if response.stop_reason != "tool_use":
                break

            tool_results = []
            for block in response.content:
                if not (hasattr(block, "type") and block.type == "tool_use"):
                    continue
                result = execute_instagram_tool(block.name, block.input, self.settings)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result, ensure_ascii=False),
                })

            messages.append({"role": "user", "content": tool_results})

        return "Tâche Instagram terminée."
