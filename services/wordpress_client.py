# =============================================================================
# WordPress REST API Client
# =============================================================================
#
# Provides async methods to interact with DirectReach WordPress tables:
# - cpd_clients: Client profiles
# - dr_campaign_settings: Campaign configurations
# - rtr_room_content_links: Content assets per room
# - rtr_prospects: Qualified prospects with scores
# - rtr_email_templates: Email prompt templates
# - rtr_email_tracking: Email generation logs
#
# All methods use httpx for async HTTP requests.
# =============================================================================

import logging
from typing import Any
from functools import lru_cache

import httpx
from pydantic import BaseModel

from config.settings import settings

logger = logging.getLogger(__name__)


# =============================================================================
# Response Models
# =============================================================================

class Prospect(BaseModel):
    # Prospect data from rtr_prospects table
    id: int
    visitor_id: int
    campaign_id: int
    current_room: str
    lead_score: int
    company_name: str | None = None
    contact_name: str | None = None
    job_title: str | None = None
    industry: str | None = None
    employee_count: str | None = None
    email: str | None = None


class ContentLink(BaseModel):
    # Content asset from rtr_room_content_links table
    id: int
    campaign_id: int
    room: str
    url: str
    title: str
    service_area: str | None = None
    content_type: str | None = None
    persona: str | None = None
    industry: str | None = None
    summary: str | None = None


class Campaign(BaseModel):
    # Campaign from dr_campaign_settings table
    id: int
    client_id: int
    name: str
    utm_source: str | None = None
    utm_medium: str | None = None
    utm_campaign: str | None = None
    active: bool = True


class EmailTemplate(BaseModel):
    # Email template from rtr_email_templates table
    id: int
    campaign_id: int
    room: str
    subject_prompt: str | None = None
    opener_prompt: str | None = None
    body_prompt: str | None = None
    cta_prompt: str | None = None
    closer_prompt: str | None = None


# =============================================================================
# Exceptions
# =============================================================================

class WordPressAPIError(Exception):
    # Raised when WordPress API request fails
    
    def __init__(self, message: str, status_code: int | None = None):
        self.status_code = status_code
        super().__init__(message)


# =============================================================================
# Client
# =============================================================================

class WordPressClient:
    # Async client for DirectReach WordPress REST API
    #
    # Usage:
    #     async with WordPressClient() as wp:
    #         prospect = await wp.get_prospect(45)
    #         content = await wp.get_content_links(campaign_id=1, room="problem")
    
    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        timeout: int | None = None,
    ):
        self.base_url = (base_url or settings.wordpress_base_url).rstrip("/")
        self.api_key = api_key or settings.wordpress_api_key
        self.timeout = timeout or settings.api_timeout_seconds
        self._client: httpx.AsyncClient | None = None
    
    async def __aenter__(self) -> "WordPressClient":
        # Enter async context manager
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "X-API-Key": self.api_key,
                "Content-Type": "application/json",
            },
            timeout=self.timeout,
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        # Exit async context manager
        if self._client:
            await self._client.aclose()
            self._client = None
    
    @property
    def client(self) -> httpx.AsyncClient:
        # Get the HTTP client, raising if not in context
        if self._client is None:
            raise RuntimeError(
                "WordPressClient must be used as async context manager: "
                "async with WordPressClient() as wp:"
            )
        return self._client
    
    # -------------------------------------------------------------------------
    # Prospects
    # -------------------------------------------------------------------------
    
    async def get_prospect(self, prospect_id: int) -> Prospect:
        # Fetch a single prospect by ID
        #
        # Args:
        #     prospect_id: ID from rtr_prospects table
        #
        # Returns:
        #     Prospect model with all fields
        #
        # Raises:
        #     WordPressAPIError: If request fails or prospect not found
        
        endpoint = f"/wp-json/directreach/rtr/v1/prospects/{prospect_id}"
        
        logger.debug(f"Fetching prospect {prospect_id}")
        
        try:
            response = await self.client.get(endpoint)
            response.raise_for_status()
            data = response.json()
            return Prospect.model_validate(data.get("data", data))
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to fetch prospect {prospect_id}: {e}")
            raise WordPressAPIError(
                f"Prospect {prospect_id} not found",
                status_code=e.response.status_code,
            ) from e
        except httpx.RequestError as e:
            logger.error(f"Request failed for prospect {prospect_id}: {e}")
            raise WordPressAPIError(f"Request failed: {e}") from e
    
    async def list_prospects(
        self,
        campaign_id: int,
        room: str | None = None,
        limit: int = 50,
    ) -> list[Prospect]:
        # List prospects for a campaign, optionally filtered by room
        #
        # Args:
        #     campaign_id: Filter by campaign
        #     room: Optional room filter ("problem", "solution", "offer")
        #     limit: Maximum results to return
        #
        # Returns:
        #     List of Prospect models
        
        endpoint = "/wp-json/directreach/rtr/v1/prospects"
        params: dict[str, Any] = {
            "campaign_id": campaign_id,
            "per_page": limit,
        }
        if room:
            params["room"] = room
        
        logger.debug(f"Listing prospects for campaign {campaign_id}")
        
        try:
            response = await self.client.get(endpoint, params=params)
            response.raise_for_status()
            data = response.json()
            items = data.get("data", data) if isinstance(data, dict) else data
            return [Prospect.model_validate(p) for p in items]
        except httpx.HTTPError as e:
            logger.error(f"Failed to list prospects: {e}")
            raise WordPressAPIError(f"Failed to list prospects: {e}") from e
    
    # -------------------------------------------------------------------------
    # Content Links
    # -------------------------------------------------------------------------
    
    async def get_content_links(
        self,
        campaign_id: int,
        room: str | None = None,
        service_area: str | None = None,
    ) -> list[ContentLink]:
        # Fetch content links for a campaign
        #
        # Args:
        #     campaign_id: Filter by campaign
        #     room: Optional room filter ("problem", "solution", "offer")
        #     service_area: Optional service area filter
        #
        # Returns:
        #     List of ContentLink models
        
        endpoint = "/wp-json/directreach/rtr/v1/content-links"
        params: dict[str, Any] = {"campaign_id": campaign_id}
        if room:
            params["room"] = room
        if service_area:
            params["service_area"] = service_area
        
        logger.debug(f"Fetching content links for campaign {campaign_id}")
        
        try:
            response = await self.client.get(endpoint, params=params)
            response.raise_for_status()
            data = response.json()
            items = data.get("data", data) if isinstance(data, dict) else data
            return [ContentLink.model_validate(c) for c in items]
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch content links: {e}")
            raise WordPressAPIError(f"Failed to fetch content links: {e}") from e
    
    # -------------------------------------------------------------------------
    # Campaigns
    # -------------------------------------------------------------------------
    
    async def get_campaign(self, campaign_id: int) -> Campaign:
        # Fetch a campaign by ID
        
        endpoint = f"/wp-json/directreach/rtr/v1/campaigns/{campaign_id}"
        
        try:
            response = await self.client.get(endpoint)
            response.raise_for_status()
            data = response.json()
            return Campaign.model_validate(data.get("data", data))
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch campaign {campaign_id}: {e}")
            raise WordPressAPIError(f"Campaign {campaign_id} not found") from e
    
    # -------------------------------------------------------------------------
    # Email Templates
    # -------------------------------------------------------------------------
    
    async def get_email_template(
        self,
        campaign_id: int,
        room: str,
    ) -> EmailTemplate | None:
        # Fetch email template for a campaign and room
        #
        # Args:
        #     campaign_id: Campaign ID
        #     room: Room name ("problem", "solution", "offer")
        #
        # Returns:
        #     EmailTemplate if found, None otherwise
        
        endpoint = "/wp-json/directreach/rtr/v1/email-templates"
        params = {"campaign_id": campaign_id, "room": room}
        
        try:
            response = await self.client.get(endpoint, params=params)
            response.raise_for_status()
            data = response.json()
            items = data.get("data", data) if isinstance(data, dict) else data
            if items and len(items) > 0:
                return EmailTemplate.model_validate(items[0])
            return None
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch email template: {e}")
            return None
    
    # -------------------------------------------------------------------------
    # Email Tracking
    # -------------------------------------------------------------------------
    
    async def log_email_generation(
        self,
        prospect_id: int,
        campaign_id: int,
        content_link_id: int,
        email_subject: str,
        email_body: str,
    ) -> int:
        # Log a generated email to rtr_email_tracking
        #
        # Returns:
        #     ID of the created tracking record
        
        endpoint = "/wp-json/directreach/rtr/v1/email-tracking"
        payload = {
            "prospect_id": prospect_id,
            "campaign_id": campaign_id,
            "content_link_id": content_link_id,
            "email_subject": email_subject,
            "email_body": email_body,
            "status": "generated",
        }
        
        try:
            response = await self.client.post(endpoint, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("id", data.get("data", {}).get("id", 0))
        except httpx.HTTPError as e:
            logger.error(f"Failed to log email generation: {e}")
            raise WordPressAPIError(f"Failed to log email: {e}") from e


# =============================================================================
# Factory
# =============================================================================

@lru_cache
def get_wordpress_client() -> WordPressClient:
    # Get a WordPress client instance (for dependency injection)
    return WordPressClient()