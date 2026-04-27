"""Outils Klaviyo API pour l'agent email/SMS."""

from __future__ import annotations
from typing import Any, TYPE_CHECKING
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

if TYPE_CHECKING:
    from zawaj.config import Settings

from zawaj.utils.logger import get_logger

logger = get_logger(__name__)

KLAVIYO_BASE_URL = "https://a.klaviyo.com/api"

KLAVIYO_TOOL_DEFINITIONS = [
    {
        "name": "create_email_campaign",
        "description": "Crée une campagne email dans Klaviyo avec un objet et un contenu HTML.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Nom interne de la campagne",
                },
                "subject": {
                    "type": "string",
                    "description": "Objet de l'email (accrocheur, avec emojis si pertinent)",
                },
                "preview_text": {
                    "type": "string",
                    "description": "Texte de prévisualisation (aperçu dans la boîte de réception)",
                },
                "html_content": {
                    "type": "string",
                    "description": "Contenu HTML de l'email",
                },
                "list_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "IDs des listes/segments Klaviyo ciblés",
                },
                "scheduled_at": {
                    "type": "string",
                    "description": "Date/heure d'envoi ISO 8601 (optionnel — immédiat si absent)",
                },
            },
            "required": ["name", "subject", "html_content"],
        },
    },
    {
        "name": "create_sms_campaign",
        "description": "Crée une campagne SMS dans Klaviyo.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Nom de la campagne"},
                "message": {
                    "type": "string",
                    "description": "Texte du SMS (max 160 caractères recommandé)",
                },
                "list_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Listes/segments ciblés",
                },
            },
            "required": ["name", "message"],
        },
    },
    {
        "name": "get_list_profiles",
        "description": "Récupère les informations sur une liste Klaviyo (nombre d'abonnés, etc.).",
        "input_schema": {
            "type": "object",
            "properties": {
                "list_id": {
                    "type": "string",
                    "description": "ID de la liste Klaviyo",
                },
            },
            "required": ["list_id"],
        },
    },
    {
        "name": "create_segment",
        "description": "Crée un segment dynamique dans Klaviyo basé sur des conditions.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Nom du segment"},
                "conditions": {
                    "type": "object",
                    "description": "Conditions de segmentation (ex: a acheté, a ouvert un email, etc.)",
                },
            },
            "required": ["name", "conditions"],
        },
    },
    {
        "name": "get_campaign_metrics",
        "description": "Récupère les métriques d'une campagne (taux d'ouverture, clics, conversions).",
        "input_schema": {
            "type": "object",
            "properties": {
                "campaign_id": {
                    "type": "string",
                    "description": "ID de la campagne Klaviyo",
                },
            },
            "required": ["campaign_id"],
        },
    },
    {
        "name": "generate_email_content",
        "description": "Génère le contenu HTML d'un email selon le brief et le template de marque.",
        "input_schema": {
            "type": "object",
            "properties": {
                "brief": {
                    "type": "string",
                    "description": "Brief de l'email (produit, promotion, événement, etc.)",
                },
                "email_type": {
                    "type": "string",
                    "enum": ["promotional", "newsletter", "welcome", "abandoned_cart", "post_purchase"],
                    "description": "Type d'email",
                },
                "cta_text": {
                    "type": "string",
                    "description": "Texte du bouton d'appel à l'action",
                },
                "cta_url": {
                    "type": "string",
                    "description": "URL du bouton d'appel à l'action",
                },
            },
            "required": ["brief", "email_type"],
        },
    },
]


def execute_klaviyo_tool(tool_name: str, tool_input: dict, settings: "Settings") -> dict[str, Any]:
    """Exécute un outil Klaviyo et retourne le résultat."""
    handlers = {
        "create_email_campaign": _create_email_campaign,
        "create_sms_campaign": _create_sms_campaign,
        "get_list_profiles": _get_list_profiles,
        "create_segment": _create_segment,
        "get_campaign_metrics": _get_campaign_metrics,
        "generate_email_content": _generate_email_content,
    }

    handler = handlers.get(tool_name)
    if not handler:
        return {"error": f"Outil inconnu : {tool_name}"}

    return handler(tool_input, settings)


def _klaviyo_headers(api_key: str) -> dict:
    return {
        "Authorization": f"Klaviyo-API-Key {api_key}",
        "revision": "2024-02-15",
        "Content-Type": "application/json",
    }


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def _create_email_campaign(params: dict, settings: "Settings") -> dict:
    """Crée une campagne email Klaviyo."""
    if not settings.klaviyo_api_key:
        return {
            "status": "simulated",
            "campaign_id": "SIMULATED_CAMPAIGN_789",
            "name": params.get("name"),
            "subject": params.get("subject"),
            "message": "Campagne créée en mode simulation (configurez KLAVIYO_API_KEY)",
        }

    list_ids = params.get("list_ids", [settings.klaviyo_list_id]) if settings.klaviyo_list_id else []

    payload = {
        "data": {
            "type": "campaign",
            "attributes": {
                "name": params["name"],
                "audiences": {
                    "included": [{"type": "list", "id": lid} for lid in list_ids],
                },
                "send_strategy": {
                    "method": "immediate" if not params.get("scheduled_at") else "static",
                    "datetime": params.get("scheduled_at"),
                },
                "campaign-messages": {
                    "data": [{
                        "type": "campaign-message",
                        "attributes": {
                            "channel": "email",
                            "label": params["name"],
                            "content": {
                                "subject": params["subject"],
                                "preview_text": params.get("preview_text", ""),
                                "from_email": "contact@zawajsecrets.com",
                                "from_label": "Zawaj Secret's",
                                "reply_to_email": "contact@zawajsecrets.com",
                                "html_body": params.get("html_content", ""),
                            },
                        },
                    }],
                },
            },
        }
    }

    try:
        with httpx.Client(timeout=30) as client:
            resp = client.post(
                f"{KLAVIYO_BASE_URL}/campaigns/",
                headers=_klaviyo_headers(settings.klaviyo_api_key),
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json().get("data", {})
            campaign_id = data.get("id", "")
            logger.info("Campagne Klaviyo créée : %s", campaign_id)
            return {"status": "created", "campaign_id": campaign_id, "name": params["name"]}
    except httpx.HTTPError as e:
        logger.error("Erreur API Klaviyo : %s", e)
        return {"status": "error", "error": str(e)}


def _create_sms_campaign(params: dict, settings: "Settings") -> dict:
    """Crée une campagne SMS Klaviyo."""
    if not settings.klaviyo_api_key:
        return {
            "status": "simulated",
            "campaign_id": "SIMULATED_SMS_321",
            "message_preview": params.get("message", "")[:60],
        }
    return {"status": "simulated", "message": "SMS campaign — implémentation à compléter avec token"}


def _get_list_profiles(params: dict, settings: "Settings") -> dict:
    """Récupère les infos d'une liste Klaviyo."""
    if not settings.klaviyo_api_key:
        return {
            "status": "simulated",
            "list_id": params.get("list_id"),
            "profile_count": 3842,
            "name": "Zawaj Secrets — Abonnés principaux",
        }

    try:
        with httpx.Client(timeout=30) as client:
            resp = client.get(
                f"{KLAVIYO_BASE_URL}/lists/{params['list_id']}/",
                headers=_klaviyo_headers(settings.klaviyo_api_key),
            )
            resp.raise_for_status()
            return {"status": "success", "data": resp.json().get("data", {})}
    except httpx.HTTPError as e:
        return {"status": "error", "error": str(e)}


def _create_segment(params: dict, settings: "Settings") -> dict:
    """Crée un segment Klaviyo."""
    if not settings.klaviyo_api_key:
        return {
            "status": "simulated",
            "segment_id": "SEG_SIMULATED",
            "name": params.get("name"),
        }
    return {"status": "simulated", "segment_id": "SEG_NEW", "name": params.get("name")}


def _get_campaign_metrics(params: dict, settings: "Settings") -> dict:
    """Récupère les métriques d'une campagne."""
    return {
        "status": "simulated",
        "campaign_id": params.get("campaign_id"),
        "open_rate": "38.2%",
        "click_rate": "12.7%",
        "conversion_rate": "4.1%",
        "revenue": "2840 MAD",
        "unsubscribe_rate": "0.3%",
    }


def _generate_email_content(params: dict, settings: "Settings") -> dict:
    """Génère le contenu HTML d'un email selon le brief."""
    brief = params.get("brief", "")
    email_type = params.get("email_type", "promotional")
    cta_text = params.get("cta_text", "Découvrir la collection")
    cta_url = params.get("cta_url", "https://zawajsecrets.com/collections")

    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Zawaj Secret's</title>
  <style>
    body {{ font-family: Georgia, serif; background: #faf8f5; margin: 0; padding: 0; }}
    .container {{ max-width: 600px; margin: 0 auto; background: #ffffff; }}
    .header {{ background: #1a1a2e; padding: 40px 30px; text-align: center; }}
    .header h1 {{ color: #d4af7a; font-size: 28px; margin: 0; letter-spacing: 3px; }}
    .header p {{ color: #c8b8a2; font-size: 13px; margin: 8px 0 0; letter-spacing: 1px; }}
    .body {{ padding: 40px 30px; color: #333; line-height: 1.8; }}
    .cta {{ text-align: center; margin: 30px 0; }}
    .cta a {{
      background: #1a1a2e; color: #d4af7a; padding: 14px 40px;
      text-decoration: none; font-size: 14px; letter-spacing: 2px;
      text-transform: uppercase; border: 1px solid #d4af7a;
    }}
    .footer {{ background: #f5f0eb; padding: 20px 30px; text-align: center; font-size: 11px; color: #888; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>ZAWAJ SECRET'S</h1>
      <p>L'élégance du mariage revisitée</p>
    </div>
    <div class="body">
      <p>Chère cliente,</p>
      <p>{brief}</p>
      <div class="cta">
        <a href="{cta_url}">{cta_text}</a>
      </div>
      <p>Avec toute notre élégance,<br>
      <em>L'équipe Zawaj Secret's</em></p>
    </div>
    <div class="footer">
      <p>Zawaj Secret's · Casablanca, Maroc</p>
      <p>© 2025 Zawaj Secret's. Tous droits réservés.</p>
      <p><a href="{{{{ unsubscribe_url }}}}" style="color:#888">Se désabonner</a></p>
    </div>
  </div>
</body>
</html>"""

    return {
        "status": "generated",
        "email_type": email_type,
        "html_content": html,
        "subject_suggestion": f"✨ {brief[:50]}...",
        "preview_text_suggestion": "Découvrez notre nouvelle collection exclusive",
    }
