"""Tests unitaires pour les outils des agents."""

import pytest
from unittest.mock import MagicMock


@pytest.fixture
def mock_settings():
    settings = MagicMock()
    settings.anthropic_api_key = "test_key"
    settings.instagram_access_token = ""
    settings.instagram_account_id = ""
    settings.klaviyo_api_key = ""
    settings.klaviyo_list_id = ""
    settings.canva_access_token = ""
    settings.canva_brand_kit_id = ""
    return settings


# --- Instagram tools ---

def test_generate_hashtags_returns_correct_count():
    from zawaj.tools.instagram_tools import _generate_hashtags
    result = _generate_hashtags({"topic": "mariage", "count": 10}, MagicMock())
    assert result["count"] == 10
    assert len(result["hashtags"]) == 10


def test_generate_hashtags_includes_brand():
    from zawaj.tools.instagram_tools import _generate_hashtags
    result = _generate_hashtags({"topic": "ramadan"}, MagicMock())
    assert "#ZawajSecrets" in result["hashtags"]


def test_get_best_posting_time_returns_recommendations():
    from zawaj.tools.instagram_tools import _get_best_posting_time
    result = _get_best_posting_time({}, MagicMock())
    assert "recommendations" in result
    assert len(result["recommendations"]) > 0
    assert result["timezone"] == "Africa/Casablanca"


def test_create_post_simulation(mock_settings):
    from zawaj.tools.instagram_tools import _create_post
    result = _create_post(
        {"caption": "Test caption #ZawajSecrets", "image_url": "https://example.com/img.jpg"},
        mock_settings,
    )
    assert result["status"] == "simulated"
    assert "post_id" in result


def test_get_insights_simulation(mock_settings):
    from zawaj.tools.instagram_tools import _get_insights
    result = _get_insights({"period": "week"}, mock_settings)
    assert result["status"] == "simulated"
    assert "reach" in result


# --- Klaviyo tools ---

def test_generate_email_content_returns_html(mock_settings):
    from zawaj.tools.klaviyo_tools import _generate_email_content
    result = _generate_email_content(
        {"brief": "Nouvelle collection Ramadan", "email_type": "promotional"},
        mock_settings,
    )
    assert result["status"] == "generated"
    assert "<!DOCTYPE html>" in result["html_content"]
    assert "ZAWAJ SECRET'S" in result["html_content"]


def test_generate_email_content_includes_brief(mock_settings):
    from zawaj.tools.klaviyo_tools import _generate_email_content
    brief = "Collection exclusive de caftans brodés pour l'Aïd"
    result = _generate_email_content({"brief": brief, "email_type": "promotional"}, mock_settings)
    assert brief in result["html_content"]


def test_create_email_campaign_simulation(mock_settings):
    from zawaj.tools.klaviyo_tools import _create_email_campaign
    result = _create_email_campaign(
        {"name": "Test Campaign", "subject": "Test Subject", "html_content": "<p>Test</p>"},
        mock_settings,
    )
    assert result["status"] == "simulated"
    assert "campaign_id" in result


def test_get_campaign_metrics_returns_rates(mock_settings):
    from zawaj.tools.klaviyo_tools import _get_campaign_metrics
    result = _get_campaign_metrics({"campaign_id": "TEST_123"}, mock_settings)
    assert "open_rate" in result
    assert "click_rate" in result


# --- Canva tools ---

def test_list_brand_templates_all():
    from zawaj.tools.canva_tools import _list_brand_templates
    result = _list_brand_templates({"category": "all"}, MagicMock())
    assert "templates" in result
    assert result["total"] > 0


def test_list_brand_templates_by_category():
    from zawaj.tools.canva_tools import _list_brand_templates
    result = _list_brand_templates({"category": "instagram"}, MagicMock())
    assert len(result["templates"]) > 0
    assert result["category"] == "instagram"


def test_apply_brand_kit_returns_colors():
    from zawaj.tools.canva_tools import _apply_brand_kit
    result = _apply_brand_kit({"design_id": "TEST_DESIGN"}, MagicMock())
    assert result["status"] == "applied"
    assert result["brand_kit"]["colors"]["primary"] == "#1a1a2e"


def test_generate_visual_brief_ramadan():
    from zawaj.tools.canva_tools import _generate_visual_brief
    result = _generate_visual_brief(
        {"campaign_theme": "Ramadan", "visual_format": "post_instagram", "key_message": "Promo Ramadan"},
        MagicMock(),
    )
    assert "brief" in result
    assert "#1a1a2e" in result["brief"]["color_palette"]


def test_create_design_simulation(mock_settings):
    from zawaj.tools.canva_tools import _create_design
    result = _create_design(
        {"title": "Post Ramadan", "design_type": "instagram_post"},
        mock_settings,
    )
    assert result["status"] == "simulated"
    assert "design_id" in result


# --- Content tools ---

def test_generate_campaign_calendar():
    from zawaj.tools.content_tools import generate_campaign_calendar
    result = generate_campaign_calendar(
        theme="Ramadan 2025",
        start_date="2025-03-01",
        end_date="2025-03-30",
        platforms=["instagram", "klaviyo"],
    )
    assert result["theme"] == "Ramadan 2025"
    assert len(result["schedule"]) > 0


def test_analyze_content_performance_low():
    from zawaj.tools.content_tools import analyze_content_performance
    result = analyze_content_performance({"engagement_rate": 1.5, "reach": 5000})
    assert result["performance"] == "faible"
    assert len(result["recommendations"]) > 0


def test_analyze_content_performance_high():
    from zawaj.tools.content_tools import analyze_content_performance
    result = analyze_content_performance({"engagement_rate": 6.0, "reach": 15000})
    assert result["performance"] == "élevée"


# --- Execute helpers ---

def test_execute_instagram_tool_unknown():
    from zawaj.tools.instagram_tools import execute_instagram_tool
    result = execute_instagram_tool("unknown_tool", {}, MagicMock())
    assert "error" in result


def test_execute_klaviyo_tool_unknown():
    from zawaj.tools.klaviyo_tools import execute_klaviyo_tool
    result = execute_klaviyo_tool("unknown_tool", {}, MagicMock())
    assert "error" in result


def test_execute_canva_tool_unknown():
    from zawaj.tools.canva_tools import execute_canva_tool
    result = execute_canva_tool("unknown_tool", {}, MagicMock())
    assert "error" in result
