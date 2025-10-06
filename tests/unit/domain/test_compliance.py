"""Unit tests for Compliance domain models."""
import pytest

from src.domain.models.compliance import ComplianceResult


class TestComplianceResult:
    """Test ComplianceResult model."""

    def test_passed_compliance_result(self):
        """Test creating compliance result that passed."""
        result = ComplianceResult(
            passed=True,
            severity_scores={"hate": 0, "violence": 0},
            blocklist_matches=[],
            recommendation="Content passed all compliance checks"
        )
        assert result.passed is True
        assert result.has_violations is False
        assert result.severity_scores == {"hate": 0, "violence": 0}
        assert result.blocklist_matches == []
        assert result.recommendation == "Content passed all compliance checks"

    def test_failed_compliance_result(self):
        """Test creating compliance result that failed."""
        result = ComplianceResult(
            passed=False,
            severity_scores={"hate": 2, "violence": 0},
            blocklist_matches=["prohibited-term"],
            recommendation="Remove prohibited terms: prohibited-term"
        )
        assert result.passed is False
        assert result.has_violations is True
        assert result.severity_scores == {"hate": 2, "violence": 0}
        assert result.blocklist_matches == ["prohibited-term"]
        assert result.recommendation == "Remove prohibited terms: prohibited-term"

    def test_has_violations_property(self):
        """Test has_violations computed property."""
        # No violations
        result1 = ComplianceResult(
            passed=True,
            severity_scores={},
            blocklist_matches=[],
            recommendation="Passed"
        )
        assert result1.has_violations is False

        # Has violations (failed)
        result2 = ComplianceResult(
            passed=False,
            severity_scores={"hate": 1},
            blocklist_matches=[],
            recommendation="Failed"
        )
        assert result2.has_violations is True

    def test_compliance_result_with_multiple_blocklist_matches(self):
        """Test compliance result with multiple blocklist matches."""
        result = ComplianceResult(
            passed=False,
            severity_scores={"hate": 0, "violence": 0},
            blocklist_matches=["term1", "term2", "term3"],
            recommendation="Remove prohibited terms: term1, term2, term3"
        )
        assert len(result.blocklist_matches) == 3
        assert "term1" in result.blocklist_matches
        assert "term2" in result.blocklist_matches
        assert "term3" in result.blocklist_matches

    def test_compliance_result_severity_scores_types(self):
        """Test that severity scores accept various score types."""
        result = ComplianceResult(
            passed=True,
            severity_scores={
                "hate": 0,
                "violence": 1,
                "sexual": 2,
                "self_harm": 0
            },
            blocklist_matches=[],
            recommendation="Passed"
        )
        assert isinstance(result.severity_scores, dict)
        assert all(isinstance(v, int) for v in result.severity_scores.values())

    def test_compliance_result_empty_severity_scores(self):
        """Test compliance result with empty severity scores."""
        result = ComplianceResult(
            passed=True,
            severity_scores={},
            blocklist_matches=[],
            recommendation="No content to check"
        )
        assert result.severity_scores == {}
        assert result.has_violations is False
