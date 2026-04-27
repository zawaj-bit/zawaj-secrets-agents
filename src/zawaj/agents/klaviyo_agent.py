"""Agent Klaviyo — campagnes email et SMS."""

import json
import anthropic

from zawaj.config import get_settings
from zawaj.prompts.brand_voice import BRAND_VOICE_SYSTEM_PROMPT
from zawaj.prompts.klaviyo_prompts import KLAVIYO_SYSTEM_PROMPT
from zawaj.tools.klaviyo_tools import (
    KLAVIYO_TOOL_DEFINITIONS,
    execute_klaviyo_tool,
)
from zawaj.utils.logger import get_logger

logger = get_logger(__name__)


class KlaviyoAgent:
    """Agent spécialisé Klaviyo — emails, SMS, segmentation, flows."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = anthropic.Anthropic(api_key=self.settings.anthropic_api_key)

    async def run(self, task: str) -> str:
        """Exécute une tâche Klaviyo."""
        logger.info("Agent Klaviyo — tâche : %s", task[:100])

        system = [
            {
                "type": "text",
                "text": BRAND_VOICE_SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral", "ttl": "1h"},
            },
            {
                "type": "text",
                "text": KLAVIYO_SYSTEM_PROMPT,
            },
        ]

        messages: list[dict] = [{"role": "user", "content": task}]

        while True:
            response = self.client.messages.create(
                model=self.settings.agent_model,
                max_tokens=6144,
                system=system,
                tools=KLAVIYO_TOOL_DEFINITIONS,
                messages=messages,
            )

            messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason == "end_turn":
                for block in response.content:
                    if hasattr(block, "type") and block.type == "text":
                        return block.text
                return "Campagne Klaviyo créée."

            if response.stop_reason != "tool_use":
                break

            tool_results = []
            for block in response.content:
                if not (hasattr(block, "type") and block.type == "tool_use"):
                    continue
                result = execute_klaviyo_tool(block.name, block.input, self.settings)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result, ensure_ascii=False),
                })

            messages.append({"role": "user", "content": tool_results})

        return "Tâche Klaviyo terminée."
