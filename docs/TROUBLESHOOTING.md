# Troubleshooting Guide

## DALL-E 3 Image Generation Issues

### Error: "The imageGenerations operation does not work with the specified model, gpt-4o"

**Symptom**: When running the campaign generator, you get a 400 error stating that imageGenerations operation doesn't work with gpt-4o model, even though your `.env` file specifies `dall-e-3`.

**Root Cause**: This occurs when using a regional Azure endpoint (e.g., `https://eastus.api.cognitive.microsoft.com/`) instead of a resource-specific endpoint. The AsyncAzureOpenAI Python SDK has issues routing to the correct deployment when using regional endpoints.

**Solution**: Update your `.env` file to use the resource-specific endpoint:

```bash
# ❌ INCORRECT - Regional endpoint
AZURE_OPENAI_ENDPOINT=https://eastus.api.cognitive.microsoft.com/

# ✅ CORRECT - Resource-specific endpoint
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
```

**How to find your resource-specific endpoint**:
1. Go to Azure Portal
2. Navigate to your Azure OpenAI resource (e.g., `oai-sparkquest-prod-eus`)
3. Go to "Keys and Endpoint" section
4. Copy the "Endpoint" value - it should be in the format `https://your-resource-name.openai.azure.com/`

**Example**:
If your Azure OpenAI resource name is `oai-sparkquest-prod-eus`, your endpoint should be:
```bash
AZURE_OPENAI_ENDPOINT=https://oai-sparkquest-prod-eus.openai.azure.com/
```

After updating the `.env` file, run the campaign generator again:
```bash
./campaign-generator generate -f assets/samples/campaign_example.yaml --skip-compliance
```

## Azure Content Safety Blocklist Issues

### Error: "Blocklist with name prohibited-advertising-terms not found"

**Root Cause**: Blocklists are resource-specific. If you have multiple Azure resources (e.g., separate OpenAI and Content Safety resources), the blocklist created in one resource won't be available in another.

**Solutions**:

**Option 1: Skip compliance checking (for testing)**
```bash
./campaign-generator generate -f campaign.yaml --skip-compliance
```

**Option 2: Remove blocklist configuration**
Edit your `.env` file and remove or comment out the blocklist name:
```bash
# AZURE_CONTENT_SAFETY_BLOCKLIST_NAME=prohibited-advertising-terms
```

**Option 3: Create blocklist in correct resource**
1. Go to Azure Portal > Content Safety resource
2. Navigate to "Blocklists" section
3. Create a new blocklist named `prohibited-advertising-terms`
4. Add prohibited terms for advertising compliance

**Option 4: Use same resource for both services**
If your Azure OpenAI resource has Content Safety integrated and includes the blocklist:
```bash
# Use the same resource for both OpenAI and Content Safety
AZURE_OPENAI_ENDPOINT=https://oai-sparkquest-prod-eus.openai.azure.com/
AZURE_OPENAI_KEY=your-openai-key

AZURE_CONTENT_SAFETY_ENDPOINT=https://oai-sparkquest-prod-eus.openai.azure.com/
AZURE_CONTENT_SAFETY_KEY=your-openai-key
AZURE_CONTENT_SAFETY_BLOCKLIST_NAME=prohibited-advertising-terms
```

## API Version Compatibility

The tool uses Azure OpenAI API version `2024-02-01` which is the stable version compatible with DALL-E 3 deployments. If you encounter version-related errors:

1. Check your deployment's supported API versions in Azure Portal
2. The API version is configured in `src/infrastructure/azure/dalle_client.py`
3. Avoid using preview versions unless specifically required

## Rate Limiting

DALL-E 3 deployments typically have rate limits (e.g., 3 requests per minute). If generating multiple campaigns:

1. The tool handles rate limiting gracefully
2. Failed generations will be logged but won't stop the process
3. Check the logs for rate limit errors if images aren't generating
4. Consider upgrading your Azure OpenAI deployment for higher limits

## Debug Logging

To see detailed logs of what's happening:

1. The tool uses `structlog` for structured logging
2. Logs show endpoint, deployment name, and API calls
3. Check the console output for detailed error messages
4. Key log events:
   - `Initializing DALL-E client` - Shows configuration
   - `Calling DALL-E API` - Shows actual API call parameters
   - `Failed to generate image` - Shows error details with context
