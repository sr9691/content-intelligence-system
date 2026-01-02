"""
LangGraph state definitions for Content Intelligence System agent workflows.

The AgentState TypedDict serves as the single source of truth passed between
all nodes in the graph. Each agent reads what it needs and returns only the
keys it updates.
"""

from typing import TypedDict, Any


class ProspectIntent(TypedDict):
    """Intent profile extracted from prospect data."""
    prospect_id: int
    service_area: str | None
    pain_points: list[str]
    confidence: float  # 0.0 to 1.0


class RankedAsset(TypedDict):
    """Content asset with relevance score."""
    asset_id: int
    url: str
    title: str
    room: str  # "problem", "solution", or "offer"
    score: float
    match_reasons: list[str]


class AgentState(TypedDict, total=False):
    """
    Shared state for email generation workflow.
    
    Using total=False allows agents to return partial updates.
    Each agent reads what it needs and returns only modified keys.
    """
    # Input - set by workflow trigger
    prospect_id: int
    campaign_id: int
    
    # Prospect data - populated by data fetch
    prospect_data: dict[str, Any] | None
    
    # Intent analysis - populated by intent_summarizer
    intent_profile: ProspectIntent | None
    
    # Content matching - populated by asset_ranker
    ranked_assets: list[RankedAsset]
    selected_content: dict[str, Any] | None
    
    # Email generation - populated by email assembler
    email_context: dict[str, Any] | None
    generated_email: str | None
    
    # Control flow
    error: str | None
    requires_human_approval: bool


# Convenience function for creating initial state
def create_initial_state(prospect_id: int, campaign_id: int) -> AgentState:
    """Create a new AgentState with required inputs."""
    return AgentState(
        prospect_id=prospect_id,
        campaign_id=campaign_id,
        prospect_data=None,
        intent_profile=None,
        ranked_assets=[],
        selected_content=None,
        email_context=None,
        generated_email=None,
        error=None,
        requires_human_approval=False,
    )
