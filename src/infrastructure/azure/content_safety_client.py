"""
Azure AI Content Safety client for content moderation.
"""
import os
from typing import List
from azure.ai.contentsafety import ContentSafetyClient
from azure.ai.contentsafety.models import AnalyzeTextOptions, TextCategory
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
import structlog

from src.domain.models.compliance import ComplianceResult

logger = structlog.get_logger()


class ContentSafetyService:
    """Service for content moderation using Azure AI Content Safety."""

    def __init__(self):
        """Initialize Content Safety client with Azure credentials."""
        endpoint = os.getenv("AZURE_CONTENT_SAFETY_ENDPOINT")
        key = os.getenv("AZURE_CONTENT_SAFETY_KEY")

        if not endpoint or not key:
            raise ValueError("Azure Content Safety credentials not configured in .env")

        self.client = ContentSafetyClient(endpoint, AzureKeyCredential(key))
        self.blocklist_name = os.getenv("AZURE_CONTENT_SAFETY_BLOCKLIST_NAME", "prohibited-advertising-terms")

    def analyze_campaign_message(self, message: str) -> ComplianceResult:
        """
        Analyze campaign message for content safety compliance.

        Args:
            message: Campaign message text to analyze

        Returns:
            ComplianceResult with safety analysis
        """
        try:
            logger.info("Analyzing content safety", message_length=len(message))

            # Prepare analysis request
            request = AnalyzeTextOptions(
                text=message,
                categories=[
                    TextCategory.HATE,
                    TextCategory.SELF_HARM,
                    TextCategory.SEXUAL,
                    TextCategory.VIOLENCE
                ],
                blocklist_names=[self.blocklist_name] if self.blocklist_name else None,
                output_type="FourSeverityLevels"  # 0, 2, 4, 6 scores
            )

            # Analyze text
            response = self.client.analyze_text(request)

            # Extract severity scores
            severity_scores = {
                "Hate": response.hate_result.severity if hasattr(response, 'hate_result') else 0,
                "SelfHarm": response.self_harm_result.severity if hasattr(response, 'self_harm_result') else 0,
                "Sexual": response.sexual_result.severity if hasattr(response, 'sexual_result') else 0,
                "Violence": response.violence_result.severity if hasattr(response, 'violence_result') else 0
            }

            # Extract blocklist matches
            blocklist_matches = []
            if hasattr(response, 'blocklists_match_results'):
                for match in response.blocklists_match_results:
                    if hasattr(match, 'blocklist_items_matched'):
                        for item in match.blocklist_items_matched:
                            if hasattr(item, 'text'):
                                blocklist_matches.append(item.text)

            # Determine if passed (no high severity, no blocklist matches)
            max_severity = max(severity_scores.values())
            passed = max_severity < 4 and len(blocklist_matches) == 0  # Severity < 4 is acceptable

            # Generate recommendation
            if not passed:
                if len(blocklist_matches) > 0:
                    recommendation = f"Campaign message contains prohibited terms: {', '.join(blocklist_matches)}"
                else:
                    high_categories = [cat for cat, score in severity_scores.items() if score >= 4]
                    recommendation = f"Campaign message has high severity in: {', '.join(high_categories)}"
            else:
                recommendation = "Campaign message passed all compliance checks"

            result = ComplianceResult(
                passed=passed,
                severity_scores=severity_scores,
                blocklist_matches=blocklist_matches,
                recommendation=recommendation
            )

            logger.info(
                "Content safety analysis complete",
                passed=passed,
                severity_scores=severity_scores,
                blocklist_matches_count=len(blocklist_matches)
            )

            return result

        except HttpResponseError as e:
            logger.error("Content Safety API error", error=str(e))
            # Return conservative result (fail-safe)
            return ComplianceResult(
                passed=False,
                severity_scores={},
                blocklist_matches=[],
                recommendation=f"Content Safety API error: {str(e)}"
            )
        except Exception as e:
            logger.error("Unexpected error in content safety analysis", error=str(e))
            return ComplianceResult(
                passed=False,
                severity_scores={},
                blocklist_matches=[],
                recommendation=f"Error analyzing content: {str(e)}"
            )
