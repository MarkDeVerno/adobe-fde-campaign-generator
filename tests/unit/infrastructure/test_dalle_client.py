"""Simplified unit tests for DALLEClient."""
import pytest
from unittest.mock import AsyncMock, Mock, patch

from src.infrastructure.azure.dalle_client import DALLEClient


class TestDALLEClient:
    """Test DALLEClient infrastructure layer."""

    @pytest.fixture
    def mock_env(self):
        """Mock environment variables for Azure OpenAI."""
        with patch.dict('os.environ', {
            'AZURE_OPENAI_ENDPOINT': 'https://fake-endpoint.openai.azure.com',
            'AZURE_OPENAI_KEY': 'fake-api-key',
            'AZURE_OPENAI_DALLE_DEPLOYMENT_NAME': 'dall-e-3'
        }):
            yield

    def test_initialization_success(self, mock_env):
        """Test successful client initialization."""
        with patch('src.infrastructure.azure.dalle_client.AsyncAzureOpenAI'):
            client = DALLEClient()
            assert client.endpoint == 'https://fake-endpoint.openai.azure.com'
            assert client.api_key == 'fake-api-key'
            assert client.deployment_name == 'dall-e-3'

    def test_initialization_missing_credentials(self):
        """Test initialization fails without credentials."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                DALLEClient()
            assert "credentials not configured" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_generate_image_success(self, mock_env):
        """Test successful image generation."""
        mock_client = Mock()
        mock_response = Mock()
        mock_data = Mock()
        mock_data.url = "https://fake-url.com/image.png"
        mock_response.data = [mock_data]
        mock_client.images.generate = AsyncMock(return_value=mock_response)

        with patch('src.infrastructure.azure.dalle_client.AsyncAzureOpenAI', return_value=mock_client):
            client = DALLEClient()
            url = await client.generate_image("Test prompt")
            assert url == "https://fake-url.com/image.png"

    @pytest.mark.asyncio
    async def test_generate_image_failure(self, mock_env):
        """Test image generation failure."""
        mock_client = Mock()
        mock_client.images.generate = AsyncMock(side_effect=Exception("API error"))

        with patch('src.infrastructure.azure.dalle_client.AsyncAzureOpenAI', return_value=mock_client):
            client = DALLEClient()
            url = await client.generate_image("Test prompt")
            assert url is None
