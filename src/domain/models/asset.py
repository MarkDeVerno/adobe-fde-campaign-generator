"""
Asset domain model representing generated campaign assets.
"""
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class AspectRatio(str, Enum):
    """Supported aspect ratios for campaign assets."""
    SQUARE = "1:1"
    STORY = "9:16"
    WIDE = "16:9"

    @property
    def dimensions(self) -> tuple[int, int]:
        """Get pixel dimensions for aspect ratio."""
        mapping = {
            "1:1": (1024, 1024),
            "9:16": (1024, 1792),
            "16:9": (1792, 1024)
        }
        return mapping[self.value]


class Asset(BaseModel):
    """Generated campaign asset."""
    product_name: str
    aspect_ratio: AspectRatio
    file_path: str
    generated_at: datetime = Field(default_factory=datetime.now)
    was_reused: bool = Field(default=False, description="Whether asset was reused from local storage")
    generation_prompt: Optional[str] = Field(default=None)
