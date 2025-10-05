"""
Azure OpenAI DALL-E 3 client for image generation.
"""
import os
import asyncio
import aiohttp
from typing import Optional
from openai import AsyncAzureOpenAI
import structlog

logger = structlog.get_logger()


class DALLEClient:
    """Client for Azure OpenAI DALL-E 3 image generation."""

    def __init__(self):
        """Initialize DALL-E client with Azure credentials."""
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_key = os.getenv("AZURE_OPENAI_KEY")
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "dall-e-3")

        if not self.endpoint or not self.api_key:
            raise ValueError("Azure OpenAI credentials not configured in .env")

        self.client = AsyncAzureOpenAI(
            azure_endpoint=self.endpoint,
            api_key=self.api_key,
            api_version="2024-02-01"
        )

    async def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "standard"
    ) -> Optional[str]:
        """
        Generate image using DALL-E 3.

        Args:
            prompt: Image generation prompt
            size: Image size (1024x1024, 1024x1792, 1792x1024)
            quality: Image quality (standard or hd)

        Returns:
            URL of generated image, or None if generation failed
        """
        try:
            logger.info("Generating image with DALL-E 3", prompt=prompt[:50], size=size)

            response = await self.client.images.generate(
                model=self.deployment_name,
                prompt=prompt,
                size=size,
                quality=quality,
                n=1
            )

            image_url = response.data[0].url
            logger.info("Image generated successfully", url=image_url)

            return image_url

        except Exception as e:
            logger.error("Failed to generate image", error=str(e), prompt=prompt[:50])
            return None

    async def download_image(self, url: str, output_path: str) -> bool:
        """
        Download generated image from URL to local file.

        Args:
            url: Image URL from DALL-E response
            output_path: Local file path to save image

        Returns:
            True if download successful, False otherwise
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        with open(output_path, 'wb') as f:
                            f.write(await response.read())
                        logger.info("Image downloaded", path=output_path)
                        return True
                    else:
                        logger.error("Failed to download image", status=response.status)
                        return False
        except Exception as e:
            logger.error("Error downloading image", error=str(e))
            return False
