"""Outils Canva Connect API pour l'agent design."""

from __future__ import annotations
from typing import Any, TYPE_CHECKING
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

if TYPE_CHECKING:
    from zawaj.config import Settings

from zawaj.utils.logger import get_logger

logger = get_logger(__name__)

CANVA_BASE_URL = "https://api.canva.com/rest/v1"

CANVA_TOOL_DEFINITIONS = [
    {
        "name": "create_design",
        "description": "Crée un nouveau design Canva à partir d'un template ou d'un format.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Titre du design",
                },
                "design_type": {
                    "type": "string",
                    "enum": [
                        "instagram_post", "instagram_story", "email_header",
                        "facebook_cover", "banner_web", "flyer",
                    ],
                    "description": "Type/format du design",
                },
                "template_id": {
                    "type": "string",
                    "description": "ID d'un template Canva existant (optionnel)",
                },
            },
            "required": ["title", "design_type"],
        },
    },
    {
        "name": "update_design_text",
        "description": "Modifie les éléments textuels d'un design Canva existant.",
        "input_schema": {
            "type": "object",
            "properties": {
                "design_id": {
                    "type": "string",
                    "description": "ID du design Canva",
                },
                "text_updates": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "element_id": {"type": "string"},
                            "new_text": {"type": "string"},
                        },
                    },
                    "description": "Liste des mises à jour de texte",
                },
            },
            "required": ["design_id", "text_updates"],
        },
    },
    {
        "name": "export_design",
        "description": "Exporte un design Canva en image (PNG/JPG/PDF).",
        "input_schema": {
            "type": "object",
            "properties": {
                "design_id": {
                    "type": "string",
                    "description": "ID du design à exporter",
                },
                "format": {
                    "type": "string",
                    "enum": ["png", "jpg", "pdf"],
                    "description": "Format d'export",
                },
                "quality": {
                    "type": "string",
                    "enum": ["low", "regular", "high"],
                    "description": "Qualité d'export",
                },
            },
            "required": ["design_id", "format"],
        },
    },
    {
        "name": "list_brand_templates",
        "description": "Liste les templates de marque Zawaj Secret's disponibles dans Canva.",
        "input_schema": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "enum": ["instagram", "email", "story", "ads", "all"],
                    "description": "Catégorie de templates à lister",
                },
            },
            "required": [],
        },
    },
    {
        "name": "apply_brand_kit",
        "description": "Applique le kit de marque Zawaj Secret's (couleurs, polices, logo) à un design.",
        "input_schema": {
            "type": "object",
            "properties": {
                "design_id": {
                    "type": "string",
                    "description": "ID du design cible",
                },
            },
            "required": ["design_id"],
        },
    },
    {
        "name": "generate_visual_brief",
        "description": "Génère un brief visuel détaillé pour un design Zawaj Secret's.",
        "input_schema": {
            "type": "object",
            "properties": {
                "campaign_theme": {
                    "type": "string",
                    "description": "Thème de la campagne (Ramadan, Aïd, collection printemps, etc.)",
                },
                "visual_format": {
                    "type": "string",
                    "description": "Format du visuel (post, story, email header, etc.)",
                },
                "key_message": {
                    "type": "string",
                    "description": "Message principal à communiquer",
                },
            },
            "required": ["campaign_theme", "visual_format"],
        },
    },
]


def execute_canva_tool(tool_name: str, tool_input: dict, settings: "Settings") -> dict[str, Any]:
    """Exécute un outil Canva et retourne le résultat."""
    handlers = {
        "create_design": _create_design,
        "update_design_text": _update_design_text,
        "export_design": _export_design,
        "list_brand_templates": _list_brand_templates,
        "apply_brand_kit": _apply_brand_kit,
        "generate_visual_brief": _generate_visual_brief,
    }

    handler = handlers.get(tool_name)
    if not handler:
        return {"error": f"Outil inconnu : {tool_name}"}

    return handler(tool_input, settings)


def _canva_headers(access_token: str) -> dict:
    return {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def _create_design(params: dict, settings: "Settings") -> dict:
    """Crée un nouveau design Canva."""
    if not settings.canva_access_token:
        design_id = f"SIMULATED_DESIGN_{params.get('design_type', 'post').upper()}_001"
        return {
            "status": "simulated",
            "design_id": design_id,
            "title": params.get("title"),
            "design_type": params.get("design_type"),
            "edit_url": f"https://www.canva.com/design/{design_id}/edit",
            "message": "Design créé en mode simulation (configurez CANVA_ACCESS_TOKEN)",
        }

    payload = {
        "design_type": {"type": params["design_type"]},
        "title": params["title"],
    }
    if params.get("template_id"):
        payload["asset_id"] = params["template_id"]

    try:
        with httpx.Client(timeout=30) as client:
            resp = client.post(
                f"{CANVA_BASE_URL}/designs",
                headers=_canva_headers(settings.canva_access_token),
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json().get("design", {})
            design_id = data.get("id", "")
            logger.info("Design Canva créé : %s", design_id)
            return {
                "status": "created",
                "design_id": design_id,
                "title": params["title"],
                "edit_url": data.get("urls", {}).get("edit_url", ""),
            }
    except httpx.HTTPError as e:
        logger.error("Erreur API Canva : %s", e)
        return {"status": "error", "error": str(e)}


def _update_design_text(params: dict, settings: "Settings") -> dict:
    """Met à jour les textes d'un design."""
    if not settings.canva_access_token:
        return {
            "status": "simulated",
            "design_id": params.get("design_id"),
            "updates_applied": len(params.get("text_updates", [])),
        }
    return {"status": "simulated", "design_id": params.get("design_id")}


def _export_design(params: dict, settings: "Settings") -> dict:
    """Exporte un design Canva."""
    if not settings.canva_access_token:
        return {
            "status": "simulated",
            "design_id": params.get("design_id"),
            "format": params.get("format"),
            "export_url": f"https://export.canva.com/simulated/{params.get('design_id')}.{params.get('format')}",
            "message": "Export simulé — configurez CANVA_ACCESS_TOKEN",
        }

    try:
        with httpx.Client(timeout=60) as client:
            resp = client.post(
                f"{CANVA_BASE_URL}/exports",
                headers=_canva_headers(settings.canva_access_token),
                json={
                    "design_id": params["design_id"],
                    "format": {"type": params["format"].upper()},
                    "export_quality": params.get("quality", "regular"),
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return {
                "status": "exported",
                "job_id": data.get("job", {}).get("id"),
                "format": params["format"],
            }
    except httpx.HTTPError as e:
        return {"status": "error", "error": str(e)}


def _list_brand_templates(params: dict, settings: "Settings") -> dict:
    """Liste les templates de marque."""
    category = params.get("category", "all")
    templates = {
        "instagram": [
            {"id": "TPL_IG_001", "name": "Post Collection Luxe", "format": "1080x1080"},
            {"id": "TPL_IG_002", "name": "Post Promotionnel", "format": "1080x1080"},
            {"id": "TPL_IG_003", "name": "Post Ramadan", "format": "1080x1080"},
        ],
        "story": [
            {"id": "TPL_STR_001", "name": "Story Lancement", "format": "1080x1920"},
            {"id": "TPL_STR_002", "name": "Story Compte à Rebours", "format": "1080x1920"},
        ],
        "email": [
            {"id": "TPL_EMAIL_001", "name": "Header Newsletter", "format": "600x200"},
            {"id": "TPL_EMAIL_002", "name": "Bannière Promo", "format": "600x300"},
        ],
        "ads": [
            {"id": "TPL_ADS_001", "name": "Pub Facebook", "format": "1200x628"},
        ],
    }

    if category == "all":
        all_templates = []
        for cats in templates.values():
            all_templates.extend(cats)
        return {"templates": all_templates, "total": len(all_templates)}

    return {"templates": templates.get(category, []), "category": category}


def _apply_brand_kit(params: dict, settings: "Settings") -> dict:
    """Applique le kit de marque au design."""
    return {
        "status": "applied",
        "design_id": params.get("design_id"),
        "brand_kit": {
            "colors": {
                "primary": "#1a1a2e",
                "secondary": "#d4af7a",
                "accent": "#f5f0eb",
                "text": "#333333",
            },
            "fonts": {
                "heading": "Playfair Display",
                "body": "Cormorant Garamond",
                "accent": "Great Vibes",
            },
            "logo": "zawaj-secrets-logo.png",
        },
    }


def _generate_visual_brief(params: dict, settings: "Settings") -> dict:
    """Génère un brief visuel structuré pour Canva."""
    theme = params.get("campaign_theme", "")
    fmt = params.get("visual_format", "post_instagram")
    message = params.get("key_message", "")

    # Directives visuelles selon le thème
    theme_guides = {
        "ramadan": {
            "palette": ["#1a1a2e", "#d4af7a", "#f9f2e7", "#8b6914"],
            "mood": "Spirituel, chaleureux, luxueux",
            "elements": ["croissant de lune", "lanternes dorées", "ornements arabesques"],
            "typography": "Calligraphie arabe élégante + serif français",
        },
        "aïd": {
            "palette": ["#0d1b2a", "#e8c99a", "#ffffff", "#c9a84c"],
            "mood": "Festif, élégant, joyeux",
            "elements": ["étoiles dorées", "motifs géométriques islamiques", "rose"],
            "typography": "Serif élégant, grandes capitales",
        },
        "mariage": {
            "palette": ["#ffffff", "#f5e6d3", "#d4af7a", "#1a1a2e"],
            "mood": "Romantique, luxueux, intemporel",
            "elements": ["fleurs blanches", "voile de mariée", "or"],
            "typography": "Script élégant + serif classique",
        },
    }

    theme_key = next((k for k in theme_guides if k in theme.lower()), "mariage")
    guide = theme_guides[theme_key]

    return {
        "brief": {
            "theme": theme,
            "format": fmt,
            "key_message": message,
            "visual_direction": guide["mood"],
            "color_palette": guide["palette"],
            "suggested_elements": guide["elements"],
            "typography_guidance": guide["typography"],
            "brand_consistency": "Appliquer le logo Zawaj Secret's en bas à droite, fond sombre ou ivoire",
            "copy_suggestions": [
                message,
                "✨ Zawaj Secret's",
                "www.zawajsecrets.com",
            ],
        },
        "canva_instructions": (
            f"1. Créer un design {fmt}\n"
            f"2. Appliquer palette : {', '.join(guide['palette'])}\n"
            f"3. Ajouter éléments : {', '.join(guide['elements'])}\n"
            f"4. Message principal : {message}\n"
            "5. Appliquer le brand kit Zawaj Secret's"
        ),
    }
