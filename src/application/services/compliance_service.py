"""
Compliance service for content safety validation.
"""
from typing import Dict, Optional
import structlog

from src.domain.models.compliance import ComplianceResult
from src.infrastructure.azure.content_safety_client import ContentSafetyService as AzureContentSafety

logger = structlog.get_logger()


class ComplianceService:
    """Application service for campaign content compliance checking."""

    def __init__(self):
        """Initialize compliance service with Azure Content Safety client."""
        try:
            self.azure_client = AzureContentSafety()
            logger.info("Compliance service initialized")
        except Exception as e:
            logger.error("Failed to initialize Azure Content Safety client", error=str(e))
            self.azure_client = None

    async def check_message(self, message: str) -> ComplianceResult:
        """
        Check campaign message for content safety compliance.

        Args:
            message: Campaign message text to analyze

        Returns:
            ComplianceResult with safety analysis and recommendations
        """
        if not self.azure_client:
            logger.error("Azure Content Safety client not available")
            return ComplianceResult(
                passed=False,
                severity_scores={},
                blocklist_matches=[],
                recommendation="Content Safety service unavailable"
            )

        try:
            logger.info("Checking message compliance", message_length=len(message))

            # Call Azure Content Safety (synchronous, but wrapped in async for consistency)
            result = self.azure_client.analyze_campaign_message(message)

            logger.info(
                "Compliance check complete",
                passed=result.passed,
                violations=result.has_violations,
                blocklist_matches_count=len(result.blocklist_matches)
            )

            return result

        except Exception as e:
            logger.error("Compliance check failed", error=str(e))
            return ComplianceResult(
                passed=False,
                severity_scores={},
                blocklist_matches=[],
                recommendation=f"Compliance check error: {str(e)}"
            )

    def get_compliance_recommendations(self, result: ComplianceResult) -> Dict[str, str]:
        """
        Generate human-readable compliance recommendations.

        Args:
            result: ComplianceResult from check_message

        Returns:
            Dictionary with recommendation categories and suggestions
        """
        recommendations = {}

        if result.passed:
            recommendations["status"] = "Campaign message is compliant"
            return recommendations

        # Severity issues
        high_severity = [
            category for category, score in result.severity_scores.items()
            if score >= 4
        ]

        if high_severity:
            recommendations["severity"] = (
                f"High severity detected in: {', '.join(high_severity)}. "
                f"Please revise campaign message to reduce content in these categories."
            )

        # Blocklist issues
        if result.blocklist_matches:
            recommendations["blocklist"] = (
                f"Prohibited advertising terms detected: {', '.join(result.blocklist_matches)}. "
                f"These terms violate advertising standards and must be removed."
            )

        # General recommendation
        if result.recommendation:
            recommendations["general"] = result.recommendation

        return recommendations
