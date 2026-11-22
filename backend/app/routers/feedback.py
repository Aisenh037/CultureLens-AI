"""Reviews of generated itineraries: the real-world feedback loop for Step 1.

Stored with only what the visitor typed, plus the anonymous visitor id and
campaign source. A comment is quotable only if the visitor ticked consent.
"""
import csv
import io
from typing import Literal, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, Header, Request, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db import Feedback
from app.rate_limit import limiter
from app.routers.experiments import csv_safe, get_session, require_admin
from app.schemas.feedback import FeedbackOut, FeedbackRequest
from app.services.notify import format_feedback, send_signup_alert

router = APIRouter(prefix="/api/feedback", tags=["feedback"])

FIELDS = ("created_at", "kind", "helpful", "comment", "destination", "name", "email", "can_quote", "source")


@router.post("", status_code=201)
@limiter.limit(settings.FEEDBACK_RATE_LIMIT)
async def give_feedback(payload: FeedbackRequest, request: Request, response: Response,
                        background: BackgroundTasks, session: AsyncSession = Depends(get_session)):
    email = payload.email.strip().lower() if payload.email else None
    # Quoting needs something to quote and someone to attribute it to.
    can_quote = bool(payload.can_quote and payload.comment and payload.name)
    session.add(Feedback(
        kind=payload.kind, helpful=payload.helpful, comment=payload.comment or None,
        destination=payload.destination or None, name=payload.name or None, email=email,
        can_quote=can_quote, visitor_id=payload.visitor_id, source=payload.source,
    ))
    await session.commit()
    text = format_feedback(payload.helpful, payload.comment, payload.destination, payload.name,
                           email, can_quote, payload.kind)
    background.add_task(send_signup_alert, request.app.state.http_client, text)
    return {"status": "ok"}


@router.get("", response_model=list[FeedbackOut])
async def list_feedback(
    quotable_only: bool = False,
    format: Literal["json", "csv"] = "json",
    x_admin_token: Optional[str] = Header(default=None),
    session: AsyncSession = Depends(get_session),
):
    """All feedback, newest first. Admin only."""
    require_admin(x_admin_token)
    query = select(Feedback).order_by(Feedback.created_at.desc(), Feedback.id.desc())
    if quotable_only:
        query = query.where(Feedback.can_quote.is_(True))
    rows = (await session.execute(query)).scalars().all()
    if format == "json":
        return [FeedbackOut.model_validate(r, from_attributes=True) for r in rows]
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(FIELDS)
    for r in rows:
        writer.writerow([csv_safe(getattr(r, f).isoformat() if f == "created_at" else getattr(r, f)) for f in FIELDS])
    return Response(content="﻿" + buffer.getvalue(), media_type="text/csv; charset=utf-8",
                    headers={"Content-Disposition": 'attachment; filename="culturelens-feedback.csv"',
                             "Cache-Control": "no-store"})
