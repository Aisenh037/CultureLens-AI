"""GeminiService on the google-genai SDK, tested offline.

The SDK's HTTP layer is replaced so we can assert on the exact request it
would send, which proves the Pydantic model converts into a valid Gemini
response schema (the old SDK could not do this, hence the hand-written dict).
"""
import json

import pytest
from google.genai import _api_client, types

from app.schemas.travel import CultureLensResponse
from app.services.gemini import GeminiService
from tests.factories import make_response


class Captured(Exception):
    pass


@pytest.fixture
def capture_request(monkeypatch):
    sent = {}

    async def fake_async_request(self, http_method, path, request_dict, http_options=None):
        sent.update(method=http_method, path=path, body=request_dict)
        raise Captured()

    monkeypatch.setattr(_api_client.BaseApiClient, "async_request", fake_async_request)
    return sent


async def test_structured_request_uses_pydantic_model_as_schema(capture_request):
    with pytest.raises(ValueError):
        await GeminiService().generate_structured_itinerary("plan Kyoto")

    gen_config = capture_request["body"]["generationConfig"]
    assert gen_config["responseMimeType"] == "application/json"
    schema = gen_config["responseSchema"]
    raw = json.dumps(schema)

    # Fully inlined: no $ref/$defs/allOf constructs for Gemini to choke on.
    assert not any(token in raw for token in ("$ref", "$defs", "allOf"))
    # Every top-level section of the response model is required.
    assert set(schema["required"]) == set(CultureLensResponse.model_fields)
    # Nested models are converted too, field by field.
    attraction = schema["properties"]["top_attractions"]["items"]
    assert set(attraction["required"]) == set(
        CultureLensResponse.model_fields["top_attractions"].annotation.__args__[0].model_fields
    )


async def test_chat_request_has_no_schema(capture_request):
    with pytest.raises(ValueError):
        await GeminiService().generate_chat_response("hello")
    assert "responseSchema" not in (capture_request["body"].get("generationConfig") or {})
    assert capture_request["path"].endswith(":generateContent")


def _sdk_response(text: str) -> types.GenerateContentResponse:
    return types.GenerateContentResponse(
        candidates=[types.Candidate(content=types.Content(role="model", parts=[types.Part(text=text)]))]
    )


async def test_structured_output_is_validated_from_text(monkeypatch):
    expected = make_response()

    async def fake_generate(**kwargs):
        return _sdk_response(expected.model_dump_json())

    service = GeminiService()
    monkeypatch.setattr(service.client.aio.models, "generate_content", fake_generate)
    result = await service.generate_structured_itinerary("plan Kyoto")
    assert isinstance(result, CultureLensResponse)
    assert result == expected


async def test_schema_mismatch_raises_clear_error(monkeypatch):
    async def fake_generate(**kwargs):
        return _sdk_response('{"summary": "missing everything else"}')

    service = GeminiService()
    monkeypatch.setattr(service.client.aio.models, "generate_content", fake_generate)
    with pytest.raises(ValueError, match="does not match the response schema"):
        await service.generate_structured_itinerary("plan Kyoto")


async def test_chat_returns_stripped_text(monkeypatch):
    async def fake_generate(**kwargs):
        return _sdk_response("  Konnichiwa!  \n")

    service = GeminiService()
    monkeypatch.setattr(service.client.aio.models, "generate_content", fake_generate)
    assert await service.generate_chat_response("hi") == "Konnichiwa!"


def test_client_is_reused_across_service_instances():
    assert GeminiService().client is GeminiService().client
