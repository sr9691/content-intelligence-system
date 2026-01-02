# =============================================================================
# Test script for WordPress client
# =============================================================================
#
# Run from VSCode:
# 1. Open integrated terminal (Ctrl+`)
# 2. Ensure venv is active
# 3. Run: python -m services.test_wordpress
# =============================================================================

import asyncio
import logging

logging.basicConfig(level=logging.INFO)


async def test_client_initialization():
    # Test that client initializes without real API
    
    from services.wordpress_client import WordPressClient
    
    print("\n" + "=" * 50)
    print("TEST: WordPress Client Initialization")
    print("=" * 50)
    
    # Test context manager pattern
    async with WordPressClient(
        base_url="https://example.com",
        api_key="test-key",
    ) as wp:
        print(f"✓ Client created")
        print(f"  Base URL: {wp.base_url}")
        print(f"  Timeout: {wp.timeout}s")
    
    print("✓ Client closed properly")
    return True


async def test_mock_prospect():
    # Test prospect model validation
    
    from services.wordpress_client import Prospect
    
    print("\n" + "=" * 50)
    print("TEST: Prospect Model")
    print("=" * 50)
    
    # Simulate API response
    mock_data = {
        "id": 45,
        "visitor_id": 12,
        "campaign_id": 1,
        "current_room": "solution",
        "lead_score": 47,
        "company_name": "Acme Health",
        "contact_name": "Sarah Johnson",
        "job_title": "VP of Operations",
        "industry": "Healthcare",
        "employee_count": "1001-5000",
    }
    
    prospect = Prospect.model_validate(mock_data)
    print(f"✓ Prospect validated")
    print(f"  ID: {prospect.id}")
    print(f"  Company: {prospect.company_name}")
    print(f"  Room: {prospect.current_room}")
    print(f"  Score: {prospect.lead_score}")
    
    return True


async def test_mock_content_links():
    # Test content link model validation
    
    from services.wordpress_client import ContentLink
    
    print("\n" + "=" * 50)
    print("TEST: ContentLink Model")
    print("=" * 50)
    
    mock_data = {
        "id": 101,
        "campaign_id": 1,
        "room": "problem",
        "url": "https://example.com/blog/data-silos",
        "title": "Drowning in Data Silos?",
        "service_area": "data-analytics",
        "content_type": "blog",
        "summary": "Identifies warning signs of fragmented data.",
    }
    
    link = ContentLink.model_validate(mock_data)
    print(f"✓ ContentLink validated")
    print(f"  Title: {link.title}")
    print(f"  Room: {link.room}")
    print(f"  Service Area: {link.service_area}")
    
    return True


async def main():
    # Run all tests
    
    print("\n" + "#" * 50)
    print("# WordPress Client Test Suite")
    print("#" * 50)
    
    results = []
    results.append(await test_client_initialization())
    results.append(await test_mock_prospect())
    results.append(await test_mock_content_links())
    
    print("\n" + "#" * 50)
    print(f"# All tests passed: {all(results)}")
    print("#" * 50 + "\n")


if __name__ == "__main__":
    asyncio.run(main())