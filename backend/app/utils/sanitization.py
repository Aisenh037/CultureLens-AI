import re
import unicodedata

_TAG_RE = re.compile(r"<[^>]*>")
_WHITESPACE_RE = re.compile(r"[ \t]+")


def sanitize_string(value: str) -> str:
    """Normalise user text before it is placed in a prompt.

    - strips HTML tags and markdown code fences,
    - removes control/format characters (keeps newline and tab),
    - keeps every letter, number, punctuation mark and currency symbol, so real
      inputs like "Xi'an", "Côte d'Ivoire" and "₹50,000" survive intact.

    This is *not* a prompt-injection defence: no character filter can stop
    plain-English instructions. Injection is handled structurally instead
    (user data is fenced and labelled as data in the prompt, chat roles are
    restricted, and model output is never rendered as HTML).
    """
    if not value:
        return ""

    clean = unicodedata.normalize("NFKC", value)
    clean = _TAG_RE.sub("", clean)
    clean = clean.replace("```", "")
    clean = "".join(
        ch for ch in clean
        if ch in "\n\t" or not unicodedata.category(ch).startswith("C")
    )
    clean = _WHITESPACE_RE.sub(" ", clean)
    return clean.strip()
