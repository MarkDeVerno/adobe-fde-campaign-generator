# Adobe FDE Take-Home Assignment - Strategy Document

**Author**: Mark (Antimatter Tech)
**Date**: 2025-10-05
**Purpose**: High-level strategy for Adobe Forward Deployed Engineer take-home assignment
**Status**: ✅ Approved

---

## Executive Summary

**Recommended Approach**: Standalone Python CLI with Clean Architecture + Azure AI Services

**Key Differentiators**:
- ✅ Azure Content Safety API (ML-powered compliance vs. simple regex)
- ✅ Clean architecture demonstrating enterprise thinking
- ✅ Async concurrency for performance optimization
- ✅ Documented Claude Code enhancement path (innovation without breaking requirements)
- ✅ Integration-ready design (workflow automation examples)

**Time Budget**: 2-3 hours implementation + 25 min demo video = **~3.5 hours total**

**Risk Level**: 🟢 **LOW** - Proven tech stack, clear fallback plans, appropriate scope

---

## Section 1: Approach Analysis

### ✅ Approach A: Python CLI with Pillow + Azure AI Services ⭐ RECOMMENDED

**Tech Stack:**
- Python 3.11+ (async/await support)
- Azure OpenAI SDK (DALL-E 3 integration)
- Azure Content Safety API (text moderation)
- Pillow (PIL) for image composition
- Pydantic for data validation
- Click for CLI interface
- PyYAML for campaign brief parsing

**Alignment with Requirements:**
- ✅ **Core Requirements**: 100% coverage
- ✅ **Bonus Features**: Content Safety API, brand compliance, structured logging
- ✅ **Standalone**: Pure Python, no Claude dependency
- ✅ **Local Execution**: Adobe can clone repo and run immediately

**Skill Showcase Potential:** ⭐⭐⭐⭐⭐
- Azure AI ecosystem integration (DALL-E + Content Safety)
- Clean Architecture with DDD patterns
- Async programming for concurrent operations
- Type-safe domain models (Pydantic)
- Professional CLI with comprehensive documentation

**Implementation Speed:** ⭐⭐⭐⭐⭐
- 2-3 hours achievable with buffer time
- Well-documented libraries, minimal learning curve
- Can leverage Claude Code for boilerplate generation

**Code Quality:** ⭐⭐⭐⭐⭐
- Natural separation of concerns (domain/application/infrastructure layers)
- Easy to write clean, testable functions
- Type hints + Pydantic = self-documenting code
- Demonstrates SOLID principles

**Demo Impact:** ⭐⭐⭐⭐⭐
- Clean CLI output shows professionalism
- Real-time image generation is visually satisfying
- Architecture diagram demonstrates enterprise thinking
- Azure AI integration aligns with Adobe's cloud partnerships

**Risk Level:** 🟢 **LOW**
- Mature, stable libraries
- Python expertise from Fusion platform experience
- Azure AI access confirmed
- Clear fallback plans for each component

---

### ❌ Approach B: Node.js/TypeScript with Sharp + Azure OpenAI

**Analysis**: Strong candidate but TypeScript setup overhead + less personal experience with Sharp = higher risk for time constraint.

**Decision**: **REJECTED** - Python is safer bet given time pressure

---

### ❌ Approach C: Python FastAPI Web App + Azure OpenAI

**Analysis**: Over-engineered for "simple local app" requirement. Would require 4-5 hours minimum (frontend + backend).

**Decision**: **REJECTED** - Violates time constraint and requirement simplicity

---

### ❌ Approach D: n8n Workflow Automation

**Analysis**:
- No n8n expertise = steep learning curve
- Complex local setup for Adobe evaluators
- Doesn't match "CLI or simple app" requirement
- Risk of appearing as "flash over substance"

**Decision**: **REJECTED** - Instead, document automation integration paths in README

---

## Section 2: Recommended Solution Architecture

### Tech Stack with Justifications

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Language** | Python 3.11+ | Async support, rich ecosystem, fast development, aligns with Fusion platform experience |
| **Image Generation** | Azure OpenAI DALL-E 3 | Showcases Azure AI expertise, high-quality outputs, confirmed access |
| **Content Moderation** | **Azure Content Safety API** | ML-powered contextual analysis (superior to regex), shows Azure ecosystem depth, supports custom blocklists |
| **Image Processing** | Pillow (PIL) 10.x | Industry standard, text rendering, multi-format support, resize/crop capabilities |
| **CLI Framework** | Click 8.x | Professional CLIs, auto-generated help, parameter validation |
| **Data Validation** | Pydantic v2 | Type safety, automatic validation, JSON/YAML parsing, self-documenting models |
| **YAML Parsing** | PyYAML | Standard library, robust |
| **Async I/O** | asyncio + aiohttp | Concurrent image generation (3 aspect ratios in parallel) |
| **Logging** | structlog | Production-ready, JSON output, enables bonus reporting feature |

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                          CLI Interface                           │
│                     (Click + Command Handlers)                   │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Application Layer                            │
│  ┌──────────────┐  ┌─────────────────┐  ┌──────────────────┐   │
│  │ Campaign     │  │ Asset Generator │  │ Composition      │   │
│  │ Orchestrator │──│ Service         │──│ Service          │   │
│  └──────────────┘  └─────────────────┘  └──────────────────┘   │
│         │                   │                     │              │
│         └───────────────────┴─────────────────────┘              │
│                             │                                    │
│                             ▼                                    │
│                  ┌─────────────────────┐                        │
│                  │ Compliance Service  │                        │
│                  │ (Content Safety)    │                        │
│                  └─────────────────────┘                        │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Domain Layer                               │
│  ┌───────────────┐  ┌──────────────┐  ┌──────────────────┐     │
│  │ Campaign      │  │ Asset        │  │ Brand Guidelines │     │
│  │ (Pydantic)    │  │ (Pydantic)   │  │ (Pydantic)       │     │
│  └───────────────┘  └──────────────┘  └──────────────────┘     │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Infrastructure Layer                           │
│  ┌──────────────┐  ┌─────────────────┐  ┌──────────────────┐   │
│  │ Azure DALL-E │  │ Azure Content   │  │ Pillow Image     │   │
│  │ Client       │  │ Safety Client   │  │ Processor        │   │
│  └──────────────┘  └─────────────────┘  └──────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ File System Repository (Local Assets + Outputs)         │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘

            ┌──────────────────────────────────┐
            │  External Dependencies           │
            │  ┌────────────┐  ┌────────────┐  │
            │  │ Azure AI   │  │ Local      │  │
            │  │ Services   │  │ Assets     │  │
            │  └────────────┘  └────────────┘  │
            └──────────────────────────────────┘
```

### Data Flow Pipeline

```
1. INPUT: campaign_brief.yaml
   ↓
2. VALIDATE: Pydantic Campaign model
   - Products (≥2 required)
   - Target market/audience
   - Campaign message
   - Brand guidelines (optional)
   ↓
3. COMPLIANCE CHECK: Azure Content Safety API
   - ML-powered contextual analysis
   - Custom blocklist for prohibited advertising terms
   - Severity scoring (Hate/Violence/Sexual/SelfHarm)
   ↓ [PASS/FAIL gate]
   ↓
4. CHECK: Local assets directory
   │
   ├─→ Asset exists? → Reuse (log reuse event)
   │
   └─→ Missing? → Generate via Azure DALL-E
       - Async generation (concurrent requests)
       - Prompt engineering for brand consistency
       ↓
5. GENERATE: 3 aspect ratios per product (1:1, 9:16, 16:9)
   - asyncio.gather() for parallel execution
   - Progress logging
   ↓
6. COMPOSE: Add campaign message text overlay
   - Pillow.ImageDraw for text rendering
   - Configurable positioning, font, color
   - Localization support (bonus)
   ↓
7. VALIDATE (Bonus): Brand compliance checks
   - Logo presence detection (template matching)
   - Color palette validation (histogram analysis)
   ↓
8. SAVE: Organized output structure
   outputs/
   ├── product-a/
   │   ├── 1-1/
   │   │   └── campaign-product-a-square.png
   │   ├── 9-16/
   │   │   └── campaign-product-a-story.png
   │   └── 16-9/
   │       └── campaign-product-a-wide.png
   └── product-b/
       └── ...
   ↓
9. REPORT: Structured log output
   - JSON logs (machine-readable)
   - Human-readable summary
   - Compliance report
   - Asset generation metrics
```

### Key Design Decisions

| Decision | Justification | Adobe Value |
|----------|---------------|-------------|
| **Clean Architecture layers** | Separates business logic from infrastructure; testable without external dependencies | Shows enterprise system design maturity |
| **Pydantic domain models** | Type safety catches errors early; auto-validates input; clear error messages | Production-ready patterns |
| **Async image generation** | Generates 1:1, 9:16, 16:9 in parallel → 3x faster | Understands I/O-bound optimization, scalability thinking |
| **Azure Content Safety API** | ML-powered contextual analysis vs. simple regex | Deep Azure AI ecosystem knowledge, integration expertise |
| **Asset reuse logic** | Checks local folder before generating; saves API costs | Cost-consciousness, efficiency optimization |
| **Structured logging (structlog)** | JSON logs for ingestion; enables bonus "reporting" feature | Observability thinking, production operations mindset |
| **CLI interface (Click)** | Professional `--help`, parameter validation, clear UX | Customer-facing tool quality |
| **Infrastructure abstraction** | `ImageGenerationPort` interface with DALL-E implementation | Could swap to Adobe Firefly without changing business logic (FDE integration scenario) |

---

## Section 3: Differentiation Strategy

### What Makes This Stand Out

#### 1. Azure Content Safety API (vs. Simple Regex)

**Most Candidates Will Do:**
```python
PROHIBITED_WORDS = ['free', 'guarantee', 'winner']
if any(word in message.lower() for word in PROHIBITED_WORDS):
    raise Error("Prohibited word detected")
```

**Your Approach:**
```python
from azure.ai.contentsafety import ContentSafetyClient

result = await content_safety.analyze_text(
    text=campaign.message,
    categories=["Hate", "SelfHarm", "Sexual", "Violence"],
    blocklist_names=["prohibited-advertising-terms"]  # Enterprise feature
)

# Returns ML-powered contextual analysis with severity scores
# "feel free to contact us" → PASS (context understood)
# "free guaranteed results" → FAIL (promotional claim detected)
```

**Why This Wins:**
- Shows deeper Azure AI understanding (beyond just DALL-E)
- Demonstrates integration expertise (connecting multiple Azure services)
- Enterprise-ready (custom blocklists managed by legal team)
- Aligns with FDE role (helping customers leverage Azure AI ecosystem)

#### 2. Clean Architecture (vs. Monolithic Script)

**Most Candidates Will Do:**
```
campaign_generator.py  (500+ lines, all logic mixed)
```

**Your Approach:**
```
src/
├── domain/           # Business models (Campaign, Asset, BrandGuidelines)
├── application/      # Orchestration (CampaignService, ComplianceService)
└── infrastructure/   # Azure clients, file system, Pillow processor
```

**Why This Wins:**
- Demonstrates system design thinking (not just coding)
- Testable architecture (domain logic isolated from I/O)
- Scalable foundation (easy to add API layer, queue processing, etc.)
- Shows senior-level patterns (most candidates won't do this for a POC)

#### 3. Async Concurrency (vs. Sequential Processing)

**Most Candidates Will Do:**
```python
for product in products:
    for aspect_ratio in ['1:1', '9:16', '16:9']:
        image = generate_image(product, aspect_ratio)  # Blocking
        save(image)
# Total time: 6 products × 3 ratios × 30 seconds = 90 seconds
```

**Your Approach:**
```python
tasks = [
    generate_image(product, ratio)
    for product in products
    for ratio in ['1:1', '9:16', '16:9']
]
results = await asyncio.gather(*tasks)  # Concurrent execution
# Total time: ~30 seconds (limited by API rate limits, not code)
```

**Why This Wins:**
- Performance optimization (3x faster for demo)
- Shows understanding of async patterns (I/O-bound workloads)
- Impressive in video (watch all 6 images generate simultaneously)
- Production-thinking (campaigns need hundreds of variants)

#### 4. Claude Code Enhancement Path (Innovation Without Breaking Requirements)

**What You Add to README:**
```markdown
## Enterprise Integration: Claude Code Orchestration

While this tool runs standalone, it can be enhanced with AI orchestration:

### Custom Slash Command: `/generate-campaign`
Validates briefs with @agent-review, suggests optimizations with @agent-architecture,
then executes generation with automated documentation via @agent-documentation.

### Why This Matters for Adobe
FDE role involves helping customers integrate Adobe products. This demonstrates
how standalone tools can be orchestrated via AI agents for enterprise workflows.
```

**Why This Wins:**
- Shows innovation (Claude Code + subagents is your unique strength)
- Doesn't break requirements (tool still runs standalone)
- Demonstrates FDE thinking (integration paths, customer value)
- Interview talking point (differentiates you from all other candidates)

### Adobe-Specific Value Alignment

| FDE Role Requirement | How Solution Demonstrates It |
|----------------------|------------------------------|
| **Customer-facing technical expertise** | CLI provides clear error messages, comprehensive `--help`, example campaigns |
| **Rapid prototyping** | 2-3 hour implementation → ability to deliver fast POCs in customer meetings |
| **Integration skills** | Azure AI integration (DALL-E + Content Safety) → connecting Adobe with partner ecosystems |
| **Scalability thinking** | Async architecture + clean separation → obvious production path (add API, queue, multi-tenant) |
| **Business outcome focus** | Addresses all 5 pain points → understanding customer problems, not just technical specs |

### Bonus Features: Maximum Impact for Minimal Time

| Feature | Implementation Time | Impact | Priority | Approach |
|---------|---------------------|--------|----------|----------|
| **Azure Content Safety** | 20 min | 🔥🔥🔥 | **P0** | Azure SDK + custom blocklist |
| **Brand compliance: Logo check** | 15 min | 🔥🔥 | **P1** | Pillow color histogram analysis |
| **Structured logging** | 5 min | 🔥 | **P1** | structlog with JSON output |
| **Claude Code docs** | 10 min | 🔥🔥 | **P2** | README section + example command |
| **Localization support** | 30 min | 🔥 | **P3** | Cut if time pressure |

---

## Section 4: Demo Video Strategy

### 2-3 Minute Video Outline (165 seconds)

| Timestamp | Duration | Segment | Visual | Script Notes |
|-----------|----------|---------|--------|--------------|
| **0:00-0:15** | 15s | Opening Hook | Assignment brief on screen | "Adobe FDE assignment: automate creative generation for hundreds of localized campaigns. Here's my solution built in under 3 hours." |
| **0:15-1:00** | 45s | Architecture Overview | ASCII diagram → folder structure | "Clean architecture: domain models validate input, application layer orchestrates Azure AI services, infrastructure handles DALL-E and Content Safety. Notice the separation—I can swap DALL-E for Adobe Firefly with one class change." |
| **1:00-1:20** | 20s | Campaign Input | Terminal with YAML | "Campaign brief in YAML: 2 products, target APAC market, message validated by Azure Content Safety API. Watch what happens..." |
| **1:20-2:20** | 60s | Live Execution | Terminal showing async output → generated images | `python -m adobe_campaign generate campaign.yaml`<br>"Async generation: 3 aspect ratios per product, 6 images total. Notice parallel execution. Content Safety check: PASSED. Brand compliance: PASSED. Logo detected, color palette valid..." |
| **2:20-2:50** | 30s | Code Highlight | IDE showing Pydantic model + async code | "Azure Content Safety API validates compliance—ML-powered contextual analysis, not just regex. Here's where it gets interesting: this standalone tool can be orchestrated by Claude Code for enterprise workflows. Campaign teams use AI agents to validate, optimize, then trigger generation." |
| **2:50-3:05** | 15s | Closing | Evolution diagram | "This scales: add API layer for web, queue for async, blob storage for assets. Built to grow with Adobe's customer needs. Thanks for watching." |

### Recording Setup Checklist

- [ ] Screen resolution: 1920x1080
- [ ] Terminal: Clean theme, 16-18pt font (readable in video)
- [ ] IDE: VS Code with clean theme, same font size
- [ ] Audio: Clear narration (test recording first), no background music
- [ ] No transitions (waste time) - just cuts between segments
- [ ] Test campaign prepared and validated beforehand

### Sample Campaign for Demo

```yaml
# demo_campaign.yaml
campaign_id: adobe-demo-eco-tech-2025
products:
  - name: "EcoBottle Pro"
    description: "Sustainable water bottle with smart hydration tracking"
  - name: "SolarCharge Mini"
    description: "Portable solar power bank for mobile devices"

target_market: "APAC"
target_audience: "Eco-conscious millennials, ages 25-35"
campaign_message: "Power your day, naturally. Save the planet, one charge at a time."

brand_guidelines:
  primary_color: "#2E7D32"  # Green
  secondary_color: "#FFC107"  # Amber
  logo_required: true
```

### Key Talking Points (Memorize These)

✅ **DO SAY:**
- "Completed in 2.5 hours" (shows efficiency)
- "Addresses all 5 pain points from the brief" (business outcome focus)
- "Production-ready patterns" (scalability thinking)
- "Azure AI ecosystem integration" (technical depth + Adobe alignment)
- "Can be orchestrated via Claude Code" (your unique differentiator)

❌ **DON'T SAY:**
- "This was easy" (shows poor judgment)
- "Given more time I would..." (sounds incomplete)
- "I usually use X but..." (undermines your choices)
- "This is just a POC" (downplays your work)

---

## Section 5: Risk Mitigation

### Technical Risks

| Risk | Probability | Impact | Mitigation Plan |
|------|-------------|--------|-----------------|
| **Azure DALL-E API failure** | 🟡 MEDIUM | 🔴 HIGH | **Pre-generate 3 sample images** before implementation. Store in `assets/samples/`. Demo shows asset reuse logic. If API fails during dev, fall back to local assets only (still meets requirements, demonstrates architecture). |
| **Azure Content Safety API issues** | 🟢 LOW | 🟡 MEDIUM | **Have regex fallback ready**: Simple implementation takes 5 min. Document in code: "Currently using regex; Azure Content Safety integration ready for deployment." Still shows integration thinking. |
| **Pillow text rendering complexity** | 🟢 LOW | 🟡 MEDIUM | **Test in first 30 minutes**. If issues arise, use simple white text on black bar at bottom (guaranteed to work). Quality downgrade acceptable for POC. |
| **Async implementation bugs** | 🟡 MEDIUM | 🟢 LOW | **Start synchronous, refactor to async**. Synchronous version meets all requirements. Async is performance optimization. |

### Time Risks

**Total Budget: 180 minutes (3 hours)**

| Phase | Allocated | Buffer Available | Fallback if Behind |
|-------|-----------|------------------|-------------------|
| **Project Setup** | 15 min | -5 min | Skip virtual env, use system Python |
| **Domain Models** | 30 min | -10 min | Skip type hints (add in polish phase) |
| **Azure DALL-E Integration** | 30 min | -15 min | Use pre-generated images only |
| **Image Composition** | 30 min | -10 min | Simple text overlay (no fancy positioning) |
| **Azure Content Safety** | 20 min | -15 min | Fall back to regex (5 min implementation) |
| **CLI + Error Handling** | 20 min | -5 min | Basic error messages only |
| **Bonus Features** | 30 min | **CUT ENTIRELY** | Skip logo check, keep only Content Safety |
| **Documentation** | 20 min | -5 min | README only (skip architecture docs) |
| **Demo Video** | 25 min | **PROTECTED** | Must allocate - it's required deliverable |

**Emergency Time-Saving Strategies:**

1. **Use Claude Code for boilerplate** (saves 20-30 min):
   - Generate Pydantic models
   - Generate CLI setup
   - Generate folder structure
   - Generate docstrings

2. **Copy-paste from proven patterns** (saves 15 min):
   - Azure SDK client setup (from Fusion platform)
   - Logging configuration
   - Error handling patterns

3. **Skip non-essential polish** (saves 20 min):
   - Detailed error messages → simple ones
   - Custom exceptions → use built-ins
   - Comprehensive logging → basic print statements
   - Unit tests → mention in README as "next step"

### Quality Risks

| Risk | Impact | Prevention | Detection | Fix |
|------|--------|------------|-----------|-----|
| **Spaghetti code under pressure** | 🔴 CRITICAL | Pre-plan architecture, use Claude Code for structure | Code review at 90-min mark | Refactor one layer at a time (domain first) |
| **Poor error messages** | 🟡 MEDIUM | Write error messages first (they're quick) | Manual testing with invalid input | Add try/except with clear messages |
| **Undocumented code** | 🔴 HIGH | Write docstrings as you code (5 sec per function), use type hints | README completeness check | Claude Code generates missing docstrings |
| **Inconsistent naming** | 🟢 LOW | Follow PEP 8, use linter | Run `black` formatter | Auto-format with `black .` |

### Quality Checkpoints (Every 30 Minutes)

**30-minute mark**: ✅ Domain models complete
- Can parse sample YAML without errors?
- Pydantic validation works correctly?

**60-minute mark**: ✅ Azure integration working or stubbed
- Generated at least one image successfully?
- Fallback to local assets works?

**90-minute mark**: ✅ Core pipeline end-to-end
- Input YAML → Output images for one campaign?
- **CODE REVIEW CHECKPOINT**: Architecture visible in folder structure?

**120-minute mark**: ✅ Bonus features decision point
- Time remaining ≥45 min? → Implement P0/P1 bonus features
- Time remaining <45 min? → Skip bonuses, focus on README + video

**150-minute mark**: ✅ README complete
- Installation tested in clean environment?
- Example commands work?

**165-minute mark**: ✅ Video recording begins
- Script prepared?
- Demo campaign validated?

### Feature Creep Circuit Breaker

**WARNING SIGNS** (stop immediately if you catch yourself):
- Spending >10 minutes on text positioning aesthetics
- Implementing retry logic with exponential backoff
- Creating custom exception hierarchy
- Building YAML schema generator
- Adding configuration validation framework

**EMERGENCY STOP PROCEDURE**:
1. Ask: "Is this Must-Have or Nice-to-Have?"
2. Reference core requirements from assignment
3. If Nice-to-Have: **STOP and move to next Must-Have**

**Acceptable Quality Shortcuts**:
- ✅ Hardcoded font path
- ✅ Fixed text positioning
- ✅ Single error message per failure type
- ✅ Basic logging (vs. full structlog if time-pressed)
- ✅ No retry logic

**Unacceptable Shortcuts** (Adobe will notice):
- ❌ No type hints
- ❌ No docstrings
- ❌ No README
- ❌ Messy folder structure
- ❌ API keys hardcoded in source

---

## Next Steps

### ✅ Strategy Approved

**Proceed to Detailed Implementation Plan**:
- Phase-by-phase instructions (15-30 min granularity)
- Exact commands and code snippets
- Manual steps (GitHub repo setup, Azure portal config)
- Claude Code integration points
- Validation checkpoints with acceptance criteria
- Time tracking and fallback plans

**Estimated Time to Create Plan**: 45-60 minutes

---

**Document Version**: 1.0
**Last Updated**: 2025-10-05
**Status**: ✅ Approved - Proceed to Implementation Plan
