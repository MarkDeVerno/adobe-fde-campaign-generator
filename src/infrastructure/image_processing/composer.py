"""
Image composition service using Pillow for text overlay and resizing.
"""
from PIL import Image, ImageDraw, ImageFont
from typing import Tuple, Optional
import os
import textwrap
import structlog

from src.domain.models.asset import AspectRatio

logger = structlog.get_logger()


class ImageComposer:
    """Service for composing campaign images with text overlays."""

    def __init__(self, font_path: str = None, font_size: int = 48):
        """
        Initialize image composer.

        Args:
            font_path: Path to TrueType font file (None uses default)
            font_size: Default font size for campaign message
        """
        self.default_font_size = font_size
        self.font_path = None  # Will store the path to loaded font
        self.use_default_font = False

        # Try to load custom font, fall back to default
        try:
            if font_path and os.path.exists(font_path):
                self.font_path = font_path
                self.font = ImageFont.truetype(font_path, self.default_font_size)
                logger.info("Loaded custom font", path=font_path)
            else:
                # Try common system fonts (prefer multi-language fonts for localization)
                font_loaded = False
                for font_name in [
                    # Multi-language fonts (CJK + Arabic + Latin support)
                    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",  # Linux - Noto Sans CJK
                    "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",  # Linux - Noto Sans CJK alt
                    "/usr/share/fonts/truetype/noto/NotoSansArabic-Bold.ttf",  # Linux - Noto Sans Arabic (RTL)
                    "/usr/share/fonts/truetype/noto/NotoNaskhArabic-Bold.ttf",  # Linux - Noto Naskh Arabic
                    "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",  # Linux - Droid (multi-lang)
                    "/System/Library/Fonts/PingFang.ttc",  # macOS - PingFang (CJK)
                    "/System/Library/Fonts/GeezaPro.ttc",  # macOS - Geeza Pro (Arabic)
                    "C:\\Windows\\Fonts\\msyh.ttc",  # Windows - Microsoft YaHei (CJK)
                    "C:\\Windows\\Fonts\\tahoma.ttf",  # Windows - Tahoma (Arabic support)
                    # Fallback to Latin-only fonts
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux - Latin
                    "/System/Library/Fonts/Helvetica.ttc",  # macOS - Latin
                    "C:\\Windows\\Fonts\\arial.ttf"  # Windows - Latin
                ]:
                    if os.path.exists(font_name):
                        self.font_path = font_name
                        self.font = ImageFont.truetype(font_name, self.default_font_size)
                        font_loaded = True
                        logger.info("Loaded system font", path=font_name, size=self.default_font_size)
                        break

                if not font_loaded:
                    # Fall back to default PIL font with size
                    self.use_default_font = True
                    self.font = ImageFont.load_default(size=self.default_font_size)
                    logger.warning("Using default PIL font (limited quality)", size=self.default_font_size)
        except Exception as e:
            logger.warning("Failed to load font, using default", error=str(e))
            self.use_default_font = True
            # Use modern load_default with size parameter (Pillow 10.0+)
            try:
                self.font = ImageFont.load_default(size=self.default_font_size)
            except TypeError:
                # Fallback for older Pillow versions
                self.font = ImageFont.load_default()
                logger.warning("Using legacy default font (no size support)")

    def resize_image(self, image: Image.Image, aspect_ratio: AspectRatio) -> Image.Image:
        """
        Resize image to match aspect ratio dimensions.

        Args:
            image: Source image
            aspect_ratio: Target aspect ratio

        Returns:
            Resized image
        """
        target_width, target_height = aspect_ratio.dimensions

        # Resize with high-quality Lanczos resampling
        resized = image.resize(
            (target_width, target_height),
            Image.Resampling.LANCZOS
        )

        logger.info(
            "Resized image",
            from_size=image.size,
            to_size=resized.size,
            aspect_ratio=aspect_ratio.value
        )

        return resized

    def _load_font_at_size(self, size: int) -> ImageFont.FreeTypeFont:
        """
        Load font at specified size.

        Args:
            size: Font size in points

        Returns:
            Font object at specified size
        """
        if self.use_default_font:
            try:
                return ImageFont.load_default(size=size)
            except TypeError:
                return ImageFont.load_default()
        elif self.font_path:
            return ImageFont.truetype(self.font_path, size)
        else:
            return ImageFont.load_default()

    def _calculate_optimal_font_size(
        self,
        text: str,
        max_width: int,
        max_height: int,
        max_font_size: int = 60,
        min_font_size: int = 16
    ) -> Tuple[ImageFont.FreeTypeFont, str]:
        """
        Calculate optimal font size to fit text within bounds.
        Supports multi-line text wrapping if needed.

        Args:
            text: Text to fit
            max_width: Maximum width in pixels
            max_height: Maximum height in pixels
            max_font_size: Maximum font size to try
            min_font_size: Minimum font size fallback

        Returns:
            Tuple of (optimal_font, wrapped_text)
        """
        # Start with maximum font size and decrease until text fits
        for size in range(max_font_size, min_font_size - 1, -2):
            font = self._load_font_at_size(size)

            # Try without wrapping first
            dummy_draw = ImageDraw.Draw(Image.new('RGB', (1, 1)))
            bbox = dummy_draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            if text_width <= max_width and text_height <= max_height:
                logger.info(
                    "Found optimal font size (single line)",
                    size=size,
                    text_width=text_width,
                    text_height=text_height,
                    max_width=max_width,
                    max_height=max_height
                )
                return font, text

            # Try with text wrapping
            # Estimate characters per line based on average character width
            avg_char_width = text_width / len(text) if len(text) > 0 else 10
            chars_per_line = int(max_width / avg_char_width) if avg_char_width > 0 else 40

            # Wrap text
            wrapped_lines = textwrap.wrap(text, width=max(chars_per_line, 10))
            wrapped_text = '\n'.join(wrapped_lines)

            # Measure wrapped text
            bbox = dummy_draw.textbbox((0, 0), wrapped_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            if text_width <= max_width and text_height <= max_height:
                logger.info(
                    "Found optimal font size (multi-line)",
                    size=size,
                    lines=len(wrapped_lines),
                    text_width=text_width,
                    text_height=text_height,
                    max_width=max_width,
                    max_height=max_height
                )
                return font, wrapped_text

        # Fallback to minimum size with wrapping
        font = self._load_font_at_size(min_font_size)
        dummy_draw = ImageDraw.Draw(Image.new('RGB', (1, 1)))
        bbox = dummy_draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        avg_char_width = text_width / len(text) if len(text) > 0 else 10
        chars_per_line = int(max_width / avg_char_width) if avg_char_width > 0 else 40
        wrapped_lines = textwrap.wrap(text, width=max(chars_per_line, 10))
        wrapped_text = '\n'.join(wrapped_lines)

        logger.warning(
            "Using minimum font size",
            size=min_font_size,
            text_length=len(text)
        )
        return font, wrapped_text

    def add_text_overlay(
        self,
        image: Image.Image,
        text: str,
        position: str = "bottom",
        text_color: str = "#FFFFFF",
        background_color: str = "#000000",
        background_opacity: int = 180
    ) -> Image.Image:
        """
        Add text overlay to image with dynamic font sizing.
        Automatically reduces font size and wraps text to fit within image bounds.

        Args:
            image: Source image
            text: Campaign message text
            position: Text position (top, bottom, center)
            text_color: Text color in hex
            background_color: Background bar color in hex
            background_opacity: Background opacity (0-255)

        Returns:
            Image with text overlay
        """
        # Debug logging
        logger.info("Adding text overlay", text=text[:100], text_len=len(text))

        # Create a copy to avoid modifying original
        img_with_text = image.copy()
        draw = ImageDraw.Draw(img_with_text)

        # Calculate available space
        img_width, img_height = img_with_text.size
        padding = 20

        # Reserve 25% of image height for text overlay (max)
        max_text_height = int(img_height * 0.25)
        # Use 90% of image width for text (leaving margins)
        max_text_width = int(img_width * 0.9)

        # Calculate optimal font size and wrapped text
        optimal_font, wrapped_text = self._calculate_optimal_font_size(
            text=text,
            max_width=max_text_width,
            max_height=max_text_height - (padding * 2),  # Account for padding
            max_font_size=60,
            min_font_size=16
        )

        # Measure actual text dimensions with optimal font
        bbox = draw.textbbox((0, 0), wrapped_text, font=optimal_font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Calculate background bar height
        bar_height = text_height + (padding * 2)

        # Calculate position
        if position == "bottom":
            bar_y = img_height - bar_height
        elif position == "top":
            bar_y = 0
        else:  # center
            bar_y = (img_height - bar_height) // 2

        # Draw semi-transparent background bar
        bg_color = self._hex_to_rgba(background_color, background_opacity)
        draw.rectangle(
            [(0, bar_y), (img_width, bar_y + bar_height)],
            fill=bg_color
        )

        # Calculate text position (centered horizontally)
        text_x = (img_width - text_width) // 2
        text_y = bar_y + padding

        # Draw text
        fg_color = self._hex_to_rgb(text_color)
        draw.text((text_x, text_y), wrapped_text, font=optimal_font, fill=fg_color)

        logger.info(
            "Added text overlay",
            text_length=len(text),
            wrapped_lines=wrapped_text.count('\n') + 1,
            position=position,
            text_size=(text_width, text_height),
            font_size=optimal_font.size if hasattr(optimal_font, 'size') else "unknown"
        )

        return img_with_text

    @staticmethod
    def _hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    @staticmethod
    def _hex_to_rgba(hex_color: str, alpha: int = 255) -> Tuple[int, int, int, int]:
        """Convert hex color to RGBA tuple."""
        rgb = ImageComposer._hex_to_rgb(hex_color)
        return (*rgb, alpha)
