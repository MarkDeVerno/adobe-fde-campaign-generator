"""
Azure Translator Text API client for campaign message translation.
"""
import os
import requests
from typing import Optional, Dict
import structlog

logger = structlog.get_logger()


class TranslatorClient:
    """Client for Azure Translator Text API."""

    # Market to locale mapping
    MARKET_TO_LOCALE: Dict[str, str] = {
        "APAC": "zh-Hans",           # Simplified Chinese (widely used in APAC)
        "North America": "en",        # English
        "Europe": "en",               # English (default, can be fr/de/es based on specific country)
        "EMEA": "en",                 # English (default for multi-region)
        "Middle East": "ar",          # Arabic
        "Asia Pacific": "zh-Hans",    # Simplified Chinese
        "Latin America": "es",        # Spanish
        "Global": "en",               # English (default)
        "Enterprise B2B": "en",       # English (business default)
    }

    def __init__(self):
        """Initialize Translator client with Azure credentials."""
        self.key = os.getenv("AZURE_TRANSLATOR_KEY")
        self.region = os.getenv("AZURE_TRANSLATOR_REGION", "eastus")
        self.endpoint = os.getenv(
            "AZURE_TRANSLATOR_ENDPOINT",
            "https://api.cognitive.microsofttranslator.com"
        )

        if not self.key:
            logger.warning(
                "Azure Translator not configured - translations will be skipped",
                hint="Set AZURE_TRANSLATOR_KEY in .env to enable translation"
            )
            self.enabled = False
        else:
            self.enabled = True
            logger.info(
                "Translator client initialized",
                endpoint=self.endpoint,
                region=self.region
            )

    async def translate_campaign_message(
        self,
        message: str,
        target_market: str,
        from_locale: str = "en"
    ) -> Optional[str]:
        """
        Translate campaign message to target market locale.

        Args:
            message: Original campaign message
            target_market: Target market (e.g., "APAC", "Europe")
            from_locale: Source locale (default: "en")

        Returns:
            Translated message, or original if translation disabled/failed
        """
        if not self.enabled:
            logger.debug("Translation disabled - returning original message")
            return message

        # Get target locale from market mapping
        target_locale = self.MARKET_TO_LOCALE.get(target_market, "en")

        # Skip translation if source and target are the same
        if from_locale == target_locale:
            logger.debug(
                "Source and target locale are the same - skipping translation",
                locale=from_locale
            )
            return message

        try:
            logger.info(
                "Translating campaign message",
                from_locale=from_locale,
                to_locale=target_locale,
                target_market=target_market,
                message_length=len(message)
            )

            # Azure Translator Text API endpoint
            path = '/translate'
            constructed_url = self.endpoint + path

            # Request parameters
            params = {
                'api-version': '3.0',
                'from': from_locale,
                'to': target_locale
            }

            # Request headers
            headers = {
                'Ocp-Apim-Subscription-Key': self.key,
                'Ocp-Apim-Subscription-Region': self.region,
                'Content-type': 'application/json'
            }

            # Request body
            body = [{'text': message}]

            # Make synchronous request (using requests library)
            response = requests.post(
                constructed_url,
                params=params,
                headers=headers,
                json=body,
                timeout=10
            )

            if response.status_code == 200:
                translations = response.json()
                translated_text = translations[0]['translations'][0]['text']

                logger.info(
                    "Translation successful",
                    original_message=message[:50],
                    translated_message=translated_text[:50],
                    from_locale=from_locale,
                    to_locale=target_locale
                )

                return translated_text

            else:
                logger.error(
                    "Translation API error",
                    status_code=response.status_code,
                    error=response.text
                )
                return message  # Return original on error

        except Exception as e:
            logger.error(
                "Translation failed",
                error=str(e),
                target_market=target_market
            )
            return message  # Graceful degradation - return original

    def get_target_locale(self, target_market: str) -> str:
        """
        Get target locale for a given market.

        Args:
            target_market: Target market string

        Returns:
            Locale code (e.g., "zh-Hans", "es", "ar")
        """
        return self.MARKET_TO_LOCALE.get(target_market, "en")
