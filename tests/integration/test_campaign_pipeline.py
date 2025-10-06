"""
Integration tests for campaign generation pipeline.
Tests end-to-end flow with mocked Azure responses.
"""
import pytest
import asyncio
import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from PIL import Image

from src.domain.models.campaign import Campaign, Product, BrandGuidelines
from src.domain.models.asset import Asset, AspectRatio
from src.domain.models.compliance import ComplianceResult
from src.infrastructure.azure.dalle_client import DALLEClient
from src.infrastructure.azure.content_safety_client import ContentSafetyService
from src.infrastructure.image_processing.composer import ImageComposer


@pytest.fixture
def sample_campaign_yaml(tmp_path):
    """Create sample campaign YAML file."""
    yaml_content = """
campaign_id: summer-2024-eco
products:
  - name: Bamboo Toothbrush
    description: Eco-friendly bamboo toothbrush with soft bristles
  - name: Reusable Water Bottle
    description: Stainless steel water bottle, keeps drinks cold for 24 hours

target_market: US
target_audience: Environmentally conscious millennials aged 25-35
campaign_message: "Make every day Earth Day with sustainable choices"

brand_guidelines:
  primary_color: "#2E7D32"
  secondary_color: "#81C784"
  logo_required: false
  font_family: "Arial"
"""
    yaml_file = tmp_path / "campaign_example.yaml"
    yaml_file.write_text(yaml_content)
    return yaml_file


@pytest.fixture
def sample_campaign():
    """Create sample campaign object."""
    return Campaign(
        campaign_id="test-campaign-001",
        products=[
            Product(name="Product A", description="Description for product A"),
            Product(name="Product B", description="Description for product B")
        ],
        target_market="US",
        target_audience="Young professionals",
        campaign_message="Innovative solutions for modern life",
        brand_guidelines=BrandGuidelines(primary_color="#FF5722")
    )


@pytest.fixture
def mock_dalle_response():
    """Mock DALL-E API response."""
    mock_response = MagicMock()
    mock_response.data = [MagicMock(url="https://example.com/generated-image.png")]
    return mock_response


@pytest.fixture
def mock_image_download(tmp_path):
    """Create mock downloaded image."""
    img_path = tmp_path / "test_image.png"
    img = Image.new('RGB', (1024, 1024), color='blue')
    img.save(img_path)
    return img_path


class TestCampaignYAMLLoading:
    """Test campaign YAML parsing and validation."""

    def test_load_valid_yaml(self, sample_campaign_yaml):
        """Test loading valid campaign YAML file."""
        import yaml
        from pydantic import ValidationError

        with open(sample_campaign_yaml, 'r') as f:
            data = yaml.safe_load(f)

        # Should parse without errors
        campaign = Campaign(**data)

        assert campaign.campaign_id == "summer-2024-eco"
        assert len(campaign.products) == 2
        assert campaign.products[0].name == "Bamboo Toothbrush"
        assert campaign.target_market == "US"
        assert campaign.brand_guidelines.primary_color == "#2E7D32"

    def test_yaml_missing_required_fields(self, tmp_path):
        """Test YAML validation catches missing required fields."""
        import yaml
        from pydantic import ValidationError

        incomplete_yaml = """
campaign_id: test
products:
  - name: Product A
    description: Description A
# Missing target_market, target_audience, campaign_message
"""
        yaml_file = tmp_path / "incomplete.yaml"
        yaml_file.write_text(incomplete_yaml)

        with open(yaml_file, 'r') as f:
            data = yaml.safe_load(f)

        with pytest.raises(ValidationError):
            Campaign(**data)

    def test_yaml_validates_product_minimum(self, tmp_path):
        """Test YAML validation enforces minimum 2 products."""
        import yaml
        from pydantic import ValidationError

        single_product_yaml = """
campaign_id: test
products:
  - name: Product A
    description: Description A
target_market: US
target_audience: Everyone
campaign_message: Test message
"""
        yaml_file = tmp_path / "single_product.yaml"
        yaml_file.write_text(single_product_yaml)

        with open(yaml_file, 'r') as f:
            data = yaml.safe_load(f)

        with pytest.raises(ValidationError) as exc_info:
            Campaign(**data)

        assert "at least 2 items" in str(exc_info.value).lower()


class TestComplianceChecks:
    """Test Azure Content Safety compliance checks."""

    def test_safe_message_passes(self, sample_campaign):
        """Test that safe campaign message passes compliance."""
        with patch.dict(os.environ, {
            'AZURE_CONTENT_SAFETY_ENDPOINT': 'https://test.cognitiveservices.azure.com/',
            'AZURE_CONTENT_SAFETY_KEY': 'test-key'
        }):
            with patch('src.infrastructure.azure.content_safety_client.ContentSafetyClient') as mock_client:
                # Mock safe response
                mock_response = MagicMock()
                mock_response.hate_result.severity = 0
                mock_response.self_harm_result.severity = 0
                mock_response.sexual_result.severity = 0
                mock_response.violence_result.severity = 0
                mock_response.blocklists_match_results = []

                mock_client.return_value.analyze_text.return_value = mock_response

                service = ContentSafetyService()
                result = service.analyze_campaign_message(sample_campaign.campaign_message)

                assert result.passed is True
                assert len(result.blocklist_matches) == 0
                assert "passed all compliance" in result.recommendation

    def test_prohibited_terms_detected(self):
        """Test that prohibited advertising terms are detected."""
        with patch.dict(os.environ, {
            'AZURE_CONTENT_SAFETY_ENDPOINT': 'https://test.cognitiveservices.azure.com/',
            'AZURE_CONTENT_SAFETY_KEY': 'test-key'
        }):
            with patch('src.infrastructure.azure.content_safety_client.ContentSafetyClient') as mock_client:
                # Mock response with blocklist matches
                mock_response = MagicMock()
                mock_response.hate_result.severity = 0
                mock_response.self_harm_result.severity = 0
                mock_response.sexual_result.severity = 0
                mock_response.violence_result.severity = 0

                # Simulate blocklist matches
                mock_match = MagicMock()
                mock_item = MagicMock()
                mock_item.text = "guaranteed results"
                mock_match.blocklist_items_matched = [mock_item]
                mock_response.blocklists_match_results = [mock_match]

                mock_client.return_value.analyze_text.return_value = mock_response

                service = ContentSafetyService()
                result = service.analyze_campaign_message("Get guaranteed results today!")

                assert result.passed is False
                assert "guaranteed results" in result.blocklist_matches
                assert "prohibited terms" in result.recommendation.lower()

    def test_high_severity_content_fails(self):
        """Test that high severity content fails compliance."""
        with patch.dict(os.environ, {
            'AZURE_CONTENT_SAFETY_ENDPOINT': 'https://test.cognitiveservices.azure.com/',
            'AZURE_CONTENT_SAFETY_KEY': 'test-key'
        }):
            with patch('src.infrastructure.azure.content_safety_client.ContentSafetyClient') as mock_client:
                # Mock high severity response
                mock_response = MagicMock()
                mock_response.hate_result.severity = 6  # High severity
                mock_response.self_harm_result.severity = 0
                mock_response.sexual_result.severity = 0
                mock_response.violence_result.severity = 0
                mock_response.blocklists_match_results = []

                mock_client.return_value.analyze_text.return_value = mock_response

                service = ContentSafetyService()
                result = service.analyze_campaign_message("Inappropriate content")

                assert result.passed is False
                assert result.severity_scores["Hate"] == 6
                assert "high severity" in result.recommendation.lower()


@pytest.mark.asyncio
class TestEndToEndPipeline:
    """Test complete campaign generation pipeline."""

    async def test_full_pipeline_with_mocked_dalle(self, sample_campaign, mock_dalle_response, tmp_path):
        """Test end-to-end pipeline with mocked DALL-E responses."""
        with patch('src.infrastructure.azure.dalle_client.AsyncAzureOpenAI') as mock_openai:
            # Mock DALL-E generation
            mock_client = AsyncMock()
            mock_client.images.generate.return_value = mock_dalle_response
            mock_openai.return_value = mock_client

            # Mock image download
            async def mock_download(url, path):
                img = Image.new('RGB', (1024, 1024), color='green')
                img.save(path)
                return True

            dalle_client = DALLEClient()

            with patch.object(dalle_client, 'download_image', side_effect=mock_download):
                # Generate image for first product
                prompt = f"Professional product photography of {sample_campaign.products[0].name}"
                image_url = await dalle_client.generate_image(prompt)

                assert image_url == "https://example.com/generated-image.png"

                # Download image
                output_path = tmp_path / "product_a.png"
                success = await dalle_client.download_image(image_url, str(output_path))

                assert success is True
                assert output_path.exists()

                # Verify image can be opened
                img = Image.open(output_path)
                assert img.size == (1024, 1024)

    async def test_pipeline_handles_dalle_failure(self, sample_campaign):
        """Test pipeline gracefully handles DALL-E API failures."""
        with patch('src.infrastructure.azure.dalle_client.AsyncAzureOpenAI') as mock_openai:
            # Mock DALL-E failure
            mock_client = AsyncMock()
            mock_client.images.generate.side_effect = Exception("API quota exceeded")
            mock_openai.return_value = mock_client

            dalle_client = DALLEClient()

            # Should return None instead of crashing
            prompt = "Test prompt"
            result = await dalle_client.generate_image(prompt)

            assert result is None


class TestImageComposition:
    """Test image composition functionality."""

    def test_image_composition_pipeline(self, mock_image_download, tmp_path):
        """Test image resizing and text overlay pipeline."""
        composer = ImageComposer()

        # Load test image
        img = Image.open(mock_image_download)

        # Test resize for different aspect ratios
        for aspect_ratio in [AspectRatio.SQUARE, AspectRatio.STORY, AspectRatio.WIDE]:
            resized = composer.resize_image(img, aspect_ratio)
            assert resized.size == aspect_ratio.dimensions

        # Test text overlay
        message = "Sustainable living starts here"
        img_with_text = composer.add_text_overlay(img, message, position="bottom")

        # Save and verify
        output_path = tmp_path / "composed_image.png"
        img_with_text.save(output_path)

        assert output_path.exists()
        composed = Image.open(output_path)
        assert composed.size == img.size


class TestAssetGeneration:
    """Test asset model and generation tracking."""

    def test_asset_creation(self):
        """Test creating asset domain model."""
        asset = Asset(
            product_name="Test Product",
            aspect_ratio=AspectRatio.SQUARE,
            file_path="/path/to/asset.png",
            was_reused=False,
            generation_prompt="Professional product photo"
        )

        assert asset.product_name == "Test Product"
        assert asset.aspect_ratio == AspectRatio.SQUARE
        assert asset.was_reused is False
        assert asset.generated_at is not None

    def test_aspect_ratio_dimensions(self):
        """Test aspect ratio dimension mappings."""
        assert AspectRatio.SQUARE.dimensions == (1024, 1024)
        assert AspectRatio.STORY.dimensions == (1024, 1792)
        assert AspectRatio.WIDE.dimensions == (1792, 1024)
