from pydantic import BaseModel, Field, field_validator

from models.review_action import ReviewAction


class DecisionRequest(BaseModel):
    """
    Request body for submitting a review decision.
    """

    session_id: str = Field(
        min_length=1,
        description="Unique review session identifier",
    )

    action: ReviewAction = Field(
        description="User decision for the current violation",
    )

    edited_code: str = Field(
        default="",
        description="Replacement code when action is EDIT",
    )

    comment: str = Field(
        default="",
        max_length=1000,
        description="Optional reviewer comment",
    )

    @field_validator("session_id")
    @classmethod
    def validate_session_id(cls, value: str):
        value = value.strip()

        if not value:
            raise ValueError("Session ID cannot be empty.")

        return value

    @field_validator("edited_code")
    @classmethod
    def clean_code(cls, value: str):
        return value.rstrip()

    @field_validator("comment")
    @classmethod
    def clean_comment(cls, value: str):
        return value.strip()

    @property
    def requires_code(self):
        """
        Returns True if this request should
        contain edited source code.
        """

        return self.action == ReviewAction.EDIT