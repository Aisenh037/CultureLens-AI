"""Step-1 wedge experiments: waitlist signups, funnel events and a private summary.

Privacy: we store only what the visitor types (email, optional name/role/note),
an anonymous random visitor id generated in their browser, and the campaign
source from the URL. No IP addresses, no user agents.
"""
import hmac
import logging
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response
from sqlalchemy import distinct, func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db import ExperimentEvent, WaitlistSignup
from app.rate_limit import limiter
from app.schemas.experiments import WEDGES, EventRequest, ExperimentSummary, SignupRequest, WedgeStats

logger = logging.getLogger("app.routers.experiments")

router = APIRouter(prefix="/api/experiments", tags=["experiments"])


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    db = getattr(request.app.state, "db", None)
    if db is None or not db.enabled:
        raise HTTPException(status_code=503, detail="Signups are not available right now.")
    async for session in db.session():
        yield session


def _insert(session: AsyncSession):
    return pg_insert if session.bind.dialect.name == "postgresql" else sqlite_insert


@router.post("/waitlist", status_code=201)
@limiter.limit(settings.SIGNUP_RATE_LIMIT)
async def join_waitlist(payload: SignupRequest, request: Request, response: Response,
                        session: AsyncSession = Depends(get_session)):
    if not payload.consent:
        raise HTTPException(status_code=422, detail="Please agree to be emailed about the launch.")

    email = payload.email.strip().lower()
    stmt = _insert(session)(WaitlistSignup).values(
        wedge=payload.wedge, email=email, name=payload.name, role=payload.role,
        note=payload.note, source=payload.source, wants_interview=payload.wants_interview,
    ).on_conflict_do_nothing(index_elements=["wedge", "email"])
    result = await session.execute(stmt)

    if result.rowcount and payload.visitor_id:
        session.add(ExperimentEvent(wedge=payload.wedge, event="signup",
                                    visitor_id=payload.visitor_id, source=payload.source))
    await session.commit()
    # Same answer for new and existing emails, so the form can't be used to
    # check whether someone is on the list.
    return {"status": "ok"}


@router.post("/events", status_code=204)
@limiter.limit(settings.EVENT_RATE_LIMIT)
async def record_event(payload: EventRequest, request: Request, session: AsyncSession = Depends(get_session)):
    session.add(ExperimentEvent(wedge=payload.wedge, event=payload.event,
                                visitor_id=payload.visitor_id, source=payload.source))
    await session.commit()
    return Response(status_code=204)


def _require_admin(x_admin_token: str | None) -> None:
    expected = settings.ADMIN_TOKEN
    # Not configured: behave as if the route doesn't exist.
    if not expected:
        raise HTTPException(status_code=404, detail="Not Found")
    if not x_admin_token or not hmac.compare_digest(x_admin_token, expected):
        raise HTTPException(status_code=401, detail="Unauthorized")


@router.get("/summary", response_model=ExperimentSummary)
async def summary(x_admin_token: str | None = Header(default=None), session: AsyncSession = Depends(get_session)):
    """Per-wedge funnel: unique visitors -> unique pay-clickers -> signups."""
    _require_admin(x_admin_token)

    event_counts = await session.execute(
        select(ExperimentEvent.wedge, ExperimentEvent.event, func.count(distinct(ExperimentEvent.visitor_id)))
        .group_by(ExperimentEvent.wedge, ExperimentEvent.event)
    )
    uniques = {(w, e): n for w, e, n in event_counts}

    signup_counts = await session.execute(
        select(WaitlistSignup.wedge, func.count(), func.count().filter(WaitlistSignup.wants_interview.is_(True)))
        .group_by(WaitlistSignup.wedge)
    )
    signups = {w: (n, i) for w, n, i in signup_counts}

    def rate(part: int, whole: int):
        return round(part / whole, 4) if whole else None

    wedges = []
    for w in WEDGES:
        visitors = uniques.get((w, "view"), 0)
        clickers = uniques.get((w, "pay_click"), 0)
        n_signups, volunteers = signups.get(w, (0, 0))
        wedges.append(WedgeStats(
            wedge=w, visitors=visitors, pay_clickers=clickers, signups=n_signups,
            interview_volunteers=volunteers,
            pay_click_rate=rate(clickers, visitors), signup_rate=rate(n_signups, visitors),
        ))
    return ExperimentSummary(wedges=wedges)
