"""
Lead Intent Summarizer Agent

Analyzes prospect data to extract intent signals:
- Service area interest based on page visits
- Pain points from engagement patterns  
- Confidence score for recommendation quality

For MVP: Returns hardcoded intent for testing graph flow.
Production: Will call Claude API for deeper analysis.
"""

import logging
from typing import Any

from models.state import AgentState, ProspectIntent

logger = logging.getLogger(__name__)


def analyze_intent(state: AgentState) -> dict[str, Any]:
    """
    Analyze prospect data to determine intent signals.
    
    Reads: prospect_id, prospect_data
    Returns: intent_profile
    
    For MVP testing, returns mock data. Production implementation
    will use Claude to analyze engagement patterns and firmographics.
    """
    prospect_id = state["prospect_id"]
    prospect_data = state.get("prospect_data")
    
    logger.info(
        "Analyzing intent",
        extra={"prospect_id": prospect_id, "has_data": prospect_data is not None}
    )
    
    # MVP: Return mock intent profile for testing graph execution
    # TODO: Replace with Claude API call for real analysis
    intent_profile: ProspectIntent = {
        "prospect_id": prospect_id,
        "service_area": _extract_service_area(prospect_data),
        "pain_points": _extract_pain_points(prospect_data),
        "confidence": 0.75,
    }
    
    logger.info(
        "Intent analysis complete",
        extra={
            "prospect_id": prospect_id,
            "service_area": intent_profile["service_area"],
            "pain_point_count": len(intent_profile["pain_points"]),
            "confidence": intent_profile["confidence"],
        }
    )
    
    return {"intent_profile": intent_profile}


def _extract_service_area(prospect_data: dict[str, Any] | None) -> str | None:
    """
    Determine primary service area interest from prospect data.
    
    MVP: Returns hardcoded value for testing.
    Production: Analyze page visits, content engagement, firmographics.
    """
    if prospect_data is None:
        return "cloud-migration"  # Default for testing
    
    # Check if prospect data has explicit service area
    if "service_area" in prospect_data:
        return prospect_data["service_area"]
    
    # Default based on industry (mock logic)
    industry = prospect_data.get("industry", "").lower()
    if "health" in industry:
        return "data-analytics"
    elif "finance" in industry:
        return "cloud-migration"
    else:
        return "ai-development"


def _extract_pain_points(prospect_data: dict[str, Any] | None) -> list[str]:
    """
    Extract pain points from prospect signals.
    
    MVP: Returns sample pain points for testing.
    Production: Analyze content engagement, form responses, behavior.
    """
    if prospect_data is None:
        return [
            "POC projects not reaching production",
            "Difficulty connecting AI to business value",
        ]
    
    # Mock pain point extraction based on industry
    industry = prospect_data.get("industry", "").lower()
    
    if "health" in industry:
        return [
            "Data silos preventing analytics adoption",
            "Compliance concerns with cloud migration",
        ]
    elif "finance" in industry:
        return [
            "Legacy systems limiting innovation",
            "High maintenance costs for on-premise infrastructure",
        ]
    else:
        return [
            "AI experiments stuck in POC phase",
            "Unclear roadmap for modernization",
        ]
