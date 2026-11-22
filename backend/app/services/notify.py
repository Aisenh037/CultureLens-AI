"""Telegram alert when someone joins a waitlist, so they get a reply within the hour.

Unconfigured (no TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID): does nothing.
Failures are logged and swallowed: an alert must never break a signup.
"""
import logging

import httpx

from app.config import settings

logger = logging.getLogger("app.services.notify")

# Telegram puts the bot token in the URL path, and httpx logs request URLs at
# INFO. Keep httpx quiet so the token can never reach the service logs.
logging.getLogger("httpx").setLevel(logging.WARNING)

WEDGE_LABELS = {
    "travellers-abroad": "Travellers abroad",
    "tour-operators": "Tour operators",
    "heritage-stories": "Heritage stories",
}


def alerts_enabled() -> bool:
    return bool(settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHAT_ID)


def format_signup(wedge: str, email: str, name: str | None, role: str | None,
                  note: str | None, wants_interview: bool, source: str | None) -> str:
    lines = [
        f"New signup: {WEDGE_LABELS.get(wedge, wedge)}",
        f"{name or '(no name)'} <{email}>",
    ]
    if role:
        lines.append(f"Role: {role}")
    if note:
        lines.append(f"Note: {note[:300]}")
    lines.append("Happy to do a call: YES, reply within the hour" if wants_interview else "Call: not offered (launch emails only)")
    if source:
        lines.append(f"Source: {source}")
    return "\n".join(lines)


def format_feedback(helpful: bool, comment: str | None, destination: str | None, name: str | None,
                    email: str | None, can_quote: bool, kind: str) -> str:
    lines = [f"New feedback: {'👍 useful' if helpful else '👎 not useful'}" + (f" ({destination})" if destination else "")]
    if comment:
        lines.append(f"\"{comment[:500]}\"")
    who = " ".join(x for x in [name or "", f"<{email}>" if email else ""] if x)
    if who:
        lines.append(f"From: {who}")
    lines.append("Can quote: yes" if can_quote else "Can quote: no")
    if kind != "itinerary":
        lines.append(f"Kind: {kind}")
    return "\n".join(lines)


async def send_signup_alert(client: httpx.AsyncClient, text: str) -> None:
    if not alerts_enabled():
        return
    try:
        # Plain text (no parse_mode), so visitor-typed text can't inject markup.
        res = await client.post(
            f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": settings.TELEGRAM_CHAT_ID, "text": text, "disable_web_page_preview": True},
            timeout=10.0,
        )
        if res.status_code != 200:
            logger.warning("Telegram alert failed with HTTP %s", res.status_code)
    except Exception as exc:  # never let an alert break a signup
        logger.warning("Telegram alert failed: %s", type(exc).__name__)
