# Campaign Samples

This directory contains sample campaign YAML files demonstrating different features and use cases.

## Quick Start

```bash
# Run any sample campaign
./campaign-generator generate -f assets/samples/[filename].yaml
```

---

## Sample Files

### 1. `campaign_example.yaml` - Basic Demo
**Purpose**: Basic campaign demonstrating core functionality
**Features**:
- ✅ 2 products (EcoBottle Pro, SolarCharge Mini)
- ✅ 3 aspect ratios (1:1, 9:16, 16:9)
- ✅ Clean brand guidelines (eco-friendly theme)
- ✅ APAC market targeting

**Best for**: First-time users, basic feature exploration

**Expected outcome**: 6 assets generated cleanly, no compliance warnings

---

### 2. `healthcare-compliance-demo.yaml` - Legal Compliance Testing
**Purpose**: Demonstrates Azure Content Safety compliance checks
**Features**:
- ⚠️ Intentionally includes prohibited advertising terms
- ⚠️ Campaign message: "100% GUARANTEED results! Get FREE trial - RISK-FREE..."
- 🚨 Triggers: "FREE", "GUARANTEED", "RISK-FREE" blocklist matches
- ✅ Healthcare products (VitalTracker Pro, NutriBalance App)

**Best for**: Testing compliance service, understanding Content Safety integration

**Expected outcome**: Compliance warnings with recommendations to fix messaging

**Run with**:
```bash
# Without compliance check (generate anyway)
./campaign-generator generate -f assets/samples/healthcare-compliance-demo.yaml --skip-compliance

# With compliance check (see warnings)
./campaign-generator generate -f assets/samples/healthcare-compliance-demo.yaml
```

---

### 3. `luxury-brand-guidelines.yaml` - Brand Consistency
**Purpose**: Demonstrates brand guidelines enforcement
**Features**:
- 🎨 Premium color palette (sophisticated black #1A1A1A + luxury gold #D4AF37)
- 🏷️ Logo requirement enforced
- ✍️ Elegant font (Garamond serif)
- 👔 Luxury products (Heritage Leather Tote, Silk Cashmere Scarf)
- 🌍 Multi-region targeting (Europe & Middle East)

**Best for**: Understanding brand guidelines validation, premium brand positioning

**Expected outcome**: High-end visual style, brand consistency validated

---

### 4. `global-multilingual-demo.yaml` - APAC Translation Demo
**Purpose**: Demonstrates Azure Translator Text API integration (English → Simplified Chinese)
**Features**:
- 🌏 APAC market targeting triggers automatic translation to zh-Hans
- 🔤 Campaign message translates: "Your home, smarter" → "你的家，更智能"
- 🖋️ CJK-compatible font (Inter supports Chinese characters)
- 🏠 Smart home products (SmartHome Hub, EcoSensor Kit)

**Best for**: Testing translation feature, understanding locale mapping

**Expected outcome**:
- **With Azure Translator configured**: Message overlays in Simplified Chinese
- **Without configuration**: Falls back to English (graceful degradation)

**Run with translation enabled**:
```bash
# Set environment variables first
export AZURE_TRANSLATOR_KEY=your-key-here
export AZURE_TRANSLATOR_REGION=eastus

# Generate campaign (message will be translated)
./campaign-generator generate -f assets/samples/global-multilingual-demo.yaml --skip-compliance
```

**Market-to-Locale Mapping**:
- APAC → zh-Hans (Simplified Chinese)
- Middle East → ar (Arabic)
- Latin America → es (Spanish)
- Europe/North America → en (English)

---

### 5. `middle-east-translation-demo.yaml` - Arabic Translation Demo
**Purpose**: Demonstrates Azure Translator Text API integration (English → Arabic)
**Features**:
- 🌍 Middle East market targeting triggers automatic translation to Arabic (ar)
- 🔤 Campaign message translates: "Trust. Security. Growth." → "الثقة. الأمان. النمو."
- 🖋️ Arabic script support (Noto Sans Arabic font)
- 💰 Financial products (SecurePay Pro, WealthGuard Elite)
- 📖 Right-to-left text rendering for Arabic

**Best for**: Testing Arabic translation, understanding RTL text handling

**Expected outcome**:
- **With Azure Translator configured**: Message overlays in Arabic script
- **Without configuration**: Falls back to English

**Run with translation enabled**:
```bash
# Set environment variables first
export AZURE_TRANSLATOR_KEY=your-key-here
export AZURE_TRANSLATOR_REGION=eastus

# Generate campaign (message will be translated to Arabic)
./campaign-generator generate -f assets/samples/middle-east-translation-demo.yaml --skip-compliance
```

---

### 6. `asset-reuse-performance.yaml` - Caching & Performance
**Purpose**: Demonstrates asset reuse and caching optimization
**Features**:
- 📁 Filename-based caching system
- ⚡ Performance comparison (first run vs. cached run)
- ♻️ Asset reuse indicators in output
- 💼 Enterprise B2B products (CloudSync Pro, DataVault Secure)

**Best for**: Understanding performance optimization, testing caching behavior

**Expected outcome**:
- **First run**: ~3-4 seconds, 6 assets generated (✨ Generated)
- **Second run**: <1 second, 6 assets reused (♻️ Reused)

**Run multiple times**:
```bash
# First run - generates all assets
./campaign-generator generate -f assets/samples/asset-reuse-performance.yaml --skip-compliance

# Second run - reuses all assets from cache
./campaign-generator generate -f assets/samples/asset-reuse-performance.yaml --skip-compliance
```

---

## Feature Coverage Matrix

| Sample | Brand Guidelines | Compliance Check | Translation | Caching Demo | Market Type |
|--------|-----------------|------------------|-------------|--------------|-------------|
| `campaign_example.yaml` | ✅ Basic | ✅ Clean | ⊡ N/A (en→en) | ⊡ Implicit | B2C APAC |
| `healthcare-compliance-demo.yaml` | ✅ Medical | 🚨 **Triggers** | ⊡ N/A | ⊡ Implicit | B2C Healthcare |
| `luxury-brand-guidelines.yaml` | ✅ **Premium** | ✅ Clean | ⊡ N/A | ⊡ Implicit | B2C Luxury |
| `global-multilingual-demo.yaml` | ✅ Tech | ✅ Clean | ✅ **zh-Hans** | ⊡ Implicit | B2C APAC |
| `middle-east-translation-demo.yaml` | ✅ Financial | ✅ Clean | ✅ **Arabic** | ⊡ Implicit | B2C MENA |
| `asset-reuse-performance.yaml` | ✅ Enterprise | ✅ Clean | ⊡ N/A | ✅ **Explicit** | B2B Enterprise |

**Legend**: ✅ Full support | ⊡ Partial/N/A | 🚨 Intentionally triggers warnings

---

## Testing Recommendations

### Complete Feature Walkthrough
Run all samples sequentially to see full system capabilities:

```bash
# 1. Basic functionality
./campaign-generator generate -f assets/samples/campaign_example.yaml --skip-compliance

# 2. Compliance testing (see warnings)
./campaign-generator generate -f assets/samples/healthcare-compliance-demo.yaml

# 3. Brand consistency
./campaign-generator generate -f assets/samples/luxury-brand-guidelines.yaml --skip-compliance

# 4. Translation demo - APAC (English → Simplified Chinese)
./campaign-generator generate -f assets/samples/global-multilingual-demo.yaml --skip-compliance

# 5. Translation demo - Middle East (English → Arabic)
./campaign-generator generate -f assets/samples/middle-east-translation-demo.yaml --skip-compliance

# 6. Performance/caching (run twice to see reuse)
./campaign-generator generate -f assets/samples/asset-reuse-performance.yaml --skip-compliance
./campaign-generator generate -f assets/samples/asset-reuse-performance.yaml --skip-compliance
```

### Quick Demo (30 seconds)
```bash
# Best sample for quick demo
./campaign-generator generate -f assets/samples/luxury-brand-guidelines.yaml --skip-compliance
```

---

## Output Organization

All samples generate organized outputs:

```
outputs/
├── {Product 1}/
│   ├── 1x1/
│   │   └── {campaign_id}_{Product 1}_1x1.png
│   ├── 9x16/
│   │   └── {campaign_id}_{Product 1}_9x16.png
│   └── 16x9/
│       └── {campaign_id}_{Product 1}_16x9.png
└── {Product 2}/
    ├── 1x1/
    ├── 9x16/
    └── 16x9/
```

---

## Creating Custom Samples

### Minimal Valid Campaign
```yaml
campaign_id: my-campaign
products:
  - name: "Product 1"
    description: "Description here"
  - name: "Product 2"  # Minimum 2 products required
    description: "Description here"
target_market: "North America"
target_audience: "Your target audience"
campaign_message: "Your message"
```

### With Brand Guidelines
```yaml
brand_guidelines:
  primary_color: "#HEX"      # Must be valid hex color
  secondary_color: "#HEX"    # Must be valid hex color
  logo_required: true        # Boolean
  font_family: "FontName"    # Any font name
```

---

## Troubleshooting

### Compliance Warnings
If you see compliance warnings, either:
1. Fix the campaign message (remove prohibited terms)
2. Use `--skip-compliance` flag to generate anyway

### Missing Blocklist
If you see "Blocklist not found" error:
- Either use `--skip-compliance` flag
- Or create blocklist in Azure Content Safety portal

See `docs/TROUBLESHOOTING.md` for detailed solutions.

---

**Last Updated**: 2025-10-05
