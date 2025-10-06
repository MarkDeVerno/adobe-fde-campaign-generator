#!/usr/bin/env python3
"""Quick test script to verify Azure Translator is working."""
import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from infrastructure.azure.translator_client import TranslatorClient


async def test_translation():
    """Test translation from English to Chinese."""
    client = TranslatorClient()

    print(f"Translator enabled: {client.enabled}")
    print(f"Translator endpoint: {client.endpoint}")
    print(f"Translator region: {client.region}")
    print()

    if not client.enabled:
        print("❌ Translator is not configured!")
        return

    # Test message from APAC campaign
    original = "Your home, smarter. Your planet, better."
    target_market = "APAC"

    print(f"Original message: {original}")
    print(f"Target market: {target_market}")
    print(f"Expected locale: {client.get_target_locale(target_market)}")
    print()

    print("Translating...")
    translated = await client.translate_campaign_message(
        message=original,
        target_market=target_market
    )

    print(f"✅ Translated message: {translated}")
    print()

    # Test Arabic translation
    original2 = "Trust. Security. Growth."
    target_market2 = "Middle East"

    print(f"Original message: {original2}")
    print(f"Target market: {target_market2}")
    print(f"Expected locale: {client.get_target_locale(target_market2)}")
    print()

    print("Translating...")
    translated2 = await client.translate_campaign_message(
        message=original2,
        target_market=target_market2
    )

    print(f"✅ Translated message: {translated2}")


if __name__ == "__main__":
    asyncio.run(test_translation())
