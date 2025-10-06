# Brand Compliance Implementation Estimate

**Status**: Current implementation provides **brand guidelines support** (data capture/validation). This document estimates what would be required for **actual compliance checking/enforcement**.

---

## Current State

### What We Have ✅

**Domain Model** (`src/domain/models/campaign.py`):
```python
class BrandGuidelines(BaseModel):
    primary_color: str = Field(pattern=r"^#[0-9A-Fa-f]{6}$")  # Validates hex format
    secondary_color: Optional[str] = Field(pattern=r"^#[0-9A-Fa-f]{6}$")
    logo_required: bool = Field(default=False)
    font_family: str = Field(default="Arial")
```

**Current Capabilities**:
- ✅ Captures brand guidelines in domain model
- ✅ Validates color format (hex string)
- ✅ Tracks logo requirement (boolean)
- ✅ Uses `primary_color` for text overlay
- ❌ **Does NOT verify** logo is actually present in output
- ❌ **Does NOT validate** colors are used correctly in composition

### Assignment Requirement

> "Brand compliance checks (e.g., presence of logo, use of brand colors)" - **Nice-to-have bonus feature**

**Our Approach**: Positioned as foundation for future compliance, not full implementation.

---

## Implementation Estimate for ACTUAL Compliance Checking

### 1. Logo Presence Validation

**Requirement**: Verify generated campaign asset contains the required logo

**Technical Approach**:

**Option A: Template Matching (Simple)**
```python
# src/application/services/compliance_checker.py

class LogoValidator:
    def __init__(self, logo_template_path: str):
        self.logo_template = cv2.imread(logo_template_path, cv2.IMREAD_UNCHANGED)

    def validate_logo_presence(self, image_path: str, threshold: float = 0.8) -> bool:
        """Check if logo exists in image using template matching."""
        image = cv2.imread(image_path)
        result = cv2.matchTemplate(image, self.logo_template, cv2.TM_CCOEFF_NORMED)
        max_val = cv2.minMaxLoc(result)[1]
        return max_val >= threshold
```

**Dependencies**:
- `opencv-python` for computer vision
- Logo template files (PNG with transparency)
- Threshold tuning for different logo sizes

**Complexity**: **Low-Medium**
- ~2-3 hours implementation
- Straightforward template matching
- Requires logo asset files

**Option B: Azure Computer Vision API (Robust)**
```python
# src/infrastructure/azure_clients/vision_client.py

class AzureVisionClient:
    async def detect_logo(self, image_path: str, brand_logos: List[str]) -> bool:
        """Use Azure Computer Vision Custom Vision to detect brand logos."""
        with open(image_path, "rb") as image_data:
            response = await self.vision_client.detect_objects(image_data)

        detected_objects = [obj.object_property for obj in response.objects]
        return any(logo in detected_objects for logo in brand_logos)
```

**Dependencies**:
- Azure Computer Vision API subscription
- Custom Vision model training (logo dataset)
- Additional API costs

**Complexity**: **Medium-High**
- ~6-8 hours implementation (including model training)
- More robust (handles rotation, scaling, occlusion)
- Requires training dataset

**Recommended**: Option A for POC, Option B for production

---

### 2. Brand Color Validation

**Requirement**: Verify generated assets use brand colors correctly

**Technical Approach**:

**Option A: Dominant Color Extraction (Simple)**
```python
# src/application/services/color_validator.py

from PIL import Image
from sklearn.cluster import KMeans
import numpy as np

class ColorValidator:
    def extract_dominant_colors(self, image_path: str, n_colors: int = 5) -> List[str]:
        """Extract dominant colors from image using k-means clustering."""
        image = Image.open(image_path).convert('RGB')
        pixels = np.array(image).reshape(-1, 3)

        kmeans = KMeans(n_clusters=n_colors, random_state=42)
        kmeans.fit(pixels)

        colors = kmeans.cluster_centers_.astype(int)
        return [self._rgb_to_hex(color) for color in colors]

    def validate_brand_colors(
        self,
        image_path: str,
        brand_colors: List[str],
        tolerance: float = 30.0  # Delta E tolerance
    ) -> bool:
        """Check if brand colors appear in image within tolerance."""
        dominant_colors = self.extract_dominant_colors(image_path)

        for brand_color in brand_colors:
            if not self._color_present(brand_color, dominant_colors, tolerance):
                return False

        return True

    def _color_distance(self, color1: str, color2: str) -> float:
        """Calculate Delta E (perceptual color difference)."""
        # Convert hex to LAB color space, calculate Euclidean distance
        # Delta E < 2.3 = imperceptible difference
        # Delta E 2.3-10 = perceptible but acceptable
        pass
```

**Dependencies**:
- `scikit-learn` for k-means clustering
- `colormath` for Delta E calculation
- Tuning for tolerance thresholds

**Complexity**: **Medium**
- ~4-5 hours implementation
- Handles color variations (shadows, highlights)
- May have false positives if brand color is very common

**Option B: Region-Specific Validation (Robust)**
```python
class RegionColorValidator:
    def validate_color_usage(
        self,
        image_path: str,
        guidelines: BrandGuidelines,
        text_region: Tuple[int, int, int, int]  # x, y, width, height
    ) -> Dict[str, bool]:
        """Validate color usage in specific regions."""
        image = Image.open(image_path)

        # Check text overlay uses primary color
        text_area = image.crop(text_region)
        text_colors = self.extract_dominant_colors(text_area, n_colors=3)
        primary_used = self._color_present(guidelines.primary_color, text_colors)

        # Check secondary color appears somewhere
        full_colors = self.extract_dominant_colors(image_path, n_colors=10)
        secondary_used = self._color_present(guidelines.secondary_color, full_colors)

        return {
            "primary_color_used": primary_used,
            "secondary_color_used": secondary_used
        }
```

**Complexity**: **Medium-High**
- ~6-7 hours implementation
- More accurate (checks specific regions)
- Requires region definitions

**Recommended**: Option A for general compliance, Option B for strict enforcement

---

### 3. Font Compliance Validation

**Requirement**: Verify text uses correct brand font family

**Technical Approach**:
```python
# src/application/services/font_validator.py

import pytesseract
from PIL import Image

class FontValidator:
    def validate_font_family(
        self,
        image_path: str,
        expected_font: str
    ) -> bool:
        """Extract text and attempt to identify font family."""
        # Note: Font detection from images is extremely difficult
        # OCR can extract text but not reliably identify fonts

        # Option 1: Metadata-based (check what we USED, not what's visible)
        # This is what we currently do implicitly

        # Option 2: Visual comparison (compare against reference images)
        # Very unreliable, not recommended

        raise NotImplementedError(
            "Font family detection from images is not reliable. "
            "Recommend validating font BEFORE composition instead."
        )
```

**Recommendation**: **Validate font at composition time, not from final image**
- Already doing this implicitly (we control the font used in `ImageComposer`)
- Font detection from raster images is unreliable
- Better approach: Pre-composition validation

**Complexity**: **N/A** (not recommended for post-processing)

---

### 4. Integration into Pipeline

**Modified Architecture**:

```python
# src/application/services/asset_generator.py

class AssetGenerator:
    def __init__(
        self,
        dalle_client: DALLEClient,
        image_composer: ImageComposer,
        logo_validator: LogoValidator,        # NEW
        color_validator: ColorValidator       # NEW
    ):
        self.dalle_client = dalle_client
        self.image_composer = image_composer
        self.logo_validator = logo_validator
        self.color_validator = color_validator

    async def generate_single_asset(
        self,
        campaign: Campaign,
        product: Product,
        aspect_ratio: AspectRatio
    ) -> Asset:
        """Generate and validate asset for compliance."""
        # 1. Generate base image
        base_image = await self.dalle_client.generate_image(...)

        # 2. Compose with text/logo overlay
        final_image = self.image_composer.compose_asset(
            base_image=base_image,
            text=campaign.adapted_message,
            brand_guidelines=campaign.brand_guidelines
        )

        # 3. VALIDATE COMPLIANCE
        compliance_results = await self._validate_compliance(
            final_image,
            campaign.brand_guidelines
        )

        if not compliance_results["is_compliant"]:
            logger.warning(
                "Asset failed compliance check",
                product=product.name,
                failures=compliance_results["failures"]
            )
            # Option A: Reject asset and regenerate
            # Option B: Flag for manual review
            # Option C: Auto-fix (adjust colors, re-compose)

        return Asset(
            product_name=product.name,
            image_path=final_image,
            compliance_results=compliance_results  # NEW field
        )

    async def _validate_compliance(
        self,
        image_path: str,
        guidelines: BrandGuidelines
    ) -> Dict[str, Any]:
        """Run all compliance checks."""
        results = {
            "is_compliant": True,
            "failures": []
        }

        # Logo check
        if guidelines.logo_required:
            logo_present = self.logo_validator.validate_logo_presence(image_path)
            if not logo_present:
                results["is_compliant"] = False
                results["failures"].append("Logo not detected")

        # Color check
        colors_valid = self.color_validator.validate_brand_colors(
            image_path,
            [guidelines.primary_color, guidelines.secondary_color]
        )
        if not colors_valid:
            results["is_compliant"] = False
            results["failures"].append("Brand colors not detected")

        return results
```

---

## Total Estimation Summary

### Scope 1: Basic Compliance (Logo + Color Detection)

**Features**:
- Logo presence validation (template matching)
- Dominant color extraction and validation
- Integration into asset generation pipeline
- Compliance reporting in output

**Time Estimate**: **12-15 hours**
- Logo validation (template matching): 3 hours
- Color validation (dominant colors + Delta E): 5 hours
- Pipeline integration: 3 hours
- Testing and tuning: 2-4 hours

**Dependencies**:
- `opencv-python` (computer vision)
- `scikit-learn` (k-means clustering)
- `colormath` (color distance calculations)
- Logo template files (PNG with alpha channel)

**Complexity**: **Medium**

---

### Scope 2: Robust Compliance (Azure Computer Vision)

**Features**:
- Azure Custom Vision logo detection (handles rotation/scaling)
- Region-specific color validation
- Advanced compliance reporting
- Auto-retry on failure

**Time Estimate**: **20-25 hours**
- Azure Custom Vision setup + model training: 8 hours
- Logo detection integration: 4 hours
- Region-specific color validation: 6 hours
- Pipeline integration with retry logic: 4 hours
- Testing across scenarios: 3-5 hours

**Dependencies**:
- Azure Computer Vision API subscription
- Logo training dataset (100+ images recommended)
- Additional Azure costs (~$1.50 per 1,000 images)

**Complexity**: **High**

---

## Recommended Approach for POC

**Phase 1: Validation at Composition (Current)**
- ✅ Already implemented: Use `primary_color` in text overlay
- ✅ Already implemented: Font family controlled in `ImageComposer`
- ✅ Already implemented: Pydantic validates color format

**Phase 2: Post-Composition Validation (Scope 1)**
- Add dominant color extraction
- Validate brand colors appear in final asset
- Simple template matching for logo (if required)

**Phase 3: Production Robustness (Scope 2)**
- Azure Computer Vision for logo detection
- Region-specific color validation
- Compliance dashboard

---

## Technical Debt Considerations

### Why We Didn't Implement Full Compliance for This Assignment

1. **Time Constraint**: 2-3 hour assignment window
2. **Bonus Feature**: Marked as "nice-to-have" in requirements
3. **Foundation Over Feature**: Prioritized demonstrating:
   - Clean Architecture (enables easy addition later)
   - Azure ecosystem integration depth
   - Problem-solving (dynamic text fitting, API debugging)
   - Creative technology integration

4. **Honest Positioning**: Documentation claims "brand guidelines support" not "compliance checking"

### How We Positioned It

**Executive Summary**:
> ✓ Brand guidelines support (color validation, logo tracking in domain model)

**README**:
> Clean Architecture allows swapping components without touching domain logic

**Implication**: Foundation is ready for compliance layer addition without refactoring

---

## Code Locations for Implementation

If implementing compliance checking:

1. **Logo Validator**: `src/application/services/logo_validator.py` (NEW)
2. **Color Validator**: `src/application/services/color_validator.py` (NEW)
3. **Integration Point**: `src/application/services/asset_generator.py:L126` (modify `generate_single_asset`)
4. **Domain Extension**: `src/domain/models/asset.py` (add `compliance_results` field)
5. **Tests**: `tests/integration/test_brand_compliance.py` (NEW)

---

## Summary

**Current State**: Brand guidelines **support** (data capture + validation)

**Full Compliance**: Brand guidelines **enforcement** (post-processing verification)

**Estimate**: 12-15 hours (basic) to 20-25 hours (robust)

**Recommendation for POC**: Current approach is appropriate given time constraints and "nice-to-have" status. Foundation supports future extension without refactoring.

---

**Document Version**: 1.0
**Last Updated**: 2025-10-06
**Related Docs**: Technical-Approach.md, Executive-Summary.md
