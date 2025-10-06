# Manual Integration Tests

These are development/debugging scripts for manual testing of individual services.

**Note**: These are NOT automated pytest tests. For automated tests, see `../integration/test_campaign_pipeline.py`.

## Usage

```bash
# Activate virtual environment
source venv/bin/activate

# Run individual test scripts
python tests/manual/test_application.py
python tests/manual/test_infrastructure.py
python tests/manual/test_translation.py
```

## Test Files

- **test_application.py**: Manual tests for application layer services (ComplianceService, AssetGeneratorService, CampaignOrchestrator)
- **test_infrastructure.py**: Manual tests for Azure infrastructure clients (DALLEClient, ContentSafetyClient, MessageAdapterService)
- **test_translation.py**: Manual tests for Azure Translator API integration

## Automated Tests

For automated integration tests with pytest, use:

```bash
pytest tests/integration/test_campaign_pipeline.py -v
```

This runs 11 automated integration tests with mocked Azure responses.
