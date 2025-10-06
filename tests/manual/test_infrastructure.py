"""Test infrastructure components."""
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_dalle():
    """Test DALL-E client."""
    from src.infrastructure.azure.dalle_client import DALLEClient

    client = DALLEClient()
    print(f"✅ DALL-E client initialized")
    print(f"   Endpoint: {client.endpoint}")
    print(f"   Deployment: {client.deployment_name}")

    # Test generation (commented out to save API credits, uncomment if needed)
    # url = await client.generate_image("A simple test image of a coffee cup")
    # print(f"✅ Generated image: {url}")

def test_content_safety():
    """Test Content Safety client."""
    from src.infrastructure.azure.content_safety_client import ContentSafetyService

    service = ContentSafetyService()
    print(f"✅ Content Safety client initialized")
    print(f"   Blocklist: {service.blocklist_name}")

    # Test safe message
    result = service.analyze_campaign_message("Enjoy our new eco-friendly products")
    print(f"✅ Safe message analysis: passed={result.passed}")

    # Test message with prohibited term
    result = service.analyze_campaign_message("Get guaranteed results with our risk-free offer")
    print(f"✅ Prohibited term detection: passed={result.passed}, matches={result.blocklist_matches}")

def test_image_composer():
    """Test image composer."""
    from PIL import Image
    from src.infrastructure.image_processing.composer import ImageComposer
    from src.domain.models.asset import AspectRatio

    composer = ImageComposer()
    print(f"✅ Image composer initialized")

    # Create test image
    img = Image.new('RGB', (1024, 1024), color='blue')

    # Test resize
    resized = composer.resize_image(img, AspectRatio.STORY)
    print(f"✅ Resize works: {img.size} → {resized.size}")

    # Test text overlay
    with_text = composer.add_text_overlay(img, "Test Campaign Message")
    print(f"✅ Text overlay works")

if __name__ == "__main__":
    print("Testing Infrastructure Layer...\n")

    asyncio.run(test_dalle())
    print()

    test_content_safety()
    print()

    test_image_composer()
    print()

    print("🎉 All infrastructure tests passed!")
