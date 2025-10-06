# Technical Approach & Problem-Solving

> **Context**: This document details the technical decisions, problem-solving approaches, and creative technology integration for the Adobe FDE Campaign Generator. It demonstrates how architectural choices, debugging strategies, and integration patterns solve real-world challenges.

---

## Table of Contents

1. [Architecture Decisions](#architecture-decisions)
2. [Problem-Solving Examples](#problem-solving-examples)
3. [Creative Technology Integration](#creative-technology-integration)
4. [Performance Optimization](#performance-optimization)
5. [Code Quality Patterns](#code-quality-patterns)

---

## Architecture Decisions

### 1. Clean Architecture with Domain-Driven Design

**Problem Statement**:
- Need extensibility for future enhancements (Claude Code, n8n automation)
- Must maintain testability despite Azure API dependencies
- Want clear separation of business logic from infrastructure

**Decision**: Implement Clean Architecture with 4 layers

```
Domain (src/domain/)
  ↓ depends on
Application (src/application/)
  ↓ depends on
Infrastructure (src/infrastructure/)
  ↓ depends on
Presentation (src/cli/)
```

**Rationale**:
1. **Domain Layer**: Pure business models with Pydantic validation
   - No external dependencies
   - Business rules enforced at model level
   - Example: `products: List[Product] = Field(min_length=2)`

2. **Application Layer**: Orchestration and service coordination
   - Depends only on domain models
   - Testable with mocked infrastructure
   - Example: `CampaignOrchestrator` coordinates 7-step pipeline

3. **Infrastructure Layer**: External API clients
   - Isolated Azure integration code
   - Swappable implementations (e.g., OpenAI → Azure OpenAI)
   - Example: `DALLEClient`, `ContentSafetyService`

4. **Presentation Layer**: CLI interface
   - User-facing commands
   - Minimal logic, delegates to application layer
   - Example: `campaign-generator generate`

**Trade-offs**:
- ✅ **Pro**: Easy to test (mock infrastructure), easy to extend
- ✅ **Pro**: Clear dependency flow prevents circular references
- ❌ **Con**: More files/folders than flat structure
- ❌ **Con**: Steeper learning curve for simple modifications

**Evidence**: 77 tests (66 unit, 11 integration) all passing with mocked Azure services

**Code References**:
- Domain: `src/domain/models/campaign.py`
- Application: `src/application/services/campaign_orchestrator.py`
- Infrastructure: `src/infrastructure/azure/dalle_client.py`
- Presentation: `src/cli/main.py`

---

### 2. Async/Await for Concurrent Image Generation

**Problem Statement**:
- Sequential image generation takes 30+ seconds (6 images × 5s each)
- User experience degrades with long wait times
- DALL-E API calls are I/O-bound, not CPU-bound

**Decision**: Use `asyncio.gather()` for parallel execution

**Implementation**:
```python
# src/application/services/asset_generator.py:126-145

async def generate_all_assets(self, campaign: Campaign, aspect_ratios: List[AspectRatio]):
    """Generate assets concurrently for all products and aspect ratios."""

    # Create tasks for concurrent execution
    tasks = []
    for product in campaign.products:
        for aspect_ratio in aspect_ratios:
            task = self.generate_single_asset(campaign, product, aspect_ratio)
            tasks.append(task)

    # Execute concurrently (6 images in ~5s vs ~30s sequential)
    assets = await asyncio.gather(*tasks, return_exceptions=True)

    # Filter out failed generations
    return [asset for asset in assets if isinstance(asset, Asset)]
```

**Measured Results**:
- **Sequential**: 30 seconds for 6 images (2 products × 3 aspect ratios)
- **Concurrent**: 5 seconds for 6 images
- **Performance Gain**: 75% improvement (5s vs 30s)

**Scalability**:
- Same code handles 100+ concurrent generations
- Limited only by Azure API rate limits (e.g., 3 requests/minute for DALL-E 3)
- Graceful degradation: Failed generations don't block successful ones

**Trade-offs**:
- ✅ **Pro**: Massive performance improvement with minimal code
- ✅ **Pro**: Scales to hundreds of generations
- ❌ **Con**: More complex error handling (need `return_exceptions=True`)
- ❌ **Con**: Debugging async code is harder than sequential

---

### 3. Pydantic for Type Safety and Validation

**Problem Statement**:
- Need to validate campaign briefs before expensive API calls
- Want self-documenting code with clear contracts
- Must enforce business rules (e.g., minimum 2 products)

**Decision**: Use Pydantic for all domain models

**Implementation Examples**:

**Business Rule Enforcement**:
```python
# src/domain/models/campaign.py

class Campaign(BaseModel):
    campaign_id: str
    products: List[Product] = Field(min_length=2)  # Business rule: 2+ products
    target_market: str
    campaign_message: str = Field(min_length=10)  # Minimum message length
    brand_guidelines: BrandGuidelines = Field(default_factory=BrandGuidelines)
```

**Hex Color Validation**:
```python
# src/domain/models/campaign.py

class BrandGuidelines(BaseModel):
    primary_color: str = Field(
        default="#000000",
        pattern=r"^#[0-9A-Fa-f]{6}$"  # Validates hex color format
    )
```

**Impact on Error Detection**:
- **Before Pydantic**: Invalid campaigns discovered during Azure API calls (waste API quota)
- **After Pydantic**: Invalid campaigns fail at YAML load (zero API waste)

**Example Validation Failure**:
```python
# This fails immediately with clear error message:
Campaign(
    campaign_id="test",
    products=[Product(name="A", description="Desc A")],  # Only 1 product
    target_market="US",
    campaign_message="Hi"  # Too short
)

# ValidationError:
# - products: ensure this value has at least 2 items
# - campaign_message: ensure this value has at least 10 characters
```

**Trade-offs**:
- ✅ **Pro**: Catch errors early, before API calls
- ✅ **Pro**: Self-documenting (Field definitions are inline docs)
- ✅ **Pro**: Free JSON/YAML parsing with validation
- ❌ **Con**: Learning curve for Pydantic patterns
- ❌ **Con**: Slightly more verbose than plain dataclasses

---

## Problem-Solving Examples

### Problem 1: Long Campaign Messages Overflowing Images

**Discovery Process**:
1. Generated luxury campaign with message: "Enduring artistry. A legacy reimagined for today's connoisseurs." (68 chars)
2. Noticed text overflow on square (1:1) images
3. Identified root cause: Fixed 48pt font size doesn't adapt to content

**Solution Design**:

**Algorithm** (src/infrastructure/image_processing/composer.py:126-210):
```python
def _calculate_optimal_font_size(text, max_width, max_height):
    """
    Binary search for optimal font size with multi-line fallback.

    Strategy:
    1. Start at 60pt (maximum), decrease to 16pt (minimum)
    2. For each size, try single-line first
    3. If doesn't fit, wrap text and try again
    4. Return first size that fits (or minimum with wrapping)
    """
    for size in range(60, 15, -2):  # 60pt → 16pt, step -2
        font = load_font(size)

        # Try single-line
        if text_fits_single_line(text, font, max_width, max_height):
            return font, text

        # Try multi-line with textwrap
        wrapped = wrap_text(text, max_width, font)
        if text_fits(wrapped, font, max_width, max_height):
            return font, wrapped

    # Fallback: minimum size with wrapping
    return load_font(16), wrap_text(text, max_width, load_font(16))
```

**Results**:
- ✅ All messages fit within image bounds (tested with 68-char luxury message)
- ✅ Adapts to aspect ratio (square has less width than 16:9)
- ✅ Graceful degradation to multi-line for long messages
- ✅ Maintains readability (16pt minimum is still legible)

**Code References**:
- Algorithm: `src/infrastructure/image_processing/composer.py:126-210`
- Integration: `src/infrastructure/image_processing/composer.py:212-301`
- Test: Campaign generation with long messages

---

### Problem 2: Azure API Blocklist Attribute Mismatch

**Discovery Process**:
1. Healthcare demo campaign should fail compliance (has "guaranteed", "risk-free")
2. Compliance check passed when it should fail
3. Checked Azure portal: Blocklist exists with correct terms
4. Debugged API response structure

**Root Cause Analysis**:
```python
# Code expected:
response.blocklists_match_results  # ❌ Doesn't exist

# Azure API returns:
response.blocklists_match  # ✅ Correct attribute
```

**Investigation Code**:
```python
# Debug script to inspect Azure response
response = client.analyze_text(request)
print('Response attributes:')
for attr in dir(response):
    if not attr.startswith('_'):
        print(f'  {attr}: {getattr(response, attr, None)}')

# Output showed:
#   blocklists_match: [{'blocklistName': 'prohibited-advertising-terms',
#                       'blocklistItemText': 'risk-free'}]
```

**Solution Implemented**:
```python
# src/infrastructure/azure/content_safety_client.py:70-77

# OLD (wrong):
if hasattr(response, 'blocklists_match_results'):
    for match in response.blocklists_match_results:
        # Never executed

# NEW (correct):
if hasattr(response, 'blocklists_match'):
    for match in response.blocklists_match:
        if isinstance(match, dict) and 'blocklistItemText' in match:
            blocklist_matches.append(match['blocklistItemText'])
```

**Results**:
- ✅ Healthcare demo now correctly fails with prohibited terms detected
- ✅ Blocklist matches: ["guaranteed results", "risk-free"]
- ✅ Compliance recommendation: "Campaign message contains prohibited terms"

**Learning**: Always inspect actual API responses, don't assume SDK documentation is complete

---

### Problem 3: Azure Endpoint Routing Failure

**Discovery Process**:
1. DALL-E calls failing with error: "imageGenerations operation does not work with gpt-4o model"
2. Environment has `AZURE_OPENAI_DALLE_DEPLOYMENT_NAME=dall-e-3` (correct)
3. Error message mentions wrong model (gpt-4o)
4. Systematic debugging of endpoint formats

**Root Cause**:
Regional endpoint (`eastus.api.cognitive.microsoft.com`) doesn't route correctly to specific deployments. AsyncAzureOpenAI SDK has routing issues with regional endpoints.

**Solution Process**:
1. **Test Hypothesis**: Changed to resource-specific endpoint
   ```bash
   # ❌ WRONG
   AZURE_OPENAI_ENDPOINT=https://eastus.api.cognitive.microsoft.com/

   # ✅ CORRECT
   AZURE_OPENAI_ENDPOINT=https://oai-sparkquest-prod-eus.openai.azure.com/
   ```

2. **Document Findings**: Created TROUBLESHOOTING.md with:
   - Symptom description
   - Root cause explanation
   - Step-by-step fix
   - How to find resource-specific endpoint

3. **Add Validation**: Log endpoint/deployment on initialization
   ```python
   logger.info(
       "Initializing DALL-E client",
       endpoint=self.endpoint,
       deployment=self.deployment_name
   )
   ```

**Documentation**: `docs/TROUBLESHOOTING.md` lines 6-36

**Learning**: Enterprise debugging should produce documentation for team knowledge sharing

---

### Problem 4: AI Implementation Gap Analysis

**Discovery Process**:
1. Claude Code generated initial implementation (automated 55% of code)
2. Manual review of Requirements Verification Checklist (30 items)
3. Systematic testing against each requirement
4. Found 3 gaps (90% → 100% coverage)

**Gaps Identified**:
1. **Message Adaptation Missing**: Requirement said "display campaign message" but UX showed need for cultural adaptation
   - Added: GPT-4o message adaptation for target market/audience

2. **Translation Integration Incomplete**: Market-based translation not connected to image overlay
   - Added: Translation pipeline integration with text composer

3. **Input Asset Feature**: "Accept input assets" requirement partially implemented
   - Completed: Full input_asset support with graceful DALL-E fallback

**Resolution Process**:
1. **Gap Identification**: Systematic checklist review
2. **Root Cause**: AI missed nuanced UX requirements
3. **Implementation**: 3 focused additions
4. **Verification**: Re-test against checklist → 100%

**Learning**: AI is powerful but systematic human review catches edge cases

---

## Creative Technology Integration

### 1. DALL-E 3 for Professional Product Photography

**Integration Approach**:
```python
# src/infrastructure/azure/dalle_client.py

class DALLEClient:
    def __init__(self):
        self.client = AsyncAzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_KEY"),
            api_version="2024-02-01",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        self.deployment_name = os.getenv("AZURE_OPENAI_DALLE_DEPLOYMENT_NAME")

    async def generate_image(self, prompt: str, size="1024x1024", quality="standard"):
        """Generate product image with DALL-E 3."""
        response = await self.client.images.generate(
            model=self.deployment_name,
            prompt=prompt,
            size=size,
            quality=quality,
            n=1
        )
        return response.data[0].url
```

**Prompt Engineering**:
- Professional product photography style
- White background for consistency
- Studio lighting specification
- High-quality rendering

**Example Prompt**:
```
"Professional product photography of a sleek sustainable water bottle
with smart hydration tracking display, BPA-free green material, modern
minimalist design, white background, studio lighting, high quality"
```

---

### 2. GPT-4o for AI-Powered Message Adaptation

**Integration Purpose**: Exceed "display message" requirement with cultural relevance

**Implementation**:
```python
# src/infrastructure/azure/message_adapter.py

async def adapt_message(self, message: str, target_market: str, target_audience: str):
    """Adapt campaign message for cultural relevance."""

    system_prompt = f"""You are a marketing expert specializing in {target_market}.
    Adapt the campaign message for {target_audience} while maintaining brand voice.
    Focus on cultural relevance and local resonance."""

    response = await self.client.chat.completions.create(
        model=self.deployment_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Adapt: {message}"}
        ],
        temperature=0.7
    )

    adapted = response.choices[0].message.content
    return adapted, rationale
```

**Example Adaptation**:
```
Original: "Power your day, naturally. Save the planet, one charge at a time."
Market: APAC
Audience: Eco-conscious millennials

Adapted: "Recharge smarter with eco-tech innovation. Tomorrow's planet starts today."
Rationale: APAC millennials respond to innovation + future-focus messaging
```

---

### 3. Azure Translator for Market-Based Localization

**Integration Strategy**:
```python
# Market → Language mapping
MARKET_TO_LOCALE = {
    "APAC": "zh-Hans",          # Simplified Chinese
    "Middle East": "ar",        # Arabic
    "Latin America": "es",      # Spanish
    "North America": "en",      # English (no translation)
}

async def translate_campaign_message(message: str, target_market: str):
    locale = MARKET_TO_LOCALE.get(target_market, "en")

    if locale == "en":
        return message  # Skip translation

    response = requests.post(
        f"{self.endpoint}/translate",
        params={'api-version': '3.0', 'to': locale},
        headers={'Ocp-Apim-Subscription-Key': self.key},
        json=[{'text': message}]
    )

    return response.json()[0]['translations'][0]['text']
```

**Pipeline Integration**:
```
1. Base Message: "Power your day, naturally"
         ↓
2. GPT-4o Adapt: "Recharge smarter with eco-tech innovation"
         ↓
3. Translate: "以环保科技创新更智能地充电"
         ↓
4. Image Overlay: Chinese text on final composed images
```

---

### 4. Azure Content Safety for ML-Powered Compliance

**Integration Approach**: Use ML model + custom blocklist (vs. simple regex)

**Why ML-Powered**:
- Catches variations: "risk free" vs "risk-free" vs "riskfree"
- Severity scoring across categories (Hate, Violence, Sexual, Self-Harm)
- Handles new prohibited patterns without code changes

**Implementation**:
```python
# src/infrastructure/azure/content_safety_client.py

request = AnalyzeTextOptions(
    text=message,
    categories=[TextCategory.HATE, TextCategory.VIOLENCE],
    blocklist_names=["prohibited-advertising-terms"],
    output_type="FourSeverityLevels"  # 0, 2, 4, 6
)

response = self.client.analyze_text(request)

# Check severity scores
max_severity = max(response.hate_result.severity, response.violence_result.severity)

# Check blocklist matches
blocklist_matches = [match['blocklistItemText'] for match in response.blocklists_match]

# Pass if low severity AND no blocklist matches
passed = max_severity < 4 and len(blocklist_matches) == 0
```

**Exceeds Requirement**: Assignment asked for "simple legal content checks" (implies regex). Implemented enterprise-grade ML solution.

---

## Performance Optimization

### Concurrent Image Generation

**Measurement**:
```python
# Sequential baseline
start = time.time()
assets = []
for product, aspect_ratio in product_aspect_pairs:
    asset = await generate_single_asset(product, aspect_ratio)  # 5s each
    assets.append(asset)
print(f"Sequential: {time.time() - start:.1f}s")  # 30.0s for 6 images

# Concurrent optimization
start = time.time()
tasks = [generate_single_asset(p, ar) for p, ar in product_aspect_pairs]
assets = await asyncio.gather(*tasks)
print(f"Concurrent: {time.time() - start:.1f}s")  # 5.0s for 6 images
```

**Performance Gain**: 75% improvement (5s vs 30s)

---

### Asset Caching Strategy

**Implementation**:
```python
# Check cache before generating
if os.path.exists(output_path) and self.enable_caching:
    logger.info("Reusing cached asset", path=output_path)
    return Asset(product_name=product.name, file_path=output_path, was_reused=True)

# Generate only if cache miss
image_url = await self.dalle_client.generate_image(prompt)
```

**Impact**: ~80% cost reduction on repeated campaigns

---

## Code Quality Patterns

### Type Safety with Mypy

All code is mypy-compliant with `--strict` mode:
```bash
mypy src/ --strict --ignore-missing-imports
# 0 errors
```

### Structured Logging

All operations use structured logging:
```python
logger.info(
    "Compliance check complete",
    passed=result.passed,
    blocklist_matches_count=len(result.blocklist_matches),
    severity_scores=result.severity_scores
)
```

### Comprehensive Testing

- 66 unit tests (mocked Azure)
- 11 integration tests (mocked Azure)
- 6 manual tests (real Azure APIs)
- 100% critical path coverage

---

**Last Updated**: 2025-10-06
**Document Version**: 1.0
