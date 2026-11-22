"""Step-1 wedge experiments: waitlist signups, funnel events and a private summary.

Privacy: we store only what the visitor types (email, optional name/role/note),
an anonymous random visitor id generated in their browser, and the campaign
source from the URL. No IP addresses, no user agents.
"""
import csv
import hmac
import io
import logging
from collections.abc import AsyncIterator
from typing import Literal, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, Request, Response
from sqlalchemy import distinct, func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db import ExperimentEvent, WaitlistSignup
from app.rate_limit import limiter
from app.services.notify import format_signup, send_signup_alert
from app.schemas.experiments import (
    WEDGES, EventRequest, ExperimentSummary, SignupOut, SignupRequest, Wedge, WedgeStats,
)

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
                        background: BackgroundTasks, session: AsyncSession = Depends(get_session)):
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

    if result.rowcount:  # new signup, not a repeat
        text = format_signup(payload.wedge, email, payload.name, payload.role, payload.note,
                             payload.wants_interview, payload.source)
        # Sent after the response, so a slow Telegram never delays the visitor.
        background.add_task(send_signup_alert, request.app.state.http_client, text)
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


def require_admin(x_admin_token: str | None) -> None:
    expected = settings.ADMIN_TOKEN
    # Not configured: behave as if the route doesn't exist.
    if not expected:
        raise HTTPException(status_code=404, detail="Not Found")
    if not x_admin_token or not hmac.compare_digest(x_admin_token, expected):
        raise HTTPException(status_code=401, detail="Unauthorized")


@router.get("/summary", response_model=ExperimentSummary)
async def summary(x_admin_token: str | None = Header(default=None), session: AsyncSession = Depends(get_session)):
    """Per-wedge funnel: unique visitors -> unique pay-clickers -> signups."""
    require_admin(x_admin_token)

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


SIGNUP_FIELDS = ("created_at", "wedge", "email", "name", "role", "note", "wants_interview", "source")


def csv_safe(value) -> str:
    """Stop spreadsheet apps treating visitor-typed text as a formula (CSV injection)."""
    text = "" if value is None else str(value)
    return "'" + text if text[:1] in ("=", "+", "-", "@", "\t", "\r") else text


@router.get("/signups", response_model=list[SignupOut])
async def list_signups(
    wedge: Optional[Wedge] = None,
    interview_only: bool = False,
    format: Literal["json", "csv"] = "json",
    x_admin_token: str | None = Header(default=None),
    session: AsyncSession = Depends(get_session),
):
    """Everyone on the waitlist, newest first, so you can reach out. Admin only."""
    require_admin(x_admin_token)

    query = select(WaitlistSignup).order_by(WaitlistSignup.created_at.desc(), WaitlistSignup.id.desc())
    if wedge:
        query = query.where(WaitlistSignup.wedge == wedge)
    if interview_only:
        query = query.where(WaitlistSignup.wants_interview.is_(True))
    rows = (await session.execute(query)).scalars().all()

    if format == "json":
        return [SignupOut.model_validate(r, from_attributes=True) for r in rows]

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(SIGNUP_FIELDS)
    for r in rows:
        writer.writerow([csv_safe(getattr(r, f).isoformat() if f == "created_at" else getattr(r, f))
                         for f in SIGNUP_FIELDS])
    return Response(
        content="\ufeff" + buffer.getvalue(),  # BOM so Excel reads ₹ and non-Latin names correctly
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="culturelens-signups.csv"',
                 "Cache-Control": "no-store"},
    )
