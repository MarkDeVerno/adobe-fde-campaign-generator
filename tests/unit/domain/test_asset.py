"""Unit tests for Asset domain models."""
import pytest
from datetime import datetime
from pydantic import ValidationError

from src.domain.models.asset import Asset, AspectRatio


class TestAspectRatio:
    """Test AspectRatio enum."""

    def test_square_dimensions(self):
        """Test square aspect ratio dimensions."""
        assert AspectRatio.SQUARE.dimensions == (1024, 1024)

    def test_story_dimensions(self):
        """Test story (9:16) aspect ratio dimensions."""
        assert AspectRatio.STORY.dimensions == (1024, 1792)

    def test_wide_dimensions(self):
        """Test wide (16:9) aspect ratio dimensions."""
        assert AspectRatio.WIDE.dimensions == (1792, 1024)

    def test_aspect_ratio_values(self):
        """Test aspect ratio string values."""
        assert AspectRatio.SQUARE.value == "1:1"
        assert AspectRatio.STORY.value == "9:16"
        assert AspectRatio.WIDE.value == "16:9"


class TestAsset:
    """Test Asset model."""

    def test_valid_asset(self):
        """Test creating valid asset."""
        asset = Asset(
            product_name="EcoBottle Pro",
            aspect_ratio=AspectRatio.SQUARE,
            file_path="/path/to/asset.png"
        )
        assert asset.product_name == "EcoBottle Pro"
        assert asset.aspect_ratio == AspectRatio.SQUARE
        assert asset.file_path == "/path/to/asset.png"
        assert asset.was_reused is False
        assert asset.generation_prompt is None
        assert isinstance(asset.generated_at, datetime)

    def test_asset_with_generation_metadata(self):
        """Test asset with generation metadata."""
        asset = Asset(
            product_name="Product A",
            aspect_ratio=AspectRatio.WIDE,
            file_path="/path/to/asset.png",
            was_reused=True,
            generation_prompt="Professional photo of Product A"
        )
        assert asset.was_reused is True
        assert asset.generation_prompt == "Professional photo of Product A"

    def test_asset_requires_product_name(self):
        """Test that product_name is required."""
        with pytest.raises(ValidationError):
            Asset(
                aspect_ratio=AspectRatio.SQUARE,
                file_path="/path/to/asset.png"
            )

    def test_asset_requires_aspect_ratio(self):
        """Test that aspect_ratio is required."""
        with pytest.raises(ValidationError):
            Asset(
                product_name="Product A",
                file_path="/path/to/asset.png"
            )

    def test_asset_requires_file_path(self):
        """Test that file_path is required."""
        with pytest.raises(ValidationError):
            Asset(
                product_name="Product A",
                aspect_ratio=AspectRatio.SQUARE
            )

    def test_asset_generated_at_defaults_to_now(self):
        """Test that generated_at defaults to current timestamp."""
        before = datetime.now()
        asset = Asset(
            product_name="Product A",
            aspect_ratio=AspectRatio.SQUARE,
            file_path="/path/to/asset.png"
        )
        after = datetime.now()

        assert before <= asset.generated_at <= after

    def test_asset_aspect_ratio_enum_values(self):
        """Test that asset can use all aspect ratio enum values."""
        for ratio in AspectRatio:
            asset = Asset(
                product_name="Product",
                aspect_ratio=ratio,
                file_path="/path.png"
            )
            assert asset.aspect_ratio == ratio
