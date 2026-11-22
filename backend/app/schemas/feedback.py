from datetime import datetime
from typing import Annotated, Literal, Optional

from pydantic import BaseModel, EmailStr, Field, StringConstraints

from app.schemas.experiments import Source, VisitorId


class FeedbackRequest(BaseModel):
    kind: Literal["itinerary", "general"] = "itinerary"
    helpful: bool
    comment: Optional[Annotated[str, StringConstraints(strip_whitespace=True, max_length=1000)]] = None
    destination: Optional[Annotated[str, StringConstraints(strip_whitespace=True, max_length=120)]] = None
    name: Optional[Annotated[str, StringConstraints(strip_whitespace=True, max_length=100)]] = None
    email: Optional[EmailStr] = None
    can_quote: bool = Field(False, description="Agreed that the comment may be quoted publicly with their name")
    visitor_id: Optional[VisitorId] = None
    source: Optional[Source] = None


class FeedbackOut(BaseModel):
    created_at: datetime
    kind: str
    helpful: bool
    comment: Optional[str] = None
    destination: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    can_quote: bool
    source: Optional[str] = None
