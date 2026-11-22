"""Itinerary reviews: storage, consent-to-quote, admin export and alerts."""
from unittest.mock import AsyncMock

import httpx
import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.db import Database, Feedback
from app.main import app

ADMIN = {"X-Admin-Token": "test-admin-token"}


@pytest.fixture
def client():
    with TestClient(app) as c:
        async def wipe():
            async with app.state.db.engine.begin() as conn:
                await conn.execute(Feedback.__table__.delete())
        c.portal.call(wipe)
        yield c


def give(client, **overrides):
    body = {"helpful": True, "comment": "Loved the food tips for Kyoto", "destination": "Kyoto",
            "name": "Asha", "can_quote": True, "visitor_id": "visitor-0001", "source": "reddit"}
    body.update(overrides)
    return client.post("/api/feedback", json=body)


def listed(client, query=""):
    return client.get(f"/api/feedback{query}", headers=ADMIN).json()


def test_feedback_is_stored_and_listed(client):
    assert give(client).status_code == 201
    [row] = listed(client)
    assert row["helpful"] is True and row["destination"] == "Kyoto"
    assert row["can_quote"] is True and row["source"] == "reddit" and row["kind"] == "itinerary"


def test_thumbs_down_without_any_details_is_accepted(client):
    assert client.post("/api/feedback", json={"helpful": False}).status_code == 201
    [row] = listed(client)
    assert row["helpful"] is False and row["comment"] is None and row["can_quote"] is False


@pytest.mark.parametrize("overrides", [{"comment": None}, {"name": None}, {"name": "  "}])
def test_quote_consent_needs_a_comment_and_a_name(client, overrides):
    give(client, **overrides)
    assert listed(client)[0]["can_quote"] is False


def test_quotable_filter_and_newest_first(client):
    give(client, comment="first", can_quote=False)
    give(client, comment="second")
    assert [r["comment"] for r in listed(client)] == ["second", "first"]
    assert [r["comment"] for r in listed(client, "?quotable_only=true")] == ["second"]


@pytest.mark.parametrize("overrides", [
    {"helpful": "maybe"},
    {"comment": "x" * 1001},
    {"email": "not-an-email"},
    {"kind": "spam"},
    {"source": "<script>"},
])
def test_bad_input_is_rejected(client, overrides):
    assert give(client, **overrides).status_code == 422


def test_csv_export_escapes_formulas(client):
    give(client, comment="=IMPORTXML(\"http://evil\")")
    res = client.get("/api/feedback?format=csv", headers=ADMIN)
    assert res.status_code == 200 and res.headers["content-type"].startswith("text/csv")
    lines = res.content.decode("utf-8-sig").splitlines()
    assert lines[0] == "created_at,kind,helpful,comment,destination,name,email,can_quote,source"
    assert "'=IMPORTXML" in lines[1]


@pytest.mark.parametrize("headers", [{}, {"X-Admin-Token": "wrong"}])
def test_listing_requires_the_admin_token(client, headers):
    assert client.get("/api/feedback", headers=headers).status_code == 401


def test_feedback_sends_a_telegram_alert(client, monkeypatch):
    monkeypatch.setattr(settings, "TELEGRAM_BOT_TOKEN", "123:secret")
    monkeypatch.setattr(settings, "TELEGRAM_CHAT_ID", "42")
    post = AsyncMock(return_value=httpx.Response(200))
    monkeypatch.setattr(app.state.http_client, "post", post)
    give(client, helpful=False, comment="Too many temples, not enough food", email="Asha@Example.com")
    text = post.call_args.kwargs["json"]["text"]
    assert "👎 not useful" in text and "(Kyoto)" in text
    assert "Too many temples" in text and "asha@example.com" in text and "Can quote: yes" in text


def test_feedback_answers_503_without_a_database(client):
    app.state.db = Database(None)
    assert give(client).status_code == 503
