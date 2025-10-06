# Adobe FDE Campaign Generator

> AI-powered marketing campaign asset generator using Azure OpenAI (DALL-E 3, GPT-4o) and Azure AI Services

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Azure](https://img.shields.io/badge/azure-openai-0078D4.svg)](https://azure.microsoft.com/en-us/products/ai-services/openai-service)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## Overview

This project demonstrates enterprise-grade AI orchestration for marketing campaign generation. It showcases:

- **Clean Architecture** with clear separation of concerns (Domain, Application, Infrastructure)
- **Azure AI Integration** using OpenAI (DALL-E 3, GPT-4o), Content Safety, and Translator APIs
- **AI Message Adaptation** for culturally relevant campaign messaging
- **Async Concurrency** for high-performance batch image generation
- **Compliance-First Design** with automated content moderation
- **Extensibility Path** for Claude Code enhancement and n8n automation

## Features

### Core Capabilities

✅ **AI-Powered Message Adaptation**
- GPT-4o adapts campaign messages for target market/audience
- Cultural relevance and local resonance optimization
- Saves adaptation rationale to markdown file
- Example: "Power your day" → "Recharge smarter with eco-tech innovation" (APAC millennials)

✅ **Multi-Product Campaign Generation**
- Generate 2+ product assets per campaign
- Support for multiple aspect ratios (1:1, 9:16, 16:9)
- Batch processing with async concurrency
- Accept input assets or generate with DALL-E

✅ **Azure Content Safety Integration**
- Automated content moderation for campaign messages
- Custom blocklist support (prohibited advertising terms)
- Severity scoring across Hate, Violence, Sexual, Self-Harm categories

✅ **Professional Image Composition**
- AI-generated base images (DALL-E 3) or user-provided photos
- Text overlay with translated campaign messages
- Multiple aspect ratio support
- High-quality image processing (Pillow)

✅ **Clean Architecture Design**
- Domain-driven design with Pydantic models
- Service-oriented application layer
- Infrastructure abstraction for testability
- Type-safe with Python 3.11+ features

### Bonus Features

🎁 **Translation Support**
- Azure Translator API integration
- Market-based language detection (APAC → Chinese/Japanese)
- Seamless pipeline: Base → Adapted → Translated → Applied

🎁 **Input Asset Support**
- Accept user-provided product photos from local filesystem
- Automatic resizing to target aspect ratios
- Graceful fallback to DALL-E generation
- Example: `input_asset: "assets/product-photos/bottle.jpg"`

🎁 **Local Asset Reuse**
- Caches generated images locally
- Reuses existing assets across campaigns
- Reduces API costs and generation time

🎁 **Comprehensive Logging**
- Structured logging with `structlog`
- Detailed operation tracking
- Error handling with context

🎁 **Enhanced CLI Output**
- Message adaptation pipeline visualization
- Translation flow display (Base → Adapted → Translated)
- Asset composition progress tracking
- Validation and error reporting

## Prerequisites

### Required Accounts & Subscriptions

- **Azure Subscription** with available credits
- **Azure OpenAI** access (DALL-E 3 and GPT-4o models)
- **Azure AI Content Safety** resource
- **Azure Translator** resource (optional - for multi-language campaigns)
- **Python 3.11+** installed locally
- **Git** for version control

### Azure Resource Setup

1. **Azure OpenAI** (East US or similar region with DALL-E 3 and GPT-4o)
   - Deploy `dall-e-3` model for image generation
   - Deploy `gpt-4o` model for message adaptation
   - Obtain API key and endpoint

2. **Azure AI Content Safety** (any region)
   - Create resource
   - Configure custom blocklist (optional)
   - Obtain API key and endpoint

3. **Azure Translator** (optional - East US or similar region)
   - Create resource for multi-language campaign support
   - Obtain API key and region
   - If not configured, campaigns remain in original language

> See [Setup Guide](#installation) below for detailed Azure configuration steps

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/[your-username]/adobe-fde-campaign-generator.git
cd adobe-fde-campaign-generator
```

### 2. Create Virtual Environment

```bash
# Create venv
python3.11 -m venv venv

# Activate (Linux/macOS)
source venv/bin/activate

# Activate (Windows PowerShell)
# venv\Scripts\Activate.ps1

# Activate (Windows CMD)
# venv\Scripts\activate.bat
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Install Multi-Language Font Support (Required for Localization)

For localized campaigns (Chinese, Japanese, Arabic, etc.), install multi-language fonts:

**Linux (Ubuntu/Debian)**:
```bash
sudo apt-get update
sudo apt-get install -y fonts-noto-cjk fonts-noto-core
```

**macOS**:
```bash
# CJK and Arabic fonts pre-installed with system
# No additional installation required
```

**Windows**:
```powershell
# CJK fonts (Microsoft YaHei) and Arabic fonts (Tahoma) pre-installed
# No additional installation required
```

**Font Fallback Behavior**:
- **First priority**: Noto Sans CJK (supports Chinese, Japanese, Korean)
- **Second priority**: Noto Sans Arabic (supports Arabic, RTL languages)
- **Fallback**: DejaVu Sans (Latin characters only - translated text shows as boxes)

**Verification**:
```bash
# Check if CJK fonts are installed (Linux)
fc-list | grep -i "noto.*cjk"

# If no output, campaigns with Chinese/Japanese translations will show boxes instead of text
```

> **Note**: If you skip font installation, English-only campaigns will work fine. Multi-language campaigns will generate successfully but translated text overlays will display as empty boxes.

### 5. Configure Environment Variables

```bash
# Copy template
cp .env.template .env

# Edit .env with your Azure credentials
nano .env
```

**Required `.env` values**:

```bash
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_KEY=your-api-key-here
AZURE_OPENAI_DALLE_DEPLOYMENT_NAME=dall-e-3
AZURE_OPENAI_GPT_DEPLOYMENT_NAME=gpt-4o

# Azure Content Safety Configuration
AZURE_CONTENT_SAFETY_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_CONTENT_SAFETY_KEY=your-api-key-here
AZURE_CONTENT_SAFETY_BLOCKLIST_NAME=prohibited-advertising-terms

# Azure Translator Configuration (Optional - for multi-language campaigns)
AZURE_TRANSLATOR_KEY=your-translator-key-here
AZURE_TRANSLATOR_REGION=eastus
AZURE_TRANSLATOR_ENDPOINT=https://api.cognitive.microsofttranslator.com

# Optional: Logging Level
LOG_LEVEL=INFO
```

## Usage

### Quick Start

```bash
# Generate campaign from sample YAML
./campaign-generator generate -f assets/samples/campaign_example.yaml

# With custom output directory
./campaign-generator generate -f my_campaign.yaml -o outputs/

# Verbose logging
./campaign-generator generate -f my_campaign.yaml -v

# Skip compliance check (faster, but not recommended)
./campaign-generator generate -f my_campaign.yaml --skip-compliance
```

### Campaign YAML Format

Create a YAML file describing your campaign:

```yaml
campaign_id: summer-2024-eco
products:
  - name: EcoBottle Pro
    description: Sustainable water bottle with advanced insulation
    input_asset: "assets/product-photos/ecobottle.jpg"  # Optional: use existing photo
  - name: SolarCharge Mini
    description: Portable solar charger for eco-conscious travelers
    # No input_asset - will be AI-generated with DALL-E

target_market: APAC  # Market drives translation (APAC → Chinese/Japanese)
target_audience: Environmentally conscious millennials aged 25-35
campaign_message: "Make every day Earth Day with sustainable choices"

brand_guidelines:
  primary_color: "#2E7D32"
  secondary_color: "#81C784"
  logo_required: false
  font_family: "Arial"
```

**Message Adaptation Pipeline**:
1. **Base message**: "Make every day Earth Day with sustainable choices"
2. **AI-adapted** (GPT-4o): "Eco-innovation for tomorrow's planet" (APAC millennials)
3. **Translated** (Translator API): "为明天的地球而创新" (Chinese for APAC market)
4. **Applied**: Text overlay on final composed images

### Python API

```python
import asyncio
from src.domain.models.campaign import Campaign, Product
from src.domain.models.asset import AspectRatio
from src.application.services.campaign_orchestrator import CampaignOrchestrator

async def generate_campaign():
    # Create campaign
    campaign = Campaign(
        campaign_id="my-campaign",
        products=[
            Product(name="Product A", description="Description A"),
            Product(name="Product B", description="Description B")
        ],
        target_market="US",
        target_audience="Young professionals",
        campaign_message="Innovative solutions for modern life"
    )

    # Generate assets
    orchestrator = CampaignOrchestrator(output_dir="outputs")
    result = await orchestrator.generate_campaign(
        campaign=campaign,
        aspect_ratios=[AspectRatio.SQUARE, AspectRatio.STORY, AspectRatio.WIDE]
    )

    if result['success']:
        print(f"Generated {len(result['assets'])} assets!")
    else:
        print(f"Errors: {result['errors']}")

asyncio.run(generate_campaign())
```

## Architecture

### Project Structure

```
adobe-fde-campaign-generator/
├── src/
│   ├── domain/                  # Domain models (Pydantic)
│   │   └── models/
│   │       ├── campaign.py      # Campaign, Product, BrandGuidelines
│   │       ├── asset.py         # Asset, AspectRatio
│   │       └── compliance.py    # ComplianceResult
│   ├── application/             # Business logic & orchestration
│   │   └── services/
│   │       ├── campaign_orchestrator.py  # Main pipeline
│   │       ├── asset_generator.py        # Concurrent generation + input assets
│   │       └── compliance_service.py     # Content safety
│   ├── infrastructure/          # External integrations
│   │   ├── azure/
│   │   │   ├── dalle_client.py          # DALL-E 3 API
│   │   │   ├── message_adapter.py       # GPT-4o message adaptation
│   │   │   ├── translator_client.py     # Azure Translator API
│   │   │   └── content_safety_client.py # Content Safety API
│   │   └── image_processing/
│   │       └── composer.py              # Pillow operations
│   └── cli/                     # Command-line interface
│       ├── main.py              # Click commands + message pipeline display
│       └── utils.py             # CLI utilities
├── tests/
│   └── integration/             # Integration tests
│       └── test_campaign_pipeline.py
├── assets/
│   └── samples/                 # Sample campaigns
│       └── campaign_example.yaml
├── outputs/                     # Generated assets + message markdown (gitignored)
├── requirements.txt             # Python dependencies
├── campaign-generator           # CLI executable
└── README.md
```

### Clean Architecture Layers

**Domain Layer** (`src/domain/`)
- Core business models
- No external dependencies
- Pydantic validation

**Application Layer** (`src/application/`)
- Business logic orchestration
- Service coordination
- Depends on domain only

**Infrastructure Layer** (`src/infrastructure/`)
- External API clients
- Image processing
- Depends on domain + application

**Presentation Layer** (`src/cli/`)
- User interface
- CLI commands
- Depends on all layers

### Pipeline Flow

```
1. Load Campaign YAML → Domain Models (Pydantic validation)
2. Validate Business Rules → Application Layer
3. Check Content Safety → Infrastructure (Azure Content Safety)
4. Adapt Message for Market → Infrastructure (GPT-4o)
5. Translate Message → Infrastructure (Azure Translator)
6. Generate/Load Images (concurrent) → Infrastructure (DALL-E 3 or local files)
7. Compose Final Assets with Text → Infrastructure (Pillow + translated message)
8. Return Results → Application Layer
```

**New Pipeline Steps**:
- **Step 4**: GPT-4o adapts campaign message for cultural relevance (saved to markdown)
- **Step 5**: Azure Translator converts adapted message to target language
- **Step 6**: Either loads user-provided `input_asset` or generates with DALL-E 3
- **Step 7**: Applies translated message as text overlay on composed images

## Testing

### Run All Tests

```bash
# Run integration tests
python -m pytest tests/integration/test_campaign_pipeline.py -v

# With coverage report
python -m pytest tests/integration/test_campaign_pipeline.py -v --cov=src --cov-report=html

# Open coverage report
open htmlcov/index.html
```

### Test Coverage

- ✅ YAML loading and validation
- ✅ Compliance checks (mocked Azure Content Safety)
- ✅ Image generation (mocked DALL-E 3)
- ✅ Image composition
- ✅ Asset model validation
- ✅ End-to-end pipeline with error handling

## Performance

### Concurrent Execution

The system uses `asyncio.gather()` for parallel image generation:

```python
# Sequential: ~30 seconds for 6 images (3 products × 3 aspect ratios, 5s each)
# Concurrent: ~5 seconds (limited by API rate limits)
```

### Caching Strategy

- Generated images are cached locally
- Reuses existing assets based on filename
- Reduces API costs by ~80% on repeated campaigns

## Troubleshooting

### Common Issues

**Error: "Azure Content Safety credentials not configured"**
```bash
# Solution: Check .env file has correct values
cat .env | grep AZURE_CONTENT_SAFETY
```

**Error: "Module not found"**
```bash
# Solution: Activate virtual environment
source venv/bin/activate
pip install -r requirements.txt
```

**Error: "API quota exceeded"**
```bash
# Solution: Check Azure OpenAI quota
# Generate fewer images or increase quota in Azure portal
```

## Development

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/integration/test_campaign_pipeline.py

# With verbose output
pytest -v

# With coverage
pytest --cov=src --cov-report=term-missing
```

### Code Quality

```bash
# Type checking
mypy src/ --ignore-missing-imports

# Linting
pylint src/

# Formatting (check only)
black src/ --check

# Formatting (apply)
black src/
```

## Future Enhancements

### Claude Code Integration

This project is designed to be enhanced with Claude Code (Anthropic's AI coding assistant):

**Planned Enhancements**:
- ✨ Automated prompt optimization using Claude
- ✨ Intelligent campaign brief refinement
- ✨ AI-powered quality analysis of generated assets
- ✨ Automated A/B testing configuration generation
- ✨ Natural language campaign editing

**Why Claude Code?**
- Understands codebase context holistically
- Can refactor architecture while maintaining Clean Architecture principles
- Generates type-safe code with comprehensive tests
- Integrates with existing Azure infrastructure

### n8n Workflow Automation

**Visual Workflow Capabilities**:
- 🔄 Scheduled campaign generation
- 🔄 Webhook-triggered asset creation
- 🔄 Multi-platform distribution (Instagram, Facebook, Twitter)
- 🔄 Approval workflows for compliance
- 🔄 Performance analytics integration

## License

MIT License - see [LICENSE](LICENSE) file for details

## Acknowledgments

- **Azure OpenAI** for DALL-E 3 access
- **Azure AI Services** for Content Safety API
- **Anthropic** for Claude Code development workflow
- **n8n** for future workflow automation capabilities

## Contact

For questions or feedback about this project, please open an issue on GitHub.

---

**Built with Clean Architecture principles for Adobe FDE Take-Home Assignment**
