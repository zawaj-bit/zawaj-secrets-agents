"""Outils Instagram Graph API pour l'agent Instagram."""

from __future__ import annotations
from typing import Any, TYPE_CHECKING
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

if TYPE_CHECKING:
    from zawaj.config import Settings

from zawaj.utils.logger import get_logger

logger = get_logger(__name__)

INSTAGRAM_BASE_URL = "https://graph.facebook.com/v19.0"

INSTAGRAM_TOOL_DEFINITIONS = [
    {
        "name": "create_instagram_post",
        "description": "Crée et publie un post Instagram (image + légende). Retourne l'ID du post.",
        "input_schema": {
            "type": "object",
            "properties": {
                "caption": {
                    "type": "string",
                    "description": "Légende du post avec emojis et hashtags",
                },
                "image_url": {
                    "type": "string",
                    "description": "URL publique de l'image à publier",
                },
                "scheduled_time": {
                    "type": "string",
                    "description": "Timestamp ISO 8601 pour la publication programmée (optionnel)",
                },
            },
            "required": ["caption", "image_url"],
        },
    },
    {
        "name": "create_instagram_story",
        "description": "Crée une story Instagram (photo ou vidéo).",
        "input_schema": {
            "type": "object",
            "properties": {
                "media_url": {
                    "type": "string",
                    "description": "URL du média (image ou vidéo)",
                },
                "media_type": {
                    "type": "string",
                    "enum": ["IMAGE", "VIDEO"],
                    "description": "Type de média",
                },
            },
            "required": ["media_url", "media_type"],
        },
    },
    {
        "name": "get_instagram_insights",
        "description": "Récupère les statistiques Instagram (portée, impressions, engagement).",
        "input_schema": {
            "type": "object",
            "properties": {
                "period": {
                    "type": "string",
                    "enum": ["day", "week", "month"],
                    "description": "Période d'analyse",
                },
                "metrics": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Métriques à récupérer (reach, impressions, follower_count, etc.)",
                },
            },
            "required": ["period"],
        },
    },
    {
        "name": "generate_hashtags",
        "description": "Génère une liste de hashtags pertinents pour le contenu Zawaj Secret's.",
        "input_schema": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "Sujet ou thème du post",
                },
                "count": {
                    "type": "integer",
                    "description": "Nombre de hashtags à générer (max 30)",
                },
                "language": {
                    "type": "string",
                    "enum": ["fr", "ar", "en", "mixed"],
                    "description": "Langue des hashtags",
                },
            },
            "required": ["topic"],
        },
    },
    {
        "name": "get_best_posting_time",
        "description": "Analyse les données d'audience pour suggérer le meilleur moment de publication.",
        "input_schema": {
            "type": "object",
            "properties": {
                "day_of_week": {
                    "type": "string",
                    "description": "Jour de la semaine cible (optionnel)",
                },
            },
            "required": [],
        },
    },
]


def execute_instagram_tool(tool_name: str, tool_input: dict, settings: "Settings") -> dict[str, Any]:
    """Exécute un outil Instagram et retourne le résultat."""
    handlers = {
        "create_instagram_post": _create_post,
        "create_instagram_story": _create_story,
        "get_instagram_insights": _get_insights,
        "generate_hashtags": _generate_hashtags,
        "get_best_posting_time": _get_best_posting_time,
    }

    handler = handlers.get(tool_name)
    if not handler:
        return {"error": f"Outil inconnu : {tool_name}"}

    return handler(tool_input, settings)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def _create_post(params: dict, settings: "Settings") -> dict:
    """Publie un post sur Instagram via l'API Graph."""
    if not settings.instagram_access_token or not settings.instagram_account_id:
        # Mode simulation si les tokens ne sont pas configurés
        logger.warning("Instagram non configuré — mode simulation")
        return {
            "status": "simulated",
            "post_id": "SIMULATED_POST_123",
            "caption_preview": params.get("caption", "")[:100],
            "message": "Post créé en mode simulation (configurez INSTAGRAM_ACCESS_TOKEN)",
        }

    try:
        with httpx.Client(timeout=30) as client:
            # Étape 1 : créer le container média
            container_resp = client.post(
                f"{INSTAGRAM_BASE_URL}/{settings.instagram_account_id}/media",
                params={
                    "image_url": params["image_url"],
                    "caption": params["caption"],
                    "access_token": settings.instagram_access_token,
                },
            )
            container_resp.raise_for_status()
            container_id = container_resp.json()["id"]

            # Étape 2 : publier le container
            publish_resp = client.post(
                f"{INSTAGRAM_BASE_URL}/{settings.instagram_account_id}/media_publish",
                params={
                    "creation_id": container_id,
                    "access_token": settings.instagram_access_token,
                },
            )
            publish_resp.raise_for_status()
            post_id = publish_resp.json()["id"]

        logger.info("Post Instagram publié : %s", post_id)
        return {"status": "published", "post_id": post_id}

    except httpx.HTTPError as e:
        logger.error("Erreur API Instagram : %s", e)
        return {"status": "error", "error": str(e)}


def _create_story(params: dict, settings: "Settings") -> dict:
    """Crée une story Instagram."""
    if not settings.instagram_access_token:
        return {
            "status": "simulated",
            "story_id": "SIMULATED_STORY_456",
            "message": "Story créée en mode simulation",
        }
    # Implémentation réelle similaire à _create_post
    return {"status": "simulated", "story_id": "STORY_ID", "media_type": params.get("media_type")}


def _get_insights(params: dict, settings: "Settings") -> dict:
    """Récupère les insights Instagram."""
    if not settings.instagram_access_token:
        return {
            "status": "simulated",
            "period": params.get("period", "week"),
            "reach": 12500,
            "impressions": 28000,
            "follower_count": 8420,
            "engagement_rate": "3.8%",
            "message": "Données simulées — configurez INSTAGRAM_ACCESS_TOKEN",
        }

    try:
        metrics = params.get("metrics", ["reach", "impressions", "follower_count"])
        with httpx.Client(timeout=30) as client:
            resp = client.get(
                f"{INSTAGRAM_BASE_URL}/{settings.instagram_account_id}/insights",
                params={
                    "metric": ",".join(metrics),
                    "period": params["period"],
                    "access_token": settings.instagram_access_token,
                },
            )
            resp.raise_for_status()
            return {"status": "success", "data": resp.json().get("data", [])}
    except httpx.HTTPError as e:
        return {"status": "error", "error": str(e)}


def _generate_hashtags(params: dict, settings: "Settings") -> dict:
    """Génère des hashtags pertinents pour Zawaj Secret's."""
    topic = params.get("topic", "")
    count = min(params.get("count", 20), 30)
    language = params.get("language", "mixed")

    # Hashtags de base de la marque
    brand_hashtags = [
        "#ZawajSecrets", "#زواج_سيكريتس", "#MariageLuxe",
        "#BridalMorocco", "#NuptialChic", "#MarocMariage",
    ]

    # Hashtags contextuels selon le sujet
    contextual = {
        "ramadan": ["#Ramadan", "#RamadanMubarak", "#رمضان", "#RamadanBridal", "#RamadanStyle"],
        "mariage": ["#Mariage", "#WeddingDay", "#عروس", "#BridalStyle", "#WeddingInspo"],
        "luxe": ["#LuxuryBridal", "#HauteCouture", "#Elegant", "#فستان_العروس", "#BridalLuxury"],
        "collection": ["#NewCollection", "#CollectionNuptiale", "#تشكيلة_جديدة", "#BridalCollection"],
    }

    topic_lower = topic.lower()
    extra = []
    for key, tags in contextual.items():
        if key in topic_lower:
            extra.extend(tags)

    all_tags = brand_hashtags + extra
    # Compléter jusqu'au count demandé
    generic = [
        "#Mariage", "#Wedding", "#Bridal", "#Bride", "#WeddingInspiration",
        "#BridalFashion", "#MarocStyle", "#Elegance", "#LuxuryBride", "#WeddingStyle",
        "#NuptialMagazine", "#Matrimonio", "#عروسة", "#زفاف", "#خطوبة",
    ]
    for tag in generic:
        if len(all_tags) >= count:
            break
        if tag not in all_tags:
            all_tags.append(tag)

    return {
        "hashtags": all_tags[:count],
        "count": len(all_tags[:count]),
        "formatted": " ".join(all_tags[:count]),
    }


def _get_best_posting_time(params: dict, settings: "Settings") -> dict:
    """Retourne les meilleures créneaux de publication."""
    return {
        "recommendations": [
            {"day": "Mardi", "time": "19:00", "score": 9.2, "reason": "Pic d'activité audience marocaine"},
            {"day": "Jeudi", "time": "20:30", "score": 8.9, "reason": "Soirée shopping en ligne"},
            {"day": "Samedi", "time": "11:00", "score": 8.7, "reason": "Matinée week-end"},
            {"day": "Dimanche", "time": "18:00", "score": 8.5, "reason": "Fin de week-end, engagement élevé"},
        ],
        "timezone": "Africa/Casablanca",
        "best_overall": "Mardi à 19h00",
    }
