"""Shared pytest setup.

Settings are read at import time, so the environment must be prepared before
any `app.*` module is imported. This keeps the suite hermetic: it passes on a
clean CI runner with no real Gemini key and never talks to Gemini.
"""
import os

os.environ.setdefault("GEMINI_API_KEY", "test-key-not-real")
os.environ.setdefault("ALLOWED_ORIGINS", "http://localhost:5173")
# Rate limiting is exercised explicitly in its own test; keep it off elsewhere
# so repeated TestClient calls from 127.0.0.1 are not throttled.
os.environ.setdefault("RATE_LIMIT_ENABLED", "false")
