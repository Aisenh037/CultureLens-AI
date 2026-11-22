"""Waitlist, funnel events and the admin summary for the Step-1 wedge tests."""
from unittest.mock import AsyncMock

import httpx
import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.db import Database, ExperimentEvent, WaitlistSignup, normalise_url
from app.main import app

ADMIN = {"X-Admin-Token": "test-admin-token"}


@pytest.fixture
def client():
    # Entering the context runs the lifespan (creates the tables). Rows are
    # cleared first so the suite also runs against a persistent Postgres.
    with TestClient(app) as c:
        async def wipe():
            async with app.state.db.engine.begin() as conn:
                for table in (WaitlistSignup.__table__, ExperimentEvent.__table__):
                    await conn.execute(table.delete())
        c.portal.call(wipe)
        yield c


def signup(client, **overrides):
    body = {"wedge": "travellers-abroad", "email": "Asha@Example.com", "consent": True,
            "visitor_id": "visitor-0001", "source": "reddit"}
    body.update(overrides)
    return client.post("/api/experiments/waitlist", json=body)


def event(client, wedge, kind, visitor):
    return client.post("/api/experiments/events", json={"wedge": wedge, "event": kind, "visitor_id": visitor})


# --- Waitlist -----------------------------------------------------------------

def test_signup_is_stored(client):
    res = signup(client, name="Asha", role="student", note="Going to Japan in May", wants_interview=True)
    assert res.status_code == 201
    assert res.json() == {"status": "ok"}
    summary = client.get("/api/experiments/summary", headers=ADMIN).json()
    abroad = next(w for w in summary["wedges"] if w["wedge"] == "travellers-abroad")
    assert abroad["signups"] == 1
    assert abroad["interview_volunteers"] == 1


def test_duplicate_email_is_not_revealed_or_double_counted(client):
    first = signup(client)
    again = signup(client, email="  asha@example.COM ")  # same address, different case/spacing
    assert first.status_code == again.status_code == 201
    assert first.json() == again.json()  # no "already registered" leak
    summary = client.get("/api/experiments/summary", headers=ADMIN).json()
    assert next(w for w in summary["wedges"] if w["wedge"] == "travellers-abroad")["signups"] == 1


def test_same_email_can_join_different_wedges(client):
    signup(client, wedge="travellers-abroad")
    signup(client, wedge="heritage-stories")
    counts = {w["wedge"]: w["signups"] for w in client.get("/api/experiments/summary", headers=ADMIN).json()["wedges"]}
    assert counts == {"travellers-abroad": 1, "tour-operators": 0, "heritage-stories": 1}


@pytest.mark.parametrize("overrides", [
    {"consent": False},
    {"email": "not-an-email"},
    {"wedge": "space-tourism"},
    {"name": "x" * 101},
    {"note": "x" * 501},
    {"visitor_id": "bad id with spaces"},
    {"source": "<script>"},
])
def test_signup_rejects_bad_input(client, overrides):
    assert signup(client, **overrides).status_code == 422


# --- Events -------------------------------------------------------------------

def test_events_are_recorded(client):
    assert event(client, "tour-operators", "view", "visitor-aaaa").status_code == 204
    assert event(client, "tour-operators", "pay_click", "visitor-aaaa").status_code == 204


@pytest.mark.parametrize("kind", ["signup", "purchase", ""])
def test_clients_cannot_send_other_event_kinds(client, kind):
    """Signups are counted by the server from real waitlist rows, never claimed by the client."""
    assert event(client, "tour-operators", kind, "visitor-aaaa").status_code == 422


# --- Summary ------------------------------------------------------------------

def test_summary_counts_unique_visitors_and_rates(client):
    for v in ("visitor-0001", "visitor-0002", "visitor-0003", "visitor-0004"):
        event(client, "heritage-stories", "view", v)
    event(client, "heritage-stories", "view", "visitor-0001")       # repeat view, same visitor
    event(client, "heritage-stories", "pay_click", "visitor-0001")
    event(client, "heritage-stories", "pay_click", "visitor-0001")  # double click, same visitor
    signup(client, wedge="heritage-stories", visitor_id="visitor-0001")

    stats = next(w for w in client.get("/api/experiments/summary", headers=ADMIN).json()["wedges"]
                 if w["wedge"] == "heritage-stories")
    assert stats == {
        "wedge": "heritage-stories", "visitors": 4, "pay_clickers": 1, "signups": 1,
        "interview_volunteers": 0, "pay_click_rate": 0.25, "signup_rate": 0.25,
    }


def test_summary_with_no_traffic_has_no_rates(client):
    stats = client.get("/api/experiments/summary", headers=ADMIN).json()["wedges"]
    assert [w["wedge"] for w in stats] == ["travellers-abroad", "tour-operators", "heritage-stories"]
    assert all(w["pay_click_rate"] is None and w["signup_rate"] is None for w in stats)


@pytest.mark.parametrize("headers", [{}, {"X-Admin-Token": "wrong"}])
def test_summary_requires_the_admin_token(client, headers):
    assert client.get("/api/experiments/summary", headers=headers).status_code == 401


def test_summary_is_hidden_when_no_token_is_configured(client, monkeypatch):
    monkeypatch.setattr(settings, "ADMIN_TOKEN", "")
    assert client.get("/api/experiments/summary", headers=ADMIN).status_code == 404


# --- Without a database -------------------------------------------------------

def test_endpoints_answer_503_without_a_database(client):
    app.state.db = Database(None)
    assert signup(client).status_code == 503
    assert event(client, "tour-operators", "view", "visitor-aaaa").status_code == 503


def test_travel_api_unaffected_without_a_database(client):
    app.state.db = Database(None)
    assert client.get("/").status_code == 200


@pytest.mark.parametrize("raw,expected", [
    ("postgres://u:p@host:5432/db", "postgresql+asyncpg://u:p@host:5432/db"),
    ("postgresql://u:p@host/db", "postgresql+asyncpg://u:p@host/db"),
    ("postgresql+asyncpg://u:p@host/db", "postgresql+asyncpg://u:p@host/db"),
    ("sqlite+aiosqlite://", "sqlite+aiosqlite://"),
])
def test_render_database_urls_are_normalised(raw, expected):
    assert normalise_url(raw) == expected


# --- Signup export ------------------------------------------------------------

def test_signups_list_newest_first_with_filters(client):
    signup(client, email="a@example.com", wedge="tour-operators", role="Agency, Bhopal", wants_interview=True)
    signup(client, email="b@example.com", wedge="tour-operators")
    signup(client, email="c@example.com", wedge="heritage-stories", wants_interview=True)

    everyone = client.get("/api/experiments/signups", headers=ADMIN).json()
    assert [r["email"] for r in everyone] == ["c@example.com", "b@example.com", "a@example.com"]
    assert everyone[2]["role"] == "Agency, Bhopal" and everyone[2]["source"] == "reddit"

    ops = client.get("/api/experiments/signups?wedge=tour-operators", headers=ADMIN).json()
    assert {r["email"] for r in ops} == {"a@example.com", "b@example.com"}

    callers = client.get("/api/experiments/signups?interview_only=true", headers=ADMIN).json()
    assert {r["email"] for r in callers} == {"a@example.com", "c@example.com"}


def test_signups_csv_is_excel_friendly_and_injection_safe(client):
    signup(client, email="x@example.com", name="=HYPERLINK(\"http://evil\")", note="+91 98765 43210")
    res = client.get("/api/experiments/signups?format=csv", headers=ADMIN)
    assert res.status_code == 200
    assert res.headers["content-type"].startswith("text/csv")
    assert "attachment" in res.headers["content-disposition"]
    body = res.content.decode("utf-8-sig").splitlines()
    assert body[0] == "created_at,wedge,email,name,role,note,wants_interview,source"
    assert "'=HYPERLINK" in body[1] and "'+91 98765 43210" in body[1]


@pytest.mark.parametrize("headers", [{}, {"X-Admin-Token": "wrong"}])
def test_signups_require_the_admin_token(client, headers):
    signup(client)
    assert client.get("/api/experiments/signups", headers=headers).status_code == 401
    assert client.get("/api/experiments/signups?format=csv", headers=headers).status_code == 401


def test_signups_rejects_unknown_wedge(client):
    assert client.get("/api/experiments/signups?wedge=nope", headers=ADMIN).status_code == 422


# --- Telegram alerts ----------------------------------------------------------

@pytest.fixture
def telegram(client, monkeypatch):
    monkeypatch.setattr(settings, "TELEGRAM_BOT_TOKEN", "123:secret")
    monkeypatch.setattr(settings, "TELEGRAM_CHAT_ID", "42")
    post = AsyncMock(return_value=httpx.Response(200))
    monkeypatch.setattr(app.state.http_client, "post", post)
    return post


def test_new_signup_sends_one_alert(client, telegram):
    signup(client, name="Ravi", role="Agency, Indore", note="40 trips a month", wants_interview=True,
           wedge="tour-operators")
    signup(client, wedge="tour-operators", name="Ravi")  # same email again: no second alert
    telegram.assert_awaited_once()
    url = telegram.call_args.args[0]
    body = telegram.call_args.kwargs["json"]
    assert url == "https://api.telegram.org/bot123:secret/sendMessage"
    assert body["chat_id"] == "42" and "parse_mode" not in body
    text = body["text"]
    assert "Tour operators" in text and "asha@example.com" in text and "40 trips a month" in text
    assert "reply within the hour" in text and "Source: reddit" in text


def test_alert_failure_does_not_break_signup(client, telegram):
    telegram.side_effect = httpx.ConnectError("down")
    assert signup(client).status_code == 201


def test_no_alert_when_not_configured(client, monkeypatch):
    monkeypatch.setattr(settings, "TELEGRAM_BOT_TOKEN", "")
    post = AsyncMock()
    monkeypatch.setattr(app.state.http_client, "post", post)
    assert signup(client).status_code == 201
    post.assert_not_awaited()
