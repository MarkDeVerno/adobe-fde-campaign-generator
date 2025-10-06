"""Unit tests for Campaign domain models."""
import pytest
from pydantic import ValidationError

from src.domain.models.campaign import Campaign, Product, BrandGuidelines


class TestBrandGuidelines:
    """Test BrandGuidelines model."""

    def test_valid_brand_guidelines(self):
        """Test creating valid brand guidelines."""
        guidelines = BrandGuidelines(
            primary_color="#FF5733",
            secondary_color="#33FF57",
            logo_required=True,
            font_family="Arial"
        )
        assert guidelines.primary_color == "#FF5733"
        assert guidelines.secondary_color == "#33FF57"
        assert guidelines.logo_required is True
        assert guidelines.font_family == "Arial"

    def test_optional_fields(self):
        """Test that all fields have defaults."""
        guidelines = BrandGuidelines()
        assert guidelines.primary_color == "#000000"
        assert guidelines.secondary_color is None
        assert guidelines.logo_required is False
        assert guidelines.font_family == "Arial"


class TestProduct:
    """Test Product model."""

    def test_valid_product(self):
        """Test creating valid product."""
        product = Product(
            name="EcoBottle Pro",
            description="Sustainable water bottle with advanced insulation"
        )
        assert product.name == "EcoBottle Pro"
        assert product.description == "Sustainable water bottle with advanced insulation"
        assert product.input_asset is None

    def test_product_with_input_asset(self):
        """Test product with input asset path."""
        product = Product(
            name="EcoBottle Pro",
            description="Sustainable bottle",
            input_asset="assets/bottle.jpg"
        )
        assert product.input_asset == "assets/bottle.jpg"

    def test_product_requires_name(self):
        """Test that product name is required."""
        with pytest.raises(ValidationError) as exc_info:
            Product(description="Test description")
        assert "name" in str(exc_info.value).lower()

    def test_product_requires_description(self):
        """Test that product description is required."""
        with pytest.raises(ValidationError) as exc_info:
            Product(name="Test Product")
        assert "description" in str(exc_info.value).lower()


class TestCampaign:
    """Test Campaign model."""

    def test_valid_campaign(self):
        """Test creating valid campaign."""
        campaign = Campaign(
            campaign_id="summer-2024-eco",
            products=[
                Product(name="Product A", description="Description A"),
                Product(name="Product B", description="Description B")
            ],
            target_market="US",
            target_audience="Millennials",
            campaign_message="Sustainable living for everyone"
        )
        assert campaign.campaign_id == "summer-2024-eco"
        assert len(campaign.products) == 2
        assert campaign.target_market == "US"
        assert campaign.target_audience == "Millennials"
        assert campaign.campaign_message == "Sustainable living for everyone"

    def test_campaign_with_brand_guidelines(self):
        """Test campaign with brand guidelines."""
        campaign = Campaign(
            campaign_id="test",
            products=[
                Product(name="A", description="Description A longer"),
                Product(name="B", description="Description B longer")
            ],
            target_market="US",
            target_audience="Everyone here",
            campaign_message="Test message longer",
            brand_guidelines=BrandGuidelines(
                primary_color="#FF5733",
                logo_required=True
            )
        )
        assert campaign.brand_guidelines.primary_color == "#FF5733"
        assert campaign.brand_guidelines.logo_required is True

    def test_campaign_requires_minimum_two_products(self):
        """Test that campaign requires at least 2 products."""
        with pytest.raises(ValidationError):
            Campaign(
                campaign_id="test",
                products=[Product(name="A", description="Description A longer")],
                target_market="US",
                target_audience="Everyone here",
                campaign_message="Test message longer"
            )

    def test_campaign_requires_campaign_id(self):
        """Test that campaign_id is required."""
        with pytest.raises(ValidationError):
            Campaign(
                products=[
                    Product(name="A", description="Description A longer"),
                    Product(name="B", description="Description B longer")
                ],
                target_market="US",
                target_audience="Everyone here",
                campaign_message="Test message longer"
            )

    def test_campaign_requires_target_market(self):
        """Test that target_market is required."""
        with pytest.raises(ValidationError):
            Campaign(
                campaign_id="test",
                products=[
                    Product(name="A", description="Description A longer"),
                    Product(name="B", description="Description B longer")
                ],
                target_audience="Everyone here",
                campaign_message="Test message longer"
            )

    def test_campaign_requires_target_audience(self):
        """Test that target_audience is required."""
        with pytest.raises(ValidationError):
            Campaign(
                campaign_id="test",
                products=[
                    Product(name="A", description="Description A longer"),
                    Product(name="B", description="Description B longer")
                ],
                target_market="US",
                campaign_message="Test message longer"
            )

    def test_campaign_requires_campaign_message(self):
        """Test that campaign_message is required."""
        with pytest.raises(ValidationError):
            Campaign(
                campaign_id="test",
                products=[
                    Product(name="A", description="Description A longer"),
                    Product(name="B", description="Description B longer")
                ],
                target_market="US",
                target_audience="Everyone here"
            )

    def test_campaign_default_brand_guidelines(self):
        """Test that campaign has default brand guidelines."""
        campaign = Campaign(
            campaign_id="test",
            products=[
                Product(name="A", description="Description A longer"),
                Product(name="B", description="Description B longer")
            ],
            target_market="US",
            target_audience="Everyone here",
            campaign_message="Test message longer"
        )
        assert campaign.brand_guidelines is not None
        assert isinstance(campaign.brand_guidelines, BrandGuidelines)
        assert campaign.brand_guidelines.logo_required is False
