from datetime import datetime
from typing import Annotated, Literal, Optional

from pydantic import BaseModel, EmailStr, Field, StringConstraints

# The three Step-1 wedges. A landing page exists for each at /for/<wedge>.
Wedge = Literal["travellers-abroad", "tour-operators", "heritage-stories"]
WEDGES: tuple[str, ...] = ("travellers-abroad", "tour-operators", "heritage-stories")

# view: landing page opened; pay_click: pressed the price button (fake door);
# signup is recorded by the server when a waitlist row is created.
ClientEvent = Literal["view", "pay_click"]

Short = Annotated[str, StringConstraints(strip_whitespace=True, max_length=100)]
VisitorId = Annotated[str, StringConstraints(strip_whitespace=True, min_length=8, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")]
Source = Annotated[str, StringConstraints(strip_whitespace=True, max_length=100, pattern=r"^[A-Za-z0-9_.\-]*$")]


class SignupRequest(BaseModel):
    wedge: Wedge
    email: EmailStr
    name: Optional[Short] = None
    role: Optional[Short] = Field(default=None, description="e.g. tour operator, student, family traveller")
    note: Optional[Annotated[str, StringConstraints(strip_whitespace=True, max_length=500)]] = None
    wants_interview: bool = False
    consent: bool = Field(..., description="Agreed to be emailed about this launch")
    visitor_id: Optional[VisitorId] = None
    source: Optional[Source] = None


class EventRequest(BaseModel):
    wedge: Wedge
    event: ClientEvent
    visitor_id: VisitorId
    source: Optional[Source] = None


class WedgeStats(BaseModel):
    wedge: str
    visitors: int
    pay_clickers: int
    signups: int
    interview_volunteers: int
    pay_click_rate: Optional[float] = Field(None, description="pay_clickers / visitors")
    signup_rate: Optional[float] = Field(None, description="signups / visitors")


class ExperimentSummary(BaseModel):
    wedges: list[WedgeStats]


class SignupOut(BaseModel):
    created_at: datetime
    wedge: str
    email: str
    name: Optional[str] = None
    role: Optional[str] = None
    note: Optional[str] = None
    wants_interview: bool
    source: Optional[str] = None
