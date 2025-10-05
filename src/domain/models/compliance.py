"""
Compliance domain model for content safety validation.
"""
from typing import List, Dict
from pydantic import BaseModel, Field


class ComplianceResult(BaseModel):
    """Result of content safety compliance check."""
    passed: bool = Field(..., description="Whether content passed compliance check")
    severity_scores: Dict[str, int] = Field(
        default_factory=dict,
        description="Severity scores for content categories (Hate, Violence, etc.)"
    )
    blocklist_matches: List[str] = Field(
        default_factory=list,
        description="Terms that matched prohibited advertising blocklist"
    )
    recommendation: str = Field(
        default="",
        description="Recommendation for handling compliance issues"
    )

    @property
    def has_violations(self) -> bool:
        """Check if there are any compliance violations."""
        return not self.passed or len(self.blocklist_matches) > 0
