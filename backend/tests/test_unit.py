from app.utils.sanitization import sanitize_string
from app.prompts.travel_prompt import build_chat_prompt
from app.schemas.travel import ChatMessage

def test_sanitize_string():
    """Verify that the sanitization helper strips dangerous tokens and HTML tags."""
    dirty_html = "<script>alert('xss')</script>Explore Kyoto temples!"
    sanitized = sanitize_string(dirty_html)
    assert "script" not in sanitized
    assert "Explore Kyoto temples!" in sanitized

    dirty_markdown = "```json {key: value} ```"
    sanitized_md = sanitize_string(dirty_markdown)
    assert "```" not in sanitized_md

def test_build_chat_prompt_empty_context():
    """Verify that build_chat_prompt constructs a prompt even without travel context."""
    history = [ChatMessage(role="user", content="Hello!"), ChatMessage(role="assistant", content="Hi there!")]
    prompt = build_chat_prompt("Suggest things to do", history, None)
    assert "USER: Suggest things to do" in prompt
    assert "USER: Hello!" in prompt
    assert "ASSISTANT: Hi there!" in prompt
