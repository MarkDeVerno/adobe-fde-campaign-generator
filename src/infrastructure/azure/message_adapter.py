"""
Azure OpenAI GPT-4 client for campaign message adaptation.
"""
import os
from typing import Optional
from openai import AsyncAzureOpenAI
import structlog

logger = structlog.get_logger()


class MessageAdapterService:
    """Service for adapting campaign messages using Azure OpenAI GPT-4."""

    def __init__(self):
        """Initialize Azure OpenAI client for message adaptation."""
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_key = os.getenv("AZURE_OPENAI_KEY")
        self.deployment_name = os.getenv("AZURE_OPENAI_GPT_DEPLOYMENT_NAME", "gpt-4o")

        if not self.endpoint or not self.api_key:
            logger.warning(
                "Azure OpenAI not configured for message adaptation - will use base messages",
                hint="Set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_KEY in .env"
            )
            self.enabled = False
            self.client = None
        else:
            self.client = AsyncAzureOpenAI(
                api_key=self.api_key,
                api_version="2024-02-01",
                azure_endpoint=self.endpoint
            )
            self.enabled = True
            logger.info(
                "Message adapter initialized",
                endpoint=self.endpoint,
                deployment=self.deployment_name
            )

    async def adapt_message(
        self,
        base_message: str,
        target_market: str,
        target_audience: str,
        brand_voice: str = "innovative, authentic, customer-focused"
    ) -> tuple[str, str]:
        """
        Adapt campaign message for target market and audience using GPT-4.

        Args:
            base_message: Original campaign message
            target_market: Target market (e.g., "APAC", "North America")
            target_audience: Target audience description
            brand_voice: Brand voice guidelines

        Returns:
            Tuple of (adapted_message, adaptation_rationale)
        """
        if not self.enabled:
            logger.debug("Message adaptation disabled - returning base message")
            return base_message, "Message adaptation disabled - using base message"

        try:
            logger.info(
                "Adapting campaign message",
                target_market=target_market,
                target_audience=target_audience,
                base_message_length=len(base_message)
            )

            # Build adaptation prompt
            prompt = self._build_adaptation_prompt(
                base_message=base_message,
                target_market=target_market,
                target_audience=target_audience,
                brand_voice=brand_voice
            )

            # Call GPT-4 for message adaptation
            response = await self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert marketing copywriter specializing in campaign localization and cultural adaptation."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=200
            )

            # Parse response
            full_response = response.choices[0].message.content.strip()

            # Extract adapted message and rationale
            # Expected format: "ADAPTED: <message>\nRATIONALE: <explanation>"
            if "ADAPTED:" in full_response and "RATIONALE:" in full_response:
                parts = full_response.split("RATIONALE:")
                adapted = parts[0].replace("ADAPTED:", "").strip()
                rationale = parts[1].strip()
            else:
                # Fallback if format not followed
                adapted = full_response
                rationale = "AI-adapted for target market"

            logger.info(
                "Message adaptation successful",
                original_message=base_message[:50],
                adapted_message=adapted[:50],
                rationale=rationale[:100]
            )

            return adapted, rationale

        except Exception as e:
            logger.error(
                "Message adaptation failed",
                error=str(e),
                target_market=target_market
            )
            # Graceful degradation - return original message
            return base_message, f"Adaptation failed: {str(e)}"

    def _build_adaptation_prompt(
        self,
        base_message: str,
        target_market: str,
        target_audience: str,
        brand_voice: str
    ) -> str:
        """
        Build GPT-4 prompt for message adaptation.

        Args:
            base_message: Original message
            target_market: Target market
            target_audience: Target audience
            brand_voice: Brand voice

        Returns:
            Formatted prompt for GPT-4
        """
        prompt = f"""You are adapting a marketing campaign message for maximum cultural relevance and engagement.

Base Campaign Message:
"{base_message}"

Target Market: {target_market}
Target Audience: {target_audience}
Brand Voice: {brand_voice}

Your task:
1. Adapt the message to resonate with the target market and audience
2. Maintain brand voice and core value proposition
3. Consider cultural nuances and local preferences
4. Keep it concise (under 100 characters for social media)

Provide your response in this exact format:
ADAPTED: [Your adapted message here]
RATIONALE: [Brief explanation of why this adaptation works for this audience]

Example:
ADAPTED: Recharge smarter with sustainable tech innovation
RATIONALE: APAC millennials respond to tech innovation + sustainability combined with action-oriented language
"""
        return prompt
