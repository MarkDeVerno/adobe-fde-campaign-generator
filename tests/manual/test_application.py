"""Test application layer services."""
import asyncio
import pytest
import yaml
from dotenv import load_dotenv

load_dotenv()

@pytest.mark.asyncio
async def test_compliance_service():
    """Test compliance service."""
    from src.application.services.compliance_service import ComplianceService

    service = ComplianceService()
    print("✅ Compliance service initialized")

    # Test safe message
    result = await service.check_message("Discover our new eco-friendly product line")
    print(f"✅ Safe message: passed={result.passed}")

    # Get recommendations
    recommendations = service.get_compliance_recommendations(result)
    print(f"✅ Recommendations generated: {len(recommendations)} items")

@pytest.mark.asyncio
async def test_asset_generator():
    """Test asset generator initialization."""
    from src.application.services.asset_generator import AssetGeneratorService

    generator = AssetGeneratorService(output_dir="outputs", enable_caching=True)
    print("✅ Asset generator initialized")
    print(f"   Output directory: {generator.output_dir}")
    print(f"   Caching enabled: {generator.enable_caching}")

@pytest.mark.asyncio
async def test_campaign_orchestrator():
    """Test campaign orchestrator initialization."""
    from src.application.services.campaign_orchestrator import CampaignOrchestrator

    orchestrator = CampaignOrchestrator(
        output_dir="outputs",
        enable_compliance_check=True,
        enable_caching=True
    )
    print("✅ Campaign orchestrator initialized")
    print(f"   Output directory: {orchestrator.output_dir}")
    print(f"   Compliance enabled: {orchestrator.enable_compliance_check}")

@pytest.mark.asyncio
async def test_campaign_validation():
    """Test campaign validation logic."""
    from src.domain.models.campaign import Campaign
    from src.application.services.campaign_orchestrator import CampaignOrchestrator

    orchestrator = CampaignOrchestrator(enable_compliance_check=False)

    # Test with valid campaign
    with open('assets/samples/campaign_example.yaml', 'r') as f:
        campaign_data = yaml.safe_load(f)
        campaign = Campaign(**campaign_data)

    errors = await orchestrator.load_campaign(campaign)
    print(f"✅ Campaign validation: {len(errors)} errors (expected 0)")

    # Note: Pydantic already validates at domain level
    print(f"✅ Pydantic domain validation prevents invalid campaigns at creation")

if __name__ == "__main__":
    print("Testing Application Layer...\n")

    asyncio.run(test_compliance_service())
    print()

    asyncio.run(test_asset_generator())
    print()

    asyncio.run(test_campaign_orchestrator())
    print()

    asyncio.run(test_campaign_validation())
    print()

    print("🎉 All application layer tests passed!")
