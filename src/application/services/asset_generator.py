"""
Asset generation service coordinating image creation and composition.
"""
import asyncio
from typing import List, Optional
from pathlib import Path
from datetime import datetime
import structlog

from src.domain.models.campaign import Campaign
from src.domain.models.asset import Asset, AspectRatio
from src.infrastructure.azure.dalle_client import DALLEClient
from src.infrastructure.image_processing.composer import ImageComposer
from PIL import Image

logger = structlog.get_logger()


class AssetGeneratorService:
    """Service for generating and composing campaign assets with concurrent execution."""

    def __init__(
        self,
        output_dir: str = "outputs",
        enable_caching: bool = True
    ):
        """
        Initialize asset generator service.

        Args:
            output_dir: Directory for generated assets
            enable_caching: Whether to reuse existing assets
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.dalle_client = DALLEClient()
        self.image_composer = ImageComposer()
        self.enable_caching = enable_caching

        logger.info(
            "Asset generator initialized",
            output_dir=str(self.output_dir),
            caching_enabled=enable_caching
        )

    async def generate_all_assets(
        self,
        campaign: Campaign,
        aspect_ratios: List[AspectRatio]
    ) -> List[Asset]:
        """
        Generate images for all products and aspect ratios concurrently.

        Uses asyncio.gather for parallel generation to maximize throughput.

        Args:
            campaign: Campaign with products and targeting
            aspect_ratios: List of aspect ratios to generate

        Returns:
            List of generated Asset objects
        """
        logger.info(
            "Starting parallel asset generation",
            products_count=len(campaign.products),
            aspect_ratios_count=len(aspect_ratios),
            total_assets=len(campaign.products) * len(aspect_ratios)
        )

        # Create tasks for all product-aspect_ratio combinations
        tasks = []
        for product in campaign.products:
            for aspect_ratio in aspect_ratios:
                task = self._generate_single_asset(
                    campaign=campaign,
                    product=product,
                    aspect_ratio=aspect_ratio
                )
                tasks.append(task)

        # Execute all tasks concurrently using asyncio.gather
        logger.info(f"Launching {len(tasks)} parallel image generation tasks")
        start_time = datetime.now()

        # Use asyncio.gather to run all tasks concurrently
        assets = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out failed generations (None or exceptions)
        successful_assets = [
            asset for asset in assets
            if asset is not None and not isinstance(asset, Exception)
        ]

        failed_count = len(assets) - len(successful_assets)
        elapsed = (datetime.now() - start_time).total_seconds()

        logger.info(
            "Parallel asset generation complete",
            total_tasks=len(tasks),
            successful=len(successful_assets),
            failed=failed_count,
            elapsed_seconds=round(elapsed, 2),
            avg_time_per_asset=round(elapsed / len(tasks), 2) if tasks else 0
        )

        return successful_assets

    async def _generate_single_asset(
        self,
        campaign: Campaign,
        product,
        aspect_ratio: AspectRatio
    ) -> Optional[Asset]:
        """
        Generate a single asset for a product and aspect ratio.

        Args:
            campaign: Campaign context
            product: Product object with name, description, and optional input_asset
            aspect_ratio: Target aspect ratio

        Returns:
            Asset object if successful, None if failed
        """
        try:
            # Create subdirectory structure: outputs/{product_name}/{aspect_ratio}/
            aspect_ratio_str = aspect_ratio.value.replace(':', 'x')
            product_dir = self.output_dir / product.name / aspect_ratio_str
            product_dir.mkdir(parents=True, exist_ok=True)

            # Generate filename
            filename = f"{campaign.campaign_id}_{product.name}_{aspect_ratio_str}.png"
            file_path = product_dir / filename

            # Check cache if enabled
            if self.enable_caching and file_path.exists():
                logger.info(
                    "Reusing cached asset",
                    product=product.name,
                    aspect_ratio=aspect_ratio.value,
                    path=str(file_path)
                )
                return Asset(
                    product_name=product.name,
                    aspect_ratio=aspect_ratio,
                    file_path=str(file_path),
                    was_reused=True
                )

            # Check if product has input asset
            if product.input_asset:
                logger.info(
                    "Using input asset",
                    product=product.name,
                    input_path=product.input_asset,
                    aspect_ratio=aspect_ratio.value
                )
                return await self._load_input_asset(
                    product=product,
                    aspect_ratio=aspect_ratio,
                    output_path=file_path,
                    campaign_id=campaign.campaign_id
                )

            # Build prompt
            prompt = self._build_generation_prompt(
                product_name=product.name,
                product_description=product.description,
                target_audience=campaign.target_audience,
                target_market=campaign.target_market
            )

            # Get dimensions for aspect ratio
            width, height = aspect_ratio.dimensions
            size = f"{width}x{height}"

            logger.info(
                "Generating new asset",
                product=product.name,
                aspect_ratio=aspect_ratio.value,
                size=size
            )

            # Generate image with DALL-E 3
            image_url = await self.dalle_client.generate_image(
                prompt=prompt,
                size=size,
                quality="standard"
            )

            if not image_url:
                logger.error("Failed to generate image", product=product.name)
                return None

            # Download image
            download_success = await self.dalle_client.download_image(
                url=image_url,
                output_path=str(file_path)
            )

            if not download_success:
                logger.error("Failed to download image", product=product.name)
                return None

            logger.info(
                "Asset generated successfully",
                product=product.name,
                aspect_ratio=aspect_ratio.value,
                path=str(file_path)
            )

            return Asset(
                product_name=product.name,
                aspect_ratio=aspect_ratio,
                file_path=str(file_path),
                was_reused=False,
                generation_prompt=prompt
            )

        except Exception as e:
            logger.error(
                "Error generating asset",
                product=product.name,
                aspect_ratio=aspect_ratio.value,
                error=str(e)
            )
            return None

    async def _load_input_asset(
        self,
        product,
        aspect_ratio: AspectRatio,
        output_path: Path,
        campaign_id: str
    ) -> Optional[Asset]:
        """
        Load and resize input asset from provided path.

        Args:
            product: Product object with input_asset path
            aspect_ratio: Target aspect ratio
            output_path: Path to save resized image
            campaign_id: Campaign identifier

        Returns:
            Asset object if successful, None if failed
        """
        try:
            input_path = Path(product.input_asset)

            # Validate input file exists
            if not input_path.exists():
                logger.error(
                    "Input asset not found",
                    product=product.name,
                    path=str(input_path)
                )
                return None

            # Load image
            img = Image.open(input_path)

            # Resize to target aspect ratio
            resized_img = self.image_composer.resize_image(img, aspect_ratio)

            # Save resized image
            resized_img.save(output_path, quality=95)

            logger.info(
                "Input asset loaded and resized",
                product=product.name,
                input_path=str(input_path),
                output_path=str(output_path),
                aspect_ratio=aspect_ratio.value
            )

            return Asset(
                product_name=product.name,
                aspect_ratio=aspect_ratio,
                file_path=str(output_path),
                was_reused=False,
                generation_prompt=f"Input asset from {input_path}"
            )

        except Exception as e:
            logger.error(
                "Failed to load input asset",
                product=product.name,
                error=str(e)
            )
            return None

    async def compose_assets(
        self,
        assets: List[Asset],
        campaign_message: str,
        brand_color: str
    ) -> List[Asset]:
        """
        Add campaign message overlay to all assets concurrently.

        Uses asyncio.gather for parallel composition.

        Args:
            assets: List of base assets
            campaign_message: Text to overlay
            brand_color: Brand color for text background

        Returns:
            List of composed Asset objects
        """
        logger.info(
            "Starting asset composition",
            assets_count=len(assets),
            message_length=len(campaign_message)
        )

        # Create tasks for all assets
        tasks = [
            self._compose_single_asset(asset, campaign_message, brand_color)
            for asset in assets
        ]

        # Execute all compositions concurrently using asyncio.gather
        composed_assets = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out failures
        successful_assets = [
            asset for asset in composed_assets
            if asset is not None and not isinstance(asset, Exception)
        ]

        logger.info(
            "Asset composition complete",
            successful=len(successful_assets),
            failed=len(assets) - len(successful_assets)
        )

        return successful_assets

    async def _compose_single_asset(
        self,
        asset: Asset,
        campaign_message: str,
        brand_color: str
    ) -> Optional[Asset]:
        """
        Add campaign message overlay to a single asset.

        Args:
            asset: Base asset
            campaign_message: Text to overlay
            brand_color: Brand color for background

        Returns:
            Updated Asset object with composed image
        """
        try:
            # Load image
            img = Image.open(asset.file_path)

            # Add text overlay
            composed_img = self.image_composer.add_text_overlay(
                image=img,
                text=campaign_message,
                position="bottom",
                text_color="#FFFFFF",
                background_color=brand_color,
                background_opacity=180
            )

            # Save composed image (overwrite original)
            composed_img.save(asset.file_path, quality=95)

            logger.info(
                "Asset composed",
                product=asset.product_name,
                aspect_ratio=asset.aspect_ratio
            )

            return asset

        except Exception as e:
            logger.error(
                "Error composing asset",
                product=asset.product_name,
                error=str(e)
            )
            return None

    def _build_generation_prompt(
        self,
        product_name: str,
        product_description: str,
        target_audience: str,
        target_market: str
    ) -> str:
        """
        Build DALL-E generation prompt from product and campaign context.

        Args:
            product_name: Product name
            product_description: Product description
            target_audience: Target audience
            target_market: Target market

        Returns:
            Optimized prompt for DALL-E 3
        """
        # DALL-E 3 works best with clear, descriptive prompts
        prompt = (
            f"Professional advertising photo of {product_name}. "
            f"{product_description}. "
            f"Target audience: {target_audience} in {target_market}. "
            f"High quality product photography, clean background, well-lit, "
            f"professional marketing style, photorealistic."
        )

        # Truncate if too long (DALL-E has token limits)
        if len(prompt) > 1000:
            prompt = prompt[:997] + "..."

        return prompt
