from pydantic import BaseModel, Field

from models.review_action import ReviewAction


class DecisionRequest(BaseModel):
    session_id: str = Field(min_length=1)
    action: ReviewAction
    edited_code: str = ""
    comment: str = ""
