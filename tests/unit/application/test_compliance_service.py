"""Unit tests for ComplianceService."""
import pytest
from unittest.mock import AsyncMock, Mock, patch

from src.application.services.compliance_service import ComplianceService
from src.domain.models.compliance import ComplianceResult


class TestComplianceService:
    """Test ComplianceService application service."""

    @pytest.fixture
    def mock_azure_client(self):
        """Create mock Azure Content Safety client."""
        mock_client = Mock()
        mock_client.analyze_campaign_message = Mock()
        return mock_client

    @pytest.fixture
    def compliance_service(self, mock_azure_client):
        """Create ComplianceService with mocked Azure client."""
        with patch('src.application.services.compliance_service.AzureContentSafety', return_value=mock_azure_client):
            service = ComplianceService()
            return service

    @pytest.mark.asyncio
    async def test_check_message_success(self, compliance_service, mock_azure_client):
        """Test successful compliance check."""
        # Arrange
        test_message = "Great product for sustainable living"
        expected_result = ComplianceResult(
            passed=True,
            severity_scores={"hate": 0, "violence": 0},
            blocklist_matches=[],
            recommendation="Content passed all checks"
        )
        mock_azure_client.analyze_campaign_message.return_value = expected_result

        # Act
        result = await compliance_service.check_message(test_message)

        # Assert
        assert result.passed is True
        assert result.has_violations is False
        mock_azure_client.analyze_campaign_message.assert_called_once_with(test_message)

    @pytest.mark.asyncio
    async def test_check_message_with_violations(self, compliance_service, mock_azure_client):
        """Test compliance check with violations."""
        # Arrange
        test_message = "Test message with violations"
        expected_result = ComplianceResult(
            passed=False,
            severity_scores={"hate": 2, "violence": 0},
            blocklist_matches=["prohibited-term"],
            recommendation="Remove prohibited terms"
        )
        mock_azure_client.analyze_campaign_message.return_value = expected_result

        # Act
        result = await compliance_service.check_message(test_message)

        # Assert
        assert result.passed is False
        assert result.has_violations is True
        assert len(result.blocklist_matches) == 1

    @pytest.mark.asyncio
    async def test_check_message_with_unavailable_client(self):
        """Test compliance check when Azure client is unavailable."""
        # Arrange
        with patch('src.application.services.compliance_service.AzureContentSafety', side_effect=Exception("Service unavailable")):
            service = ComplianceService()

        # Act
        result = await service.check_message("Test message")

        # Assert
        assert result.passed is False
        assert "unavailable" in result.recommendation.lower()

    @pytest.mark.asyncio
    async def test_check_message_with_exception(self, compliance_service, mock_azure_client):
        """Test compliance check when Azure service throws exception."""
        # Arrange
        mock_azure_client.analyze_campaign_message.side_effect = Exception("API error")

        # Act
        result = await compliance_service.check_message("Test message")

        # Assert
        assert result.passed is False
        assert "error" in result.recommendation.lower()

    def test_get_compliance_recommendations_passed(self, compliance_service):
        """Test recommendations for passed compliance result."""
        # Arrange
        result = ComplianceResult(
            passed=True,
            severity_scores={},
            blocklist_matches=[],
            recommendation="Passed"
        )

        # Act
        recommendations = compliance_service.get_compliance_recommendations(result)

        # Assert
        assert "status" in recommendations
        assert "compliant" in recommendations["status"].lower()

    def test_get_compliance_recommendations_high_severity(self, compliance_service):
        """Test recommendations for high severity violations."""
        # Arrange
        result = ComplianceResult(
            passed=False,
            severity_scores={"hate": 4, "violence": 5},
            blocklist_matches=[],
            recommendation="High severity detected"
        )

        # Act
        recommendations = compliance_service.get_compliance_recommendations(result)

        # Assert
        assert "severity" in recommendations
        assert "hate" in recommendations["severity"].lower()
        assert "violence" in recommendations["severity"].lower()

    def test_get_compliance_recommendations_blocklist_matches(self, compliance_service):
        """Test recommendations for blocklist violations."""
        # Arrange
        result = ComplianceResult(
            passed=False,
            severity_scores={},
            blocklist_matches=["term1", "term2"],
            recommendation="Blocklist match"
        )

        # Act
        recommendations = compliance_service.get_compliance_recommendations(result)

        # Assert
        assert "blocklist" in recommendations
        assert "term1" in recommendations["blocklist"]
        assert "term2" in recommendations["blocklist"]

    def test_get_compliance_recommendations_general(self, compliance_service):
        """Test general recommendation is included."""
        # Arrange
        result = ComplianceResult(
            passed=False,
            severity_scores={},
            blocklist_matches=[],
            recommendation="General recommendation text"
        )

        # Act
        recommendations = compliance_service.get_compliance_recommendations(result)

        # Assert
        assert "general" in recommendations
        assert recommendations["general"] == "General recommendation text"

    def test_get_compliance_recommendations_combined(self, compliance_service):
        """Test recommendations with multiple violation types."""
        # Arrange
        result = ComplianceResult(
            passed=False,
            severity_scores={"hate": 4},
            blocklist_matches=["prohibited-word"],
            recommendation="Multiple issues detected"
        )

        # Act
        recommendations = compliance_service.get_compliance_recommendations(result)

        # Assert
        assert "severity" in recommendations
        assert "blocklist" in recommendations
        assert "general" in recommendations
        assert len(recommendations) == 3
