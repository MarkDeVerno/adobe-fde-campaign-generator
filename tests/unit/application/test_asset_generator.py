"""Unit tests for AssetGeneratorService."""
import pytest
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from pathlib import Path
from PIL import Image

from src.application.services.asset_generator import AssetGeneratorService
from src.domain.models.campaign import Campaign, Product
from src.domain.models.asset import Asset, AspectRatio


class TestAssetGeneratorService:
    """Test AssetGeneratorService application service."""

    @pytest.fixture
    def mock_dalle_client(self):
        """Create mock DALL-E client."""
        mock = Mock()
        mock.generate_image = AsyncMock(return_value="https://fake-url.com/image.png")
        mock.download_image = AsyncMock(return_value=True)
        return mock

    @pytest.fixture
    def mock_image_composer(self):
        """Create mock ImageComposer."""
        mock = Mock()
        mock_img = Mock(spec=Image.Image)
        mock_img.save = Mock()
        mock.add_text_overlay = Mock(return_value=mock_img)
        mock.resize_image = Mock(return_value=mock_img)
        return mock

    @pytest.fixture
    def asset_generator(self, mock_dalle_client, mock_image_composer, tmp_path):
        """Create AssetGeneratorService with mocked dependencies."""
        with patch('src.application.services.asset_generator.DALLEClient', return_value=mock_dalle_client):
            with patch('src.application.services.asset_generator.ImageComposer', return_value=mock_image_composer):
                service = AssetGeneratorService(output_dir=str(tmp_path))
                return service

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
            campaign_message="Test message"
        )

    @pytest.mark.asyncio
    async def test_generate_all_assets_success(self, asset_generator, sample_campaign):
        """Test successful generation of all assets."""
        # Arrange
        aspect_ratios = [AspectRatio.SQUARE]

        # Act
        assets = await asset_generator.generate_all_assets(
            campaign=sample_campaign,
            aspect_ratios=aspect_ratios
        )

        # Assert
        assert len(assets) == 2  # 2 products × 1 aspect ratio
        assert all(isinstance(asset, Asset) for asset in assets)
        assert all(asset.aspect_ratio == AspectRatio.SQUARE for asset in assets)

    @pytest.mark.asyncio
    async def test_generate_all_assets_multiple_ratios(self, asset_generator, sample_campaign):
        """Test generation with multiple aspect ratios."""
        # Arrange
        aspect_ratios = [AspectRatio.SQUARE, AspectRatio.STORY, AspectRatio.WIDE]

        # Act
        assets = await asset_generator.generate_all_assets(
            campaign=sample_campaign,
            aspect_ratios=aspect_ratios
        )

        # Assert
        assert len(assets) == 6  # 2 products × 3 aspect ratios

    @pytest.mark.asyncio
    async def test_generate_single_asset_new(self, asset_generator, sample_campaign, mock_dalle_client):
        """Test generating a new single asset."""
        # Arrange
        product = sample_campaign.products[0]
        aspect_ratio = AspectRatio.SQUARE
        asset_generator.enable_caching = False

        # Act
        asset = await asset_generator._generate_single_asset(
            campaign=sample_campaign,
            product=product,
            aspect_ratio=aspect_ratio
        )

        # Assert
        assert asset is not None
        assert asset.product_name == "Product A"
        assert asset.aspect_ratio == AspectRatio.SQUARE
        assert asset.was_reused is False
        assert asset.generation_prompt is not None
        mock_dalle_client.generate_image.assert_called_once()
        mock_dalle_client.download_image.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_single_asset_cached(self, asset_generator, sample_campaign, tmp_path):
        """Test reusing cached asset."""
        # Arrange
        product = sample_campaign.products[0]
        aspect_ratio = AspectRatio.SQUARE
        asset_generator.enable_caching = True

        # Create existing file
        product_dir = tmp_path / product.name / aspect_ratio.value.replace(':', 'x')
        product_dir.mkdir(parents=True, exist_ok=True)
        cached_file = product_dir / f"{sample_campaign.campaign_id}_{product.name}_{aspect_ratio.value.replace(':', 'x')}.png"
        cached_file.touch()

        # Act
        asset = await asset_generator._generate_single_asset(
            campaign=sample_campaign,
            product=product,
            aspect_ratio=aspect_ratio
        )

        # Assert
        assert asset is not None
        assert asset.was_reused is True

    @pytest.mark.asyncio
    async def test_generate_single_asset_with_input_asset(self, asset_generator, sample_campaign, tmp_path, mock_image_composer):
        """Test loading input asset instead of generating."""
        # Arrange
        input_file = tmp_path / "input.png"

        # Create a real temporary image file
        test_img = Image.new('RGB', (100, 100), color='red')
        test_img.save(input_file)

        product = Product(
            name="Product C",
            description="Description C",
            input_asset=str(input_file)
        )
        aspect_ratio = AspectRatio.SQUARE

        # Act
        asset = await asset_generator._generate_single_asset(
            campaign=sample_campaign,
            product=product,
            aspect_ratio=aspect_ratio
        )

        # Assert
        assert asset is not None
        assert asset.product_name == "Product C"
        assert "Input asset" in asset.generation_prompt

    @pytest.mark.asyncio
    async def test_generate_single_asset_dalle_failure(self, asset_generator, sample_campaign, mock_dalle_client):
        """Test handling DALL-E generation failure."""
        # Arrange
        product = sample_campaign.products[0]
        aspect_ratio = AspectRatio.SQUARE
        mock_dalle_client.generate_image = AsyncMock(return_value=None)

        # Act
        asset = await asset_generator._generate_single_asset(
            campaign=sample_campaign,
            product=product,
            aspect_ratio=aspect_ratio
        )

        # Assert
        assert asset is None

    @pytest.mark.asyncio
    async def test_load_input_asset_success(self, asset_generator, tmp_path, mock_image_composer):
        """Test loading input asset successfully."""
        # Arrange
        input_file = tmp_path / "input.png"

        # Create a real image file
        test_img = Image.new('RGB', (100, 100), color='blue')
        test_img.save(input_file)

        product = Product(
            name="Test Product",
            description="Test description",
            input_asset=str(input_file)
        )
        output_path = tmp_path / "output.png"

        # Act
        asset = await asset_generator._load_input_asset(
            product=product,
            aspect_ratio=AspectRatio.SQUARE,
            output_path=output_path,
            campaign_id="test-campaign"
        )

        # Assert
        assert asset is not None
        assert asset.product_name == "Test Product"
        mock_image_composer.resize_image.assert_called_once()

    @pytest.mark.asyncio
    async def test_load_input_asset_missing_file(self, asset_generator, tmp_path):
        """Test loading non-existent input asset."""
        # Arrange
        product = Product(
            name="Test Product",
            description="Test description",
            input_asset="/nonexistent/path.png"
        )
        output_path = tmp_path / "output.png"

        # Act
        asset = await asset_generator._load_input_asset(
            product=product,
            aspect_ratio=AspectRatio.SQUARE,
            output_path=output_path,
            campaign_id="test-campaign"
        )

        # Assert
        assert asset is None

    @pytest.mark.asyncio
    async def test_compose_assets_success(self, asset_generator, mock_image_composer, tmp_path):
        """Test composing assets with text overlay."""
        # Arrange
        test_file = tmp_path / "test.png"
        test_img = Image.new('RGB', (100, 100), color='green')
        test_img.save(test_file)

        assets = [
            Asset(
                campaign_id="test",
                product_name="Product A",
                aspect_ratio=AspectRatio.SQUARE,
                file_path=str(test_file)
            )
        ]
        campaign_message = "Test message"
        brand_color = "#FF5733"

        # Act
        composed = await asset_generator.compose_assets(
            assets=assets,
            campaign_message=campaign_message,
            brand_color=brand_color
        )

        # Assert
        assert len(composed) == 1
        mock_image_composer.add_text_overlay.assert_called_once()

    @pytest.mark.asyncio
    async def test_compose_single_asset_success(self, asset_generator, mock_image_composer, tmp_path):
        """Test composing a single asset."""
        # Arrange
        test_file = tmp_path / "test.png"
        test_img = Image.new('RGB', (100, 100), color='yellow')
        test_img.save(test_file)

        asset = Asset(
            campaign_id="test",
            product_name="Product A",
            aspect_ratio=AspectRatio.SQUARE,
            file_path=str(test_file)
        )
        campaign_message = "Test message"
        brand_color = "#33FF57"

        # Act
        result = await asset_generator._compose_single_asset(
            asset=asset,
            campaign_message=campaign_message,
            brand_color=brand_color
        )

        # Assert
        assert result is not None
        assert result == asset
        mock_image_composer.add_text_overlay.assert_called_once()

    def test_build_generation_prompt(self, asset_generator):
        """Test building DALL-E generation prompt."""
        # Act
        prompt = asset_generator._build_generation_prompt(
            product_name="EcoBottle Pro",
            product_description="Sustainable water bottle",
            target_audience="Millennials",
            target_market="US"
        )

        # Assert
        assert "EcoBottle Pro" in prompt
        assert "Sustainable water bottle" in prompt
        assert "Millennials" in prompt
        assert "US" in prompt
        assert len(prompt) <= 1000

    def test_build_generation_prompt_truncation(self, asset_generator):
        """Test prompt truncation for very long descriptions."""
        # Arrange
        long_description = "A" * 2000

        # Act
        prompt = asset_generator._build_generation_prompt(
            product_name="Product",
            product_description=long_description,
            target_audience="Everyone",
            target_market="Global"
        )

        # Assert
        assert len(prompt) == 1000
        assert prompt.endswith("...")
