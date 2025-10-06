"""
Campaign orchestration service coordinating the asset generation pipeline.
"""
import asyncio
from typing import List, Dict, Optional
from pathlib import Path
import structlog

from src.domain.models.campaign import Campaign
from src.domain.models.asset import Asset, AspectRatio
from src.domain.models.compliance import ComplianceResult
from src.application.services.compliance_service import ComplianceService
from src.application.services.asset_generator import AssetGeneratorService
from src.infrastructure.azure.translator_client import TranslatorClient
from src.infrastructure.azure.message_adapter import MessageAdapterService

logger = structlog.get_logger()


class CampaignOrchestrator:
    """Orchestrates the end-to-end campaign asset generation workflow."""

    def __init__(
        self,
        output_dir: str = "outputs",
        enable_compliance_check: bool = True,
        enable_caching: bool = True
    ):
        """
        Initialize campaign orchestrator.

        Args:
            output_dir: Directory for generated assets
            enable_compliance_check: Whether to perform content safety checks
            enable_caching: Whether to reuse existing assets
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.compliance_service = ComplianceService() if enable_compliance_check else None
        self.asset_generator = AssetGeneratorService(
            output_dir=str(self.output_dir),
            enable_caching=enable_caching
        )
        self.message_adapter = MessageAdapterService()
        self.translator_client = TranslatorClient()

        self.enable_compliance_check = enable_compliance_check

        logger.info(
            "Campaign orchestrator initialized",
            output_dir=str(self.output_dir),
            compliance_enabled=enable_compliance_check,
            caching_enabled=enable_caching,
            message_adaptation_enabled=self.message_adapter.enabled,
            translation_enabled=self.translator_client.enabled
        )

    async def generate_campaign(
        self,
        campaign: Campaign,
        aspect_ratios: Optional[List[AspectRatio]] = None
    ) -> Dict[str, any]:
        """
        Execute complete campaign generation pipeline.

        Args:
            campaign: Campaign domain model with products and message
            aspect_ratios: List of aspect ratios to generate (default: all)

        Returns:
            Dictionary with results:
            - success: bool
            - compliance_result: ComplianceResult (if enabled)
            - assets: List[Asset]
            - errors: List[str]
        """
        logger.info(
            "Starting campaign generation",
            campaign_id=campaign.campaign_id,
            products_count=len(campaign.products),
            aspect_ratios=aspect_ratios
        )

        errors = []
        compliance_result = None
        generated_assets = []

        try:
            # Step 1: Load and validate campaign
            logger.info("Step 1: Loading campaign", campaign_id=campaign.campaign_id)
            validation_errors = await self.load_campaign(campaign)
            if validation_errors:
                errors.extend(validation_errors)
                return {
                    "success": False,
                    "compliance_result": None,
                    "assets": [],
                    "errors": errors
                }

            # Step 2: Check compliance (if enabled)
            if self.enable_compliance_check:
                logger.info("Step 2: Checking compliance")
                compliance_result = await self.check_compliance(campaign)

                if compliance_result.has_violations:
                    logger.warning(
                        "Campaign failed compliance check",
                        recommendation=compliance_result.recommendation
                    )
                    errors.append(f"Compliance check failed: {compliance_result.recommendation}")

                    # Return early if compliance fails (optional: could be a warning instead)
                    return {
                        "success": False,
                        "compliance_result": compliance_result,
                        "assets": [],
                        "errors": errors
                    }
                else:
                    logger.info("Campaign passed compliance check")

            # Step 2a: Adapt campaign message for target market/audience using AI
            logger.info("Step 2a: Adapting campaign message for target market")
            adapted_message, adaptation_rationale = await self.message_adapter.adapt_message(
                base_message=campaign.campaign_message,
                target_market=campaign.target_market,
                target_audience=campaign.target_audience,
                brand_voice=campaign.brand_guidelines.get_brand_voice() if hasattr(campaign.brand_guidelines, 'get_brand_voice') else "innovative, authentic"
            )

            # Step 2b: Save adapted message to output folder
            message_file_path = self.output_dir / f"{campaign.campaign_id}_message.md"
            await self._save_message_file(
                file_path=message_file_path,
                campaign=campaign,
                adapted_message=adapted_message,
                adaptation_rationale=adaptation_rationale
            )
            logger.info("Campaign message saved", path=str(message_file_path))

            # Step 2.5: Translate adapted message based on target market (if enabled)
            if self.translator_client.enabled:
                logger.info("Step 2.5: Translating adapted message", target_market=campaign.target_market)
                translated_message = await self.translator_client.translate_campaign_message(
                    message=adapted_message,
                    target_market=campaign.target_market
                )
            else:
                logger.info("Translation disabled, using adapted message")
                translated_message = adapted_message

            # Step 3: Generate images for all products and aspect ratios
            logger.info("Step 3: Generating images")
            generated_assets = await self.generate_images(
                campaign=campaign,
                aspect_ratios=aspect_ratios or [AspectRatio.SQUARE, AspectRatio.STORY, AspectRatio.WIDE]
            )

            if not generated_assets:
                errors.append("No assets were generated")
                return {
                    "success": False,
                    "compliance_result": compliance_result,
                    "assets": [],
                    "errors": errors
                }

            # Step 4: Compose final assets (add campaign message overlay)
            logger.info("Step 4: Composing final assets", message_translated=self.translator_client.enabled)
            final_assets = await self.compose_assets(
                assets=generated_assets,
                campaign_message=translated_message,
                brand_color=campaign.brand_guidelines.primary_color
            )

            logger.info(
                "Campaign generation complete",
                campaign_id=campaign.campaign_id,
                assets_count=len(final_assets)
            )

            return {
                "success": True,
                "compliance_result": compliance_result,
                "assets": final_assets,
                "adapted_message": adapted_message,
                "translated_message": translated_message,
                "errors": errors
            }

        except Exception as e:
            logger.error("Campaign generation failed", error=str(e))
            errors.append(f"Unexpected error: {str(e)}")
            return {
                "success": False,
                "compliance_result": compliance_result,
                "assets": generated_assets,
                "errors": errors
            }

    async def load_campaign(self, campaign: Campaign) -> List[str]:
        """
        Load and validate campaign data.

        Args:
            campaign: Campaign domain model

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Validate campaign has minimum required data
        if not campaign.campaign_id:
            errors.append("Campaign ID is required")

        if len(campaign.products) < 2:
            errors.append("Campaign must have at least 2 products")

        if not campaign.campaign_message or len(campaign.campaign_message.strip()) < 10:
            errors.append("Campaign message must be at least 10 characters")

        if not campaign.target_audience or len(campaign.target_audience.strip()) < 5:
            errors.append("Target audience is required")

        # Validate each product
        for idx, product in enumerate(campaign.products):
            if not product.name or len(product.name.strip()) == 0:
                errors.append(f"Product {idx + 1} missing name")
            if not product.description or len(product.description.strip()) < 10:
                errors.append(f"Product {idx + 1} description too short")

        if errors:
            logger.warning("Campaign validation failed", errors=errors)
        else:
            logger.info("Campaign validation passed", campaign_id=campaign.campaign_id)

        return errors

    async def check_compliance(self, campaign: Campaign) -> ComplianceResult:
        """
        Check campaign message for content safety compliance.

        Args:
            campaign: Campaign with message to check

        Returns:
            ComplianceResult with safety analysis
        """
        if not self.compliance_service:
            logger.warning("Compliance service not initialized, skipping check")
            return ComplianceResult(
                passed=True,
                severity_scores={},
                blocklist_matches=[],
                recommendation="Compliance check disabled"
            )

        return await self.compliance_service.check_message(campaign.campaign_message)

    async def generate_images(
        self,
        campaign: Campaign,
        aspect_ratios: List[AspectRatio]
    ) -> List[Asset]:
        """
        Generate images for all products and aspect ratios concurrently.

        Args:
            campaign: Campaign with products to generate images for
            aspect_ratios: List of aspect ratios to generate

        Returns:
            List of generated Asset objects
        """
        return await self.asset_generator.generate_all_assets(
            campaign=campaign,
            aspect_ratios=aspect_ratios
        )

    async def compose_assets(
        self,
        assets: List[Asset],
        campaign_message: str,
        brand_color: str
    ) -> List[Asset]:
        """
        Add campaign message overlay to all generated assets.

        Args:
            assets: List of generated base assets
            campaign_message: Text to overlay on images
            brand_color: Brand color for text background

        Returns:
            List of composed Asset objects
        """
        return await self.asset_generator.compose_assets(
            assets=assets,
            campaign_message=campaign_message,
            brand_color=brand_color
        )

    async def _save_message_file(
        self,
        file_path: Path,
        campaign: Campaign,
        adapted_message: str,
        adaptation_rationale: str
    ) -> None:
        """
        Save campaign message details to markdown file.

        Args:
            file_path: Path to save message file
            campaign: Campaign model
            adapted_message: AI-adapted message
            adaptation_rationale: Explanation for adaptation
        """
        # Build markdown content
        content = f"""# Campaign Message: {campaign.campaign_id}

## Base Message
{campaign.campaign_message}

## Adapted Message
**{adapted_message}**

### Target Market
{campaign.target_market}

### Target Audience
{campaign.target_audience}

### Brand Guidelines
- Primary Color: {campaign.brand_guidelines.primary_color}
- Secondary Color: {campaign.brand_guidelines.secondary_color}
- Font Family: {campaign.brand_guidelines.font_family}

## Adaptation Rationale
{adaptation_rationale}

---
*Generated: {file_path.stem}*
*This message was AI-adapted for maximum cultural relevance and audience engagement.*
"""

        # Write to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(
            "Message file saved",
            path=str(file_path),
            base_message_length=len(campaign.campaign_message),
            adapted_message_length=len(adapted_message)
        )
