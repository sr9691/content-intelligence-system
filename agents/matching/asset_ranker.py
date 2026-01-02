"""
Asset Ranker Agent

Ranks available content links for a prospect based on:
- Room match (required - must match prospect's current room)
- Service area alignment (+25 points)
- Persona match (+20 points)
- Industry relevance (+20 points)
- Format preference (+10 points)
- Content freshness (+5 points)

For MVP: Returns hardcoded ranked assets for testing.
Production: Will query WordPress for content links and apply scoring.
"""

import logging
from typing import Any

from models.state import AgentState, RankedAsset

logger = logging.getLogger(__name__)

# Scoring weights per Content Intelligence System spec
SCORING_WEIGHTS = {
    "service_area": 25,
    "persona": 20,
    "industry": 20,
    "format": 10,
    "freshness": 5,
}


def rank_assets(state: AgentState) -> dict[str, Any]:
    """
    Rank available content assets for the prospect.
    
    Reads: intent_profile, prospect_data
    Returns: ranked_assets, selected_content
    
    For MVP, returns mock ranked assets. Production will query
    rtr_room_content_links table via WordPress REST API.
    """
    intent_profile = state.get("intent_profile")
    prospect_data = state.get("prospect_data", {})
    
    if intent_profile is None:
        logger.warning("No intent profile available for ranking")
        return {"ranked_assets": [], "selected_content": None}
    
    service_area = intent_profile.get("service_area", "general")
    
    logger.info(
        "Ranking assets",
        extra={
            "prospect_id": intent_profile["prospect_id"],
            "service_area": service_area,
        }
    )
    
    # MVP: Return mock ranked assets based on service area
    # TODO: Replace with WordPress API call to fetch real content links
    ranked_assets = _get_mock_assets(service_area, prospect_data)
    
    # Select top asset for email
    selected = ranked_assets[0] if ranked_assets else None
    
    logger.info(
        "Asset ranking complete",
        extra={
            "total_candidates": len(ranked_assets),
            "selected_asset": selected["title"] if selected else None,
        }
    )
    
    return {
        "ranked_assets": ranked_assets,
        "selected_content": selected,
    }


def _get_mock_assets(service_area: str, prospect_data: dict) -> list[RankedAsset]:
    """
    Generate mock ranked assets for testing.
    
    Production: Query rtr_room_content_links filtered by campaign,
    then score each asset against prospect intent.
    """
    # Mock content library organized by service area
    mock_library: dict[str, list[RankedAsset]] = {
        "ai-development": [
            {
                "asset_id": 101,
                "url": "https://example.com/blog/poc-limbo",
                "title": "Are Your Gen AI Experiments Stuck in POC Limbo?",
                "room": "problem",
                "score": 85.0,
                "match_reasons": ["service_area", "pain_point_match"],
            },
            {
                "asset_id": 102,
                "url": "https://example.com/blog/ai-roadmap",
                "title": "Building an AI Roadmap: 5 Priorities for Getting Started",
                "room": "solution",
                "score": 72.0,
                "match_reasons": ["service_area", "industry_match"],
            },
        ],
        "cloud-migration": [
            {
                "asset_id": 201,
                "url": "https://example.com/blog/data-center-budget",
                "title": "Is Your Data Center Draining Your Budget?",
                "room": "problem",
                "score": 88.0,
                "match_reasons": ["service_area", "pain_point_match", "persona"],
            },
            {
                "asset_id": 202,
                "url": "https://example.com/blog/migration-roadmap",
                "title": "Understanding Your Migration Roadmap and TCO",
                "room": "solution",
                "score": 70.0,
                "match_reasons": ["service_area"],
            },
        ],
        "data-analytics": [
            {
                "asset_id": 301,
                "url": "https://example.com/blog/data-silos",
                "title": "Drowning in Data Silos? 7 Red Flags to Watch For",
                "room": "problem",
                "score": 82.0,
                "match_reasons": ["service_area", "industry_match"],
            },
            {
                "asset_id": 302,
                "url": "https://example.com/blog/lakehouse-comparison",
                "title": "Data Lakehouse vs. Traditional Warehousing: Pros and Cons",
                "room": "solution",
                "score": 68.0,
                "match_reasons": ["service_area"],
            },
        ],
    }
    
    # Return assets for the service area, or default set
    return mock_library.get(service_area, mock_library["ai-development"])
