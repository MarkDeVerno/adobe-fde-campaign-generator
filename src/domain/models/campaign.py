"""
Campaign domain model representing a marketing campaign brief.
"""
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class Product(BaseModel):
    """Product to be featured in campaign."""
    name: str = Field(..., min_length=1, description="Product name")
    description: str = Field(..., min_length=10, description="Product description")
    input_asset: Optional[str] = Field(
        default=None,
        description="Optional path to existing product image (local file or storage path)"
    )

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate product name is not empty after stripping whitespace."""
        if len(v.strip()) == 0:
            raise ValueError("Product name cannot be empty")
        return v.strip()


class BrandGuidelines(BaseModel):
    """Brand guidelines for campaign assets."""
    primary_color: str = Field(default="#000000", pattern=r"^#[0-9A-Fa-f]{6}$")
    secondary_color: Optional[str] = Field(default=None, pattern=r"^#[0-9A-Fa-f]{6}$")
    logo_required: bool = Field(default=False)
    font_family: str = Field(default="Arial")


class Campaign(BaseModel):
    """Marketing campaign brief."""
    campaign_id: str = Field(..., min_length=1)
    products: List[Product] = Field(..., min_length=2, description="At least 2 products required")
    target_market: str = Field(..., min_length=2)
    target_audience: str = Field(..., min_length=10)
    campaign_message: str = Field(..., min_length=10, max_length=500)
    brand_guidelines: BrandGuidelines = Field(default_factory=BrandGuidelines)

    @field_validator('products')
    @classmethod
    def validate_products(cls, v: List[Product]) -> List[Product]:
        """Validate campaign has at least 2 products."""
        if len(v) < 2:
            raise ValueError("Campaign requires at least 2 products")
        return v

    @field_validator('campaign_message')
    @classmethod
    def validate_message(cls, v: str) -> str:
        """Validate campaign message has at least 10 characters after stripping whitespace."""
        if len(v.strip()) < 10:
            raise ValueError("Campaign message must be at least 10 characters")
        return v.strip()
