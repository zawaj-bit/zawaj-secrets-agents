"""Outils de génération de contenu transversaux."""

from __future__ import annotations
from typing import Any

from zawaj.utils.logger import get_logger

logger = get_logger(__name__)


def generate_campaign_calendar(
    theme: str,
    start_date: str,
    end_date: str,
    platforms: list[str],
) -> dict[str, Any]:
    """Génère un calendrier de publication pour une campagne."""
    return {
        "theme": theme,
        "period": f"{start_date} → {end_date}",
        "platforms": platforms,
        "schedule": [
            {
                "date": start_date,
                "platform": "Instagram",
                "content_type": "Teaser post",
                "status": "à créer",
            },
            {
                "date": start_date,
                "platform": "Klaviyo",
                "content_type": "Email annonce",
                "status": "à créer",
            },
        ],
        "message": "Calendrier généré — personnaliser selon le planning de la marque",
    }


def analyze_content_performance(metrics: dict[str, Any]) -> dict[str, Any]:
    """Analyse les performances de contenu et donne des recommandations."""
    engagement_rate = metrics.get("engagement_rate", 0)
    reach = metrics.get("reach", 0)

    recommendations = []
    if engagement_rate < 2.0:
        recommendations.append("Augmenter l'interaction : poser des questions dans les légendes")
    if engagement_rate > 5.0:
        recommendations.append("Excellent engagement — amplifier avec des stories et des reels")

    return {
        "summary": f"Taux d'engagement : {engagement_rate}% | Portée : {reach:,}",
        "performance": "élevée" if engagement_rate > 4 else "moyenne" if engagement_rate > 2 else "faible",
        "recommendations": recommendations,
    }


CONTENT_TOOL_DEFINITIONS = [
    {
        "name": "generate_campaign_calendar",
        "description": "Génère un calendrier de contenu pour une campagne multi-canal.",
        "input_schema": {
            "type": "object",
            "properties": {
                "theme": {"type": "string", "description": "Thème de la campagne"},
                "start_date": {"type": "string", "description": "Date de début (YYYY-MM-DD)"},
                "end_date": {"type": "string", "description": "Date de fin (YYYY-MM-DD)"},
                "platforms": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Plateformes incluses (instagram, klaviyo, canva)",
                },
            },
            "required": ["theme", "start_date", "end_date"],
        },
    },
]


def execute_content_tool(tool_name: str, tool_input: dict) -> dict[str, Any]:
    """Exécute un outil de contenu."""
    if tool_name == "generate_campaign_calendar":
        return generate_campaign_calendar(
            theme=tool_input.get("theme", ""),
            start_date=tool_input.get("start_date", ""),
            end_date=tool_input.get("end_date", ""),
            platforms=tool_input.get("platforms", ["instagram", "klaviyo"]),
        )
    return {"error": f"Outil inconnu : {tool_name}"}
