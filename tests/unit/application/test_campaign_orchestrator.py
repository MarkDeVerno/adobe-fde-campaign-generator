"""Unit tests for CampaignOrchestrator."""
import pytest
from unittest.mock import AsyncMock, Mock, patch
from pathlib import Path

from src.application.services.campaign_orchestrator import CampaignOrchestrator
from src.domain.models.campaign import Campaign, Product, BrandGuidelines
from src.domain.models.asset import Asset, AspectRatio
from src.domain.models.compliance import ComplianceResult


class TestCampaignOrchestrator:
    """Test CampaignOrchestrator application service."""

    @pytest.fixture
    def mock_compliance_service(self):
        """Create mock ComplianceService."""
        mock = Mock()
        mock.check_message = AsyncMock(return_value=ComplianceResult(
            passed=True,
            severity_scores={},
            blocklist_matches=[],
            recommendation="Passed"
        ))
        return mock

    @pytest.fixture
    def mock_asset_generator(self):
        """Create mock AssetGeneratorService."""
        mock = Mock()
        mock.generate_all_assets = AsyncMock(return_value=[
            Asset(
                campaign_id="test",
                product_name="Product A",
                aspect_ratio=AspectRatio.SQUARE,
                file_path="/fake/path.png"
            )
        ])
        mock.compose_assets = AsyncMock(return_value=[
            Asset(
                campaign_id="test",
                product_name="Product A",
                aspect_ratio=AspectRatio.SQUARE,
                file_path="/fake/path.png"
            )
        ])
        return mock

    @pytest.fixture
    def mock_message_adapter(self):
        """Create mock MessageAdapterService."""
        mock = Mock()
        mock.enabled = True
        mock.adapt_message = AsyncMock(return_value=(
            "Adapted message",
            "Rationale for adaptation"
        ))
        return mock

    @pytest.fixture
    def mock_translator_client(self):
        """Create mock TranslatorClient."""
        mock = Mock()
        mock.enabled = True
        mock.translate_campaign_message = AsyncMock(return_value="Translated message")
        return mock

    @pytest.fixture
    def orchestrator(self, mock_compliance_service, mock_asset_generator,
                    mock_message_adapter, mock_translator_client, tmp_path):
        """Create CampaignOrchestrator with mocked dependencies."""
        with patch('src.application.services.campaign_orchestrator.ComplianceService', return_value=mock_compliance_service):
            with patch('src.application.services.campaign_orchestrator.AssetGeneratorService', return_value=mock_asset_generator):
                with patch('src.application.services.campaign_orchestrator.MessageAdapterService', return_value=mock_message_adapter):
                    with patch('src.application.services.campaign_orchestrator.TranslatorClient', return_value=mock_translator_client):
                        return CampaignOrchestrator(output_dir=str(tmp_path))

    @pytest.fixture
    def sample_campaign(self):
        """Create sample campaign for testing."""
        return Campaign(
            campaign_id="test-campaign",
            products=[
                Product(name="Product A", description="Description A"),
                Product(name="Product B", description="Description B")
            ],
            target_market="US",
            target_audience="Millennials",
            campaign_message="Sustainable living for everyone",
            brand_guidelines=BrandGuidelines(
                primary_color="#FF5733",
                secondary_color="#33FF57"
            )
        )

    @pytest.mark.asyncio
    async def test_generate_campaign_success(self, orchestrator, sample_campaign):
        """Test successful end-to-end campaign generation."""
        # Act
        result = await orchestrator.generate_campaign(
            campaign=sample_campaign,
            aspect_ratios=[AspectRatio.SQUARE]
        )

        # Assert
        assert result["success"] is True
        assert result["compliance_result"] is not None
        assert result["compliance_result"].passed is True
        assert len(result["assets"]) == 1
        assert len(result["errors"]) == 0

    # Validation is handled by Pydantic, so invalid campaigns can't be created

    @pytest.mark.asyncio
    async def test_generate_campaign_compliance_failure(self, orchestrator, sample_campaign, mock_compliance_service):
        """Test campaign generation with compliance violations."""
        # Arrange
        mock_compliance_service.check_message = AsyncMock(return_value=ComplianceResult(
            passed=False,
            severity_scores={"hate": 2},
            blocklist_matches=["prohibited-term"],
            recommendation="Remove prohibited terms"
        ))

        # Act
        result = await orchestrator.generate_campaign(
            campaign=sample_campaign,
            aspect_ratios=[AspectRatio.SQUARE]
        )

        # Assert
        assert result["success"] is False
        assert result["compliance_result"].has_violations is True
        assert len(result["assets"]) == 0

    @pytest.mark.asyncio
    async def test_generate_campaign_no_assets_generated(self, orchestrator, sample_campaign, mock_asset_generator):
        """Test campaign generation when no assets are generated."""
        # Arrange
        mock_asset_generator.generate_all_assets = AsyncMock(return_value=[])

        # Act
        result = await orchestrator.generate_campaign(
            campaign=sample_campaign,
            aspect_ratios=[AspectRatio.SQUARE]
        )

        # Assert
        assert result["success"] is False
        assert "No assets were generated" in result["errors"]

    @pytest.mark.asyncio
    async def test_load_campaign_valid(self, orchestrator, sample_campaign):
        """Test loading valid campaign."""
        # Act
        errors = await orchestrator.load_campaign(sample_campaign)

        # Assert
        assert len(errors) == 0

    # Pydantic validation tests moved to domain layer tests

    @pytest.mark.asyncio
    async def test_check_compliance_enabled(self, orchestrator, sample_campaign, mock_compliance_service):
        """Test compliance check when enabled."""
        # Act
        result = await orchestrator.check_compliance(sample_campaign)

        # Assert
        assert result.passed is True
        mock_compliance_service.check_message.assert_called_once_with(sample_campaign.campaign_message)

    @pytest.mark.asyncio
    async def test_check_compliance_disabled(self, tmp_path):
        """Test compliance check when disabled."""
        # Arrange
        with patch('src.application.services.campaign_orchestrator.ComplianceService'):
            with patch('src.application.services.campaign_orchestrator.AssetGeneratorService'):
                with patch('src.application.services.campaign_orchestrator.MessageAdapterService'):
                    with patch('src.application.services.campaign_orchestrator.TranslatorClient'):
                        orchestrator = CampaignOrchestrator(
                            output_dir=str(tmp_path),
                            enable_compliance_check=False
                        )

        campaign = Campaign(
            campaign_id="test",
            products=[
                Product(name="A", description="Description A"),
                Product(name="B", description="Description B")
            ],
            target_market="US",
            target_audience="Millennials",
            campaign_message="Test message"
        )

        # Act
        result = await orchestrator.check_compliance(campaign)

        # Assert
        assert result.passed is True
        assert "disabled" in result.recommendation.lower()

    @pytest.mark.asyncio
    async def test_generate_images(self, orchestrator, sample_campaign, mock_asset_generator):
        """Test image generation delegation."""
        # Arrange
        aspect_ratios = [AspectRatio.SQUARE, AspectRatio.STORY]

        # Act
        assets = await orchestrator.generate_images(
            campaign=sample_campaign,
            aspect_ratios=aspect_ratios
        )

        # Assert
        assert len(assets) > 0
        mock_asset_generator.generate_all_assets.assert_called_once_with(
            campaign=sample_campaign,
            aspect_ratios=aspect_ratios
        )

    @pytest.mark.asyncio
    async def test_compose_assets(self, orchestrator, mock_asset_generator):
        """Test asset composition delegation."""
        # Arrange
        assets = [
            Asset(
                campaign_id="test",
                product_name="Product A",
                aspect_ratio=AspectRatio.SQUARE,
                file_path="/fake/path.png"
            )
        ]
        campaign_message = "Test message"
        brand_color = "#FF5733"

        # Act
        composed = await orchestrator.compose_assets(
            assets=assets,
            campaign_message=campaign_message,
            brand_color=brand_color
        )

        # Assert
        assert len(composed) > 0
        mock_asset_generator.compose_assets.assert_called_once_with(
            assets=assets,
            campaign_message=campaign_message,
            brand_color=brand_color
        )

    @pytest.mark.asyncio
    async def test_save_message_file(self, orchestrator, sample_campaign, tmp_path):
        """Test saving campaign message to file."""
        # Arrange
        file_path = tmp_path / "message.md"
        adapted_message = "Adapted message"
        adaptation_rationale = "Rationale"

        # Act
        await orchestrator._save_message_file(
            file_path=file_path,
            campaign=sample_campaign,
            adapted_message=adapted_message,
            adaptation_rationale=adaptation_rationale
        )

        # Assert
        assert file_path.exists()
        content = file_path.read_text(encoding='utf-8')
        assert "test-campaign" in content
        assert adapted_message in content
        assert adaptation_rationale in content
        assert sample_campaign.campaign_message in content

    @pytest.mark.asyncio
    async def test_generate_campaign_with_exception(self, orchestrator, sample_campaign, mock_asset_generator):
        """Test campaign generation with unexpected exception."""
        # Arrange
        mock_asset_generator.generate_all_assets = AsyncMock(side_effect=Exception("Unexpected error"))

        # Act
        result = await orchestrator.generate_campaign(
            campaign=sample_campaign,
            aspect_ratios=[AspectRatio.SQUARE]
        )

        # Assert
        assert result["success"] is False
        assert len(result["errors"]) > 0
        assert "Unexpected error" in result["errors"][0]
