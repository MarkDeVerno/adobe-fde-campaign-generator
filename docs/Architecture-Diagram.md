# Architecture Diagrams

This document provides visual representations of the system architecture, data flows, and integration patterns.

---

## System Architecture (Clean Architecture)

```mermaid
graph TB
    subgraph Presentation["🎯 Presentation Layer"]
        CLI[CLI Interface<br/>campaign_generator.py]
    end

    subgraph Application["⚙️ Application Layer"]
        CampaignService[Campaign Service<br/>Orchestration]
        AssetGenerator[Asset Generator<br/>Async Execution]
        ComplianceChecker[Compliance Checker<br/>Content Safety]
        MessageAdapter[Message Adapter<br/>GPT-4o Integration]
    end

    subgraph Domain["🏛️ Domain Layer"]
        Campaign[Campaign Model<br/>Business Rules]
        Product[Product Model]
        Asset[Asset Model]
        BrandGuidelines[Brand Guidelines<br/>Validation]
    end

    subgraph Infrastructure["🔧 Infrastructure Layer"]
        DALLEClient[DALL-E 3 Client]
        GPTClient[GPT-4o Client]
        SafetyClient[Content Safety Client]
        TranslatorClient[Translator Client]
        ImageComposer[Image Composer<br/>PIL/Pillow]
    end

    CLI --> CampaignService
    CampaignService --> Campaign
    CampaignService --> AssetGenerator
    CampaignService --> ComplianceChecker

    AssetGenerator --> Product
    AssetGenerator --> Asset
    AssetGenerator --> DALLEClient
    AssetGenerator --> ImageComposer
    AssetGenerator --> MessageAdapter

    MessageAdapter --> GPTClient
    MessageAdapter --> TranslatorClient

    ComplianceChecker --> SafetyClient

    Campaign --> BrandGuidelines

    style Presentation fill:#e1f5ff
    style Application fill:#fff4e1
    style Domain fill:#f0e1ff
    style Infrastructure fill:#e1ffe1
```

---

## Data Flow Pipeline

```mermaid
flowchart LR
    subgraph Input
        YAML[Campaign YAML<br/>products, message,<br/>target market]
    end

    subgraph Validation
        Pydantic[Pydantic Models<br/>Type Safety +<br/>Business Rules]
    end

    subgraph Generation["Concurrent Generation (asyncio.gather)"]
        DALLE[DALL-E 3<br/>Product Images]
        Adapt[GPT-4o<br/>Message Adaptation]
        Translate[Azure Translator<br/>Localization]
    end

    subgraph Compliance
        Safety[Content Safety API<br/>Compliance Check]
    end

    subgraph Composition
        Overlay[Image Composer<br/>Text Overlay +<br/>Dynamic Sizing]
    end

    subgraph Output
        PNG[Final Campaign Assets<br/>output/*.png]
        Report[Campaign Report<br/>JSON + Metadata]
    end

    YAML --> Pydantic
    Pydantic --> DALLE
    Pydantic --> Adapt

    Adapt --> Translate
    Translate --> Safety

    DALLE --> Overlay
    Safety --> Overlay

    Overlay --> PNG
    Overlay --> Report

    style Input fill:#e1f5ff
    style Validation fill:#fff4e1
    style Generation fill:#f0e1ff
    style Compliance fill:#ffe1e1
    style Composition fill:#e1ffe1
    style Output fill:#e1f5ff
```

---

## Message Adaptation Pipeline

```mermaid
sequenceDiagram
    participant Campaign
    participant MessageAdapter
    participant GPT4o as GPT-4o API
    participant Translator as Azure Translator
    participant ImageComposer

    Campaign->>MessageAdapter: Base message +<br/>target audience

    MessageAdapter->>GPT4o: Adapt message for<br/>cultural relevance
    Note over GPT4o: "Make culturally relevant<br/>for APAC, maintain tone"
    GPT4o-->>MessageAdapter: Adapted message

    MessageAdapter->>Translator: Detect market language<br/>(APAC → Chinese)
    Translator-->>MessageAdapter: Translated message

    MessageAdapter->>ImageComposer: Final message +<br/>brand colors

    ImageComposer->>ImageComposer: Calculate optimal<br/>font size (60pt → 16pt)
    ImageComposer->>ImageComposer: Apply text wrapping<br/>if needed

    ImageComposer-->>Campaign: Branded image with<br/>localized message
```

---

## Async Concurrency Model

```mermaid
graph LR
    subgraph Sequential["❌ Sequential Approach (30s)"]
        S1[Product 1<br/>Aspect 1:1<br/>5s] --> S2[Product 1<br/>Aspect 16:9<br/>5s]
        S2 --> S3[Product 1<br/>Aspect 4:5<br/>5s]
        S3 --> S4[Product 2<br/>Aspect 1:1<br/>5s]
        S4 --> S5[Product 2<br/>Aspect 16:9<br/>5s]
        S5 --> S6[Product 2<br/>Aspect 4:5<br/>5s]
    end

    subgraph Concurrent["✅ Async/Await (5s) - asyncio.gather()"]
        direction TB
        C1[Product 1, Aspect 1:1]
        C2[Product 1, Aspect 16:9]
        C3[Product 1, Aspect 4:5]
        C4[Product 2, Aspect 1:1]
        C5[Product 2, Aspect 16:9]
        C6[Product 2, Aspect 4:5]
    end

    style Sequential fill:#ffe1e1
    style Concurrent fill:#e1ffe1
```

**Performance**: 75% reduction in execution time (5s vs 30s for 6 images)

---

## Azure Services Integration

```mermaid
graph TB
    subgraph Application["Campaign Generator Application"]
        App[Python Application<br/>Clean Architecture]
    end

    subgraph Azure["Azure AI Services"]
        DALLE[DALL-E 3<br/>Image Generation<br/>eastus endpoint]
        GPT[GPT-4o<br/>Message Adaptation<br/>eastus endpoint]
        Safety[Content Safety<br/>Compliance Checking<br/>eastus endpoint]
        Translator[Translator API<br/>Localization<br/>global endpoint]
    end

    subgraph Output["Generated Assets"]
        Images[Product Images<br/>1024x1024,<br/>1792x1024,<br/>1024x1792]
        Metadata[Campaign Metadata<br/>Compliance Results<br/>Translations]
    end

    App -->|Prompt Engineering| DALLE
    App -->|Cultural Adaptation| GPT
    App -->|Safety Check| Safety
    App -->|Market Localization| Translator

    DALLE --> Images
    GPT --> Metadata
    Safety --> Metadata
    Translator --> Metadata

    style Application fill:#e1f5ff
    style Azure fill:#f0e1ff
    style Output fill:#e1ffe1
```

---

## Key Architecture Decisions

### Clean Architecture Benefits
1. **Domain Independence**: Business rules (Campaign, Product) don't depend on Azure APIs
2. **Testability**: Can mock infrastructure layer for fast unit tests
3. **Flexibility**: Can swap DALL-E for Midjourney without changing domain logic

### Async/Await Performance
- **Before**: Sequential image generation = 6 × 5s = 30s
- **After**: Concurrent with `asyncio.gather()` = max(5s) = 5s
- **Impact**: 75% reduction in execution time

### Type Safety with Pydantic
```python
# Domain model enforces business rules at the boundary
class Campaign(BaseModel):
    products: List[Product] = Field(min_length=2)  # ≥2 products required
    campaign_message: str = Field(min_length=10)   # ≥10 chars required
    brand_guidelines: BrandGuidelines              # Type-safe color validation
```

---

## Integration Points

| Component | Technology | Purpose | Performance |
|-----------|-----------|---------|-------------|
| **Image Generation** | DALL-E 3 | Professional product photography | 5s per image |
| **Message Adaptation** | GPT-4o | Cultural relevance | 1-2s per message |
| **Compliance** | Content Safety API | ML-powered safety checks | <1s per check |
| **Localization** | Azure Translator | Market-based translation | <1s per translation |
| **Composition** | PIL/Pillow | Image overlay + text fitting | <100ms per image |

**Total Pipeline**: ~5-7 seconds for 6 fully localized, compliant campaign assets

---

**Document Version**: 1.0
**Last Updated**: 2025-10-06
**Related Docs**: Technical-Approach.md, README.md
