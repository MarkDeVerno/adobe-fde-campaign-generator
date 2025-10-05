# Adobe FDE Campaign Generator - Test Checklist

**Purpose**: Sequential validation checklist for the implementation process
**Usage**: Check off each item as you complete it during implementation
**Status**: Run through this checklist at each phase milestone

---

## Phase 0: Manual Setup

| Step | Status | Description | Reference |
|------|--------|-------------|-----------|
| 0.1 | ✅ | Azure OpenAI resource created and DALL-E 3 deployed | [Phase 0 - Step 0.1](02-IMPLEMENTATION-PLAN.md#phase-0-manual-setup-30-45-min) |
| 0.2 | ✅ | Azure Content Safety resource created with custom blocklist | [Phase 0 - Step 0.1](02-IMPLEMENTATION-PLAN.md#phase-0-manual-setup-30-45-min) |
| 0.3 | ✅ | All Azure credentials saved (endpoints + API keys) | [Phase 0 - Validation](02-IMPLEMENTATION-PLAN.md#validation-checkpoint) |
| 0.4 | ✅ | GitHub repo created: `adobe-fde-campaign-generator` | [Phase 0 - Step 0.2](02-IMPLEMENTATION-PLAN.md#step-02-create-github-repository-10-min-manual) |
| 0.5 | ✅ | Local project directory created with venv | [Phase 0 - Step 0.3](02-IMPLEMENTATION-PLAN.md#step-03-initialize-local-project-15-min-hybrid) |
| 0.6 | ✅ | `.env` file created with actual Azure credentials | [Phase 0 - Validation](02-IMPLEMENTATION-PLAN.md#validation-checkpoint-1) |
| 0.7 | ✅ | Git remote configured to GitHub repo | [Phase 0 - Validation](02-IMPLEMENTATION-PLAN.md#validation-checkpoint-1) |

**Validation Commands**:
```bash
# Verify .env has real credentials (not placeholders)
cat .env | grep AZURE_OPENAI_ENDPOINT

# Verify git remote
git remote -v
```

---

## Phase 1: Project Scaffolding

| Step | Status | Description | Reference |
|------|--------|-------------|-----------|
| 1.1 | ☐ | Directory structure created (src/domain, src/application, src/infrastructure, src/cli) | [Phase 1 - Step 1.1](02-IMPLEMENTATION-PLAN.md#step-11-create-directory-structure-2-min) |
| 1.2 | ☐ | `.gitignore` configured (excludes .env, venv/, \_\_pycache\_\_) | [Phase 1 - Step 1.2](02-IMPLEMENTATION-PLAN.md#step-12-create-gitignore-2-min) |
| 1.3 | ☐ | `requirements.txt` created with all dependencies | [Phase 1 - Step 1.3](02-IMPLEMENTATION-PLAN.md#step-13-create-requirementstxt-3-min) |
| 1.4 | ☐ | Dependencies installed in venv | [Phase 1 - Step 1.4](02-IMPLEMENTATION-PLAN.md#step-14-install-dependencies-5-min) |
| 1.5 | ☐ | All imports work (click, pydantic, openai, PIL, structlog) | [Phase 1 - Validation](02-IMPLEMENTATION-PLAN.md#validation-checkpoint-2) |

**Validation Commands**:
```bash
# Verify directory structure
tree -L 3 src/

# Verify dependencies installed
pip list | grep -E "(click|pydantic|azure|Pillow|structlog)"

# Test imports
python -c "import click, pydantic, openai, PIL, structlog; print('All imports successful')"
```

---

## Phase 2: Domain Layer

| Step | Status | Description | Reference |
|------|--------|-------------|-----------|
| 2.1 | ☐ | `campaign.py` created with Product, BrandGuidelines, Campaign models | [Phase 2 - Step 2.1](02-IMPLEMENTATION-PLAN.md#step-21-create-campaign-model) |
| 2.2 | ☐ | `asset.py` created with AspectRatio enum and Asset model | [Phase 2 - Step 2.2](02-IMPLEMENTATION-PLAN.md#step-22-create-asset-model) |
| 2.3 | ☐ | `compliance.py` created with ComplianceResult model | [Phase 2 - Step 2.3](02-IMPLEMENTATION-PLAN.md#step-23-create-compliance-model) |
| 2.4 | ☐ | Campaign model parses `campaign_example.yaml` successfully | [Phase 2 - Validation](02-IMPLEMENTATION-PLAN.md#validation-checkpoint-5-min) |
| 2.5 | ☐ | Pydantic validators reject invalid data (empty product name, <2 products) | [Phase 2 - Validation](02-IMPLEMENTATION-PLAN.md#validation-checkpoint-5-min) |
| 2.6 | ☐ | AspectRatio enum returns correct dimensions (1024x1024, 1024x1820, 1820x1024) | [Phase 2 - Validation](02-IMPLEMENTATION-PLAN.md#validation-checkpoint-5-min) |

**Validation Commands**:
```bash
# Test domain models (create test_domain.py from implementation plan)
python test_domain.py

# Expected output:
# ✅ Campaign loaded successfully
# ✅ Campaign has 2 products
# ✅ Validation rejected empty product name
# ✅ Asset dimensions correct: 1024x1024
# ✅ Compliance result created
```

**Checkpoint**: ⏱️ **30 minutes** - Domain models must parse YAML successfully

---

## Phase 3: Infrastructure Layer

| Step | Status | Description | Reference |
|------|--------|-------------|-----------|
| 3.1 | ☐ | `dalle_client.py` created with async image generation | [Phase 3 - Step 3.1](02-IMPLEMENTATION-PLAN.md#step-31-create-dall-e-client-15-min) |
| 3.2 | ☐ | `content_safety_client.py` created with blocklist support | [Phase 3 - Step 3.2](02-IMPLEMENTATION-PLAN.md#step-32-create-azure-content-safety-client-10-min) |
| 3.3 | ☐ | `image_composer.py` created with resize and text overlay | [Phase 3 - Step 3.3](02-IMPLEMENTATION-PLAN.md#step-33-create-image-composer-10-min) |
| 3.4 | ☐ | DALL-E client initializes with correct endpoint and deployment | [Phase 3 - Validation](02-IMPLEMENTATION-PLAN.md#validation-checkpoint-10-min) |
| 3.5 | ☐ | Content Safety detects safe messages (passed=True) | [Phase 3 - Validation](02-IMPLEMENTATION-PLAN.md#validation-checkpoint-10-min) |
| 3.6 | ☐ | Content Safety detects prohibited terms (passed=False, matches list) | [Phase 3 - Validation](02-IMPLEMENTATION-PLAN.md#validation-checkpoint-10-min) |
| 3.7 | ☐ | Image composer resizes correctly (1024x1024 → 1024x1820 for 9:16) | [Phase 3 - Validation](02-IMPLEMENTATION-PLAN.md#validation-checkpoint-10-min) |
| 3.8 | ☐ | Image composer adds text overlay successfully | [Phase 3 - Validation](02-IMPLEMENTATION-PLAN.md#validation-checkpoint-10-min) |

**Validation Commands**:
```bash
# Run infrastructure tests (create test_infrastructure.py from plan)
python test_infrastructure.py

# Expected output:
# ✅ DALL-E client initialized
# ✅ Content Safety client initialized
# ✅ Safe message analysis: passed=True
# ✅ Prohibited term detection: passed=False, matches=['guaranteed results', 'risk-free']
# ✅ Image composer initialized
# ✅ Resize works: (1024, 1024) → (1024, 1820)
# ✅ Text overlay works
# 🎉 All infrastructure tests passed!
```

**Checkpoint**: ⏱️ **60 minutes** - Azure integration must be working (at least 1 successful API call)

---

## Phase 4: Application Layer

| Step | Status | Description | Reference |
|------|--------|-------------|-----------|
| 4.1 | ☐ | `campaign_orchestrator.py` created with pipeline orchestration | [Phase 4 - Step 4.1](02-IMPLEMENTATION-PLAN.md#step-41-campaign-orchestrator-service-15-min) |
| 4.2 | ☐ | `compliance_service.py` created wrapping Content Safety | [Phase 4 - Step 4.2](02-IMPLEMENTATION-PLAN.md#step-42-compliance-service-5-min) |
| 4.3 | ☐ | `asset_generator.py` created with async concurrent generation | [Phase 4 - Step 4.3](02-IMPLEMENTATION-PLAN.md#step-43-asset-generator-service-10-min) |
| 4.4 | ☐ | Compliance service validates safe messages | [Phase 4 - Validation](02-IMPLEMENTATION-PLAN.md#validation-checkpoint-10-min-1) |
| 4.5 | ☐ | Compliance service rejects prohibited terms | [Phase 4 - Validation](02-IMPLEMENTATION-PLAN.md#validation-checkpoint-10-min-1) |
| 4.6 | ☐ | Asset generator builds correct DALL-E prompts | [Phase 4 - Validation](02-IMPLEMENTATION-PLAN.md#validation-checkpoint-10-min-1) |
| 4.7 | ☐ | Campaign orchestrator validates YAML loading | [Phase 4 - Validation](02-IMPLEMENTATION-PLAN.md#validation-checkpoint-10-min-1) |
| 4.8 | ☐ | Clean Architecture dependency flow correct (App→Domain←Infra) | [Phase 4 - Architecture Validation](02-IMPLEMENTATION-PLAN.md#architecture-validation) |

**Validation Commands**:
```bash
# Test application layer (create test_application.py from plan)
python test_application.py

# Expected output:
# Testing Application Layer...
# 1. Testing Compliance Service:
#    ✅ Safe message passed compliance
#    ✅ Prohibited terms detected: ['guaranteed results']
# 2. Testing Asset Generator:
#    ✅ Prompt generated for EcoBottle Pro
# 3. Testing Campaign Orchestrator:
#    ✅ Campaign loaded successfully
#    ✅ Compliance check completed
```

**Checkpoint**: ⏱️ **90 minutes** - CODE REVIEW - Is Clean Architecture visible? Type hints present?

---

## Phase 5: CLI Interface

| Step | Status | Description | Reference |
|------|--------|-------------|-----------|
| 5.1 | ☐ | `cli/main.py` created with Click commands | [Phase 5 - Step 5.1](02-IMPLEMENTATION-PLAN.md#step-51-main-cli-entry-point-10-min) |
| 5.2 | ☐ | `cli/utils.py` created with colored output functions | [Phase 5 - Step 5.2](02-IMPLEMENTATION-PLAN.md#step-52-cli-utilities-5-min) |
| 5.3 | ☐ | CLI help text displays correctly | [Phase 5 - Validation](02-IMPLEMENTATION-PLAN.md#validation-checkpoint-3) |
| 5.4 | ☐ | CLI validates environment variables before execution | [Phase 5 - Validation](02-IMPLEMENTATION-PLAN.md#validation-checkpoint-3) |

**Validation Commands**:
```bash
# Test CLI help
python -m src.cli.main --help

# Expected output:
# Usage: main.py [OPTIONS] COMMAND [ARGS]...
#
# Adobe Campaign Generator CLI
#
# Options:
#   --help  Show this message and exit.
#
# Commands:
#   generate  Generate campaign assets from YAML brief
```

**Checkpoint**: ⏱️ **120 minutes** - Core pipeline end-to-end working

---

## Phase 6: Testing & Validation

| Step | Status | Description | Reference |
|------|--------|-------------|-----------|
| 6.1 | ☐ | Integration tests created (`test_campaign_pipeline.py`) | [Phase 6 - Step 6.1](02-IMPLEMENTATION-PLAN.md#step-61-integration-test-suite-15-min) |
| 6.2 | ☐ | YAML loading tests pass | [Phase 6 - Step 6.1](02-IMPLEMENTATION-PLAN.md#step-61-integration-test-suite-15-min) |
| 6.3 | ☐ | Compliance check tests pass | [Phase 6 - Step 6.1](02-IMPLEMENTATION-PLAN.md#step-61-integration-test-suite-15-min) |
| 6.4 | ☐ | End-to-end pipeline test passes (with mocked DALL-E) | [Phase 6 - Step 6.1](02-IMPLEMENTATION-PLAN.md#step-61-integration-test-suite-15-min) |
| 6.5 | ☐ | No hardcoded secrets in source code | [Phase 6 - Step 6.3](02-IMPLEMENTATION-PLAN.md#step-63-quality-checks-5-min) |
| 6.6 | ☐ | All functions have type hints | [Phase 6 - Step 6.3](02-IMPLEMENTATION-PLAN.md#step-63-quality-checks-5-min) |
| 6.7 | ☐ | All classes/functions have docstrings | [Phase 6 - Step 6.3](02-IMPLEMENTATION-PLAN.md#step-63-quality-checks-5-min) |

**Validation Commands**:
```bash
# Run integration tests
pytest tests/integration/test_campaign_pipeline.py -v

# Check for hardcoded secrets
grep -r "sk-" src/ || echo "✅ No hardcoded API keys"
grep -r "https://.*openai.azure.com" src/ || echo "✅ No hardcoded endpoints"

# Check type hints (requires mypy)
mypy src/ --ignore-missing-imports

# Check docstrings
python -c "import ast; import sys; [print(f'Missing docstring: {node.name}') for node in ast.walk(ast.parse(open('src/domain/models/campaign.py').read())) if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and not ast.get_docstring(node)]"
```

**Checkpoint**: ⏱️ **150 minutes** - README complete, all tests passing

---

## Phase 7: Documentation

| Step | Status | Description | Reference |
|------|--------|-------------|-----------|
| 7.1 | ☐ | `README.md` created with all required sections | [Phase 7 - Step 7.1](02-IMPLEMENTATION-PLAN.md#step-71-comprehensive-readmemd-15-min) |
| 7.2 | ☐ | README includes Claude Code enhancement path (key differentiator!) | [Phase 7 - Step 7.1](02-IMPLEMENTATION-PLAN.md#step-71-comprehensive-readmemd-15-min) |
| 7.3 | ☐ | `.env.template` created with placeholder values | [Phase 7 - Step 7.2](02-IMPLEMENTATION-PLAN.md#step-72-envtemplate-enhancement-optional) |
| 7.4 | ☐ | `docs/ARCHITECTURE.md` created (optional but recommended) | [Phase 7 - Step 7.3](02-IMPLEMENTATION-PLAN.md#step-73-architecture-documentation-5-min) |
| 7.5 | ☐ | README has 15+ sections (Features, Installation, Usage, Architecture, etc.) | [Phase 7 - Validation](02-IMPLEMENTATION-PLAN.md#validation-checkpoint-4) |
| 7.6 | ☐ | LICENSE file created | [Phase 7 - Step 7.4](02-IMPLEMENTATION-PLAN.md#step-74-license-file-2-min) |

**Validation Commands**:
```bash
# Check README line count (should be ~550 lines)
wc -l README.md

# Check README sections
grep "^#" README.md | wc -l  # Should be 15+

# Verify .env.template exists (NOT .env)
ls -la | grep ".env"
# Should show: .env.template (NOT .env)
```

---

## Phase 8: Demo Video Preparation

| Step | Status | Description | Reference |
|------|--------|-------------|-----------|
| 8.1 | ☐ | Screen recording software tested (1920x1080) | [Phase 8 - Step 8.1](02-IMPLEMENTATION-PLAN.md#step-81-recording-setup-checklist) |
| 8.2 | ☐ | Terminal configured (clean theme, 16-18pt font) | [Phase 8 - Step 8.1](02-IMPLEMENTATION-PLAN.md#step-81-recording-setup-checklist) |
| 8.3 | ☐ | Demo campaign executed successfully (outputs/demo/ populated) | [Phase 8 - Step 8.4](02-IMPLEMENTATION-PLAN.md#step-84-pre-flight-check) |
| 8.4 | ☐ | Demo script prepared with exact commands and timestamps | [Phase 8 - Step 8.2](02-IMPLEMENTATION-PLAN.md#step-82-demo-script) |
| 8.5 | ☐ | Talking points memorized (Azure Content Safety, async, Claude Code path) | [Phase 8 - Step 8.3](02-IMPLEMENTATION-PLAN.md#step-83-talking-points) |
| 8.6 | ☐ | Practice run-through completed (at least once) | [Phase 8 - Step 8.4](02-IMPLEMENTATION-PLAN.md#step-84-pre-flight-check) |
| 8.7 | ☐ | Video length verified (2-3 minutes) | [Phase 8 - Step 8.4](02-IMPLEMENTATION-PLAN.md#step-84-pre-flight-check) |

**Validation Commands**:
```bash
# Generate demo campaign
python -m src.cli.main generate assets/samples/demo_campaign.yaml --output outputs/demo

# Verify outputs
ls -R outputs/demo/

# Should show:
# outputs/demo/
# ├── ecobottle-pro/
# │   ├── 1-1/*.png
# │   ├── 9-16/*.png
# │   └── 16-9/*.png
# └── solarcharge-mini/
#     └── ...
```

---

## Phase 9: Final Review & Submission

| Step | Status | Description | Reference |
|------|--------|-------------|-----------|
| 9.1 | ☐ | Type hints on all functions | [Phase 9 - Step 9.1](02-IMPLEMENTATION-PLAN.md#step-91-code-quality-checklist-5-min) |
| 9.2 | ☐ | Docstrings on all classes/functions | [Phase 9 - Step 9.1](02-IMPLEMENTATION-PLAN.md#step-91-code-quality-checklist-5-min) |
| 9.3 | ☐ | No hardcoded API keys in source | [Phase 9 - Step 9.1](02-IMPLEMENTATION-PLAN.md#step-91-code-quality-checklist-5-min) |
| 9.4 | ☐ | Clean folder structure visible | [Phase 9 - Step 9.1](02-IMPLEMENTATION-PLAN.md#step-91-code-quality-checklist-5-min) |
| 9.5 | ☐ | No TODO/FIXME comments | [Phase 9 - Step 9.1](02-IMPLEMENTATION-PLAN.md#step-91-code-quality-checklist-5-min) |
| 9.6 | ☐ | Requirements.txt accurate | [Phase 9 - Step 9.1](02-IMPLEMENTATION-PLAN.md#step-91-code-quality-checklist-5-min) |
| 9.7 | ☐ | README.md complete | [Phase 9 - Step 9.2](02-IMPLEMENTATION-PLAN.md#step-92-github-repo-checklist-5-min) |
| 9.8 | ☐ | `.env.template` in repo (NOT .env with real keys) | [Phase 9 - Step 9.2](02-IMPLEMENTATION-PLAN.md#step-92-github-repo-checklist-5-min) |
| 9.9 | ☐ | `.gitignore` includes .env, venv/, \_\_pycache\_\_ | [Phase 9 - Step 9.2](02-IMPLEMENTATION-PLAN.md#step-92-github-repo-checklist-5-min) |
| 9.10 | ☐ | Example campaign YAML included | [Phase 9 - Step 9.2](02-IMPLEMENTATION-PLAN.md#step-92-github-repo-checklist-5-min) |
| 9.11 | ☐ | Clean git history with meaningful commits | [Phase 9 - Step 9.2](02-IMPLEMENTATION-PLAN.md#step-92-github-repo-checklist-5-min) |
| 9.12 | ☐ | Repository is public | [Phase 9 - Step 9.2](02-IMPLEMENTATION-PLAN.md#step-92-github-repo-checklist-5-min) |
| 9.13 | ☐ | Demo video 2-3 minutes | [Phase 9 - Step 9.3](02-IMPLEMENTATION-PLAN.md#step-93-demo-video-checklist) |
| 9.14 | ☐ | Demo video shows live execution | [Phase 9 - Step 9.3](02-IMPLEMENTATION-PLAN.md#step-93-demo-video-checklist) |
| 9.15 | ☐ | Demo video mentions Azure Content Safety | [Phase 9 - Step 9.3](02-IMPLEMENTATION-PLAN.md#step-93-demo-video-checklist) |
| 9.16 | ☐ | Demo video mentions Claude Code enhancement path | [Phase 9 - Step 9.3](02-IMPLEMENTATION-PLAN.md#step-93-demo-video-checklist) |
| 9.17 | ☐ | Demo video has clear audio and readable text | [Phase 9 - Step 9.3](02-IMPLEMENTATION-PLAN.md#step-93-demo-video-checklist) |
| 9.18 | ☐ | Clean environment test passed | [Phase 9 - Step 9.5](02-IMPLEMENTATION-PLAN.md#step-95-clean-environment-test-3-min) |
| 9.19 | ☐ | Final git commit and push completed | [Phase 9 - Step 9.4](02-IMPLEMENTATION-PLAN.md#step-94-final-git-commands-2-min) |
| 9.20 | ☐ | GitHub repo URL accessible and public | [Phase 9 - Success Criteria](02-IMPLEMENTATION-PLAN.md#success-criteria) |

**Final Validation Commands**:
```bash
# Run all quality checks at once
echo "=== Code Quality Checks ==="
find src/ -name "*.py" -exec grep -l "sk-\|api_key\s*=\s*['\"]" {} \; || echo "✅ No hardcoded secrets"
find src/ -name "*.py" -exec grep -l "TODO\|FIXME" {} \; || echo "✅ No TODO/FIXME"
grep -q "\.env$" .gitignore && echo "✅ .gitignore includes .env"
grep -q "venv/" .gitignore && echo "✅ .gitignore includes venv/"
test -f .env.template && echo "✅ .env.template exists"
test ! -f .env && echo "✅ .env NOT in repo (good!)" || echo "⚠️ WARNING: .env file found - DO NOT COMMIT"

echo ""
echo "=== Repository Checks ==="
git remote -v | grep -q "adobe-fde-campaign-generator" && echo "✅ Git remote configured"
test -f README.md && wc -l README.md | awk '{print "✅ README exists ("$1" lines)"}'
test -f requirements.txt && echo "✅ requirements.txt exists"
test -f campaign_example.yaml && echo "✅ Example campaign exists"

echo ""
echo "=== Clean Environment Test ==="
# Simulate fresh clone
cd /tmp
rm -rf test-adobe-clone
git clone [YOUR-GITHUB-URL] test-adobe-clone
cd test-adobe-clone
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -c "import src.domain.models.campaign; print('✅ Imports work in clean environment')"
```

---

## Quick Reference: Time Checkpoints

| Time | Checkpoint | Validation |
|------|------------|------------|
| **30 min** | Domain models parse YAML | `python test_domain.py` |
| **60 min** | Azure integration working | `python test_infrastructure.py` |
| **90 min** | CODE REVIEW | Architecture visible? Type hints? |
| **120 min** | Core pipeline end-to-end | `python test_application.py` |
| **150 min** | README complete, all tests pass | `pytest tests/` + README check |

---

## Emergency Fallback Activations

If behind schedule at 120-minute mark:

| Action | Status | Reference |
|--------|--------|-----------|
| ❌ Skip bonus features (logo check, localization) | ☐ | [START-HERE.md - Emergency Fallbacks](START-HERE.md#if-running-behind-schedule-120-min-mark) |
| ✅ Keep Azure Content Safety (core differentiator) | ☐ | [START-HERE.md - Emergency Fallbacks](START-HERE.md#if-running-behind-schedule-120-min-mark) |
| ✅ Simple text overlay (no fancy positioning) | ☐ | [START-HERE.md - Emergency Fallbacks](START-HERE.md#if-running-behind-schedule-120-min-mark) |
| ✅ Basic error messages | ☐ | [START-HERE.md - Emergency Fallbacks](START-HERE.md#if-running-behind-schedule-120-min-mark) |
| ✅ Focus on README + video quality | ☐ | [START-HERE.md - Emergency Fallbacks](START-HERE.md#if-running-behind-schedule-120-min-mark) |

---

**Document Version**: 1.0
**Last Updated**: 2025-10-05
**Total Test Items**: 83 validation checkpoints
**Estimated Validation Time**: ~30 minutes (if run continuously)
