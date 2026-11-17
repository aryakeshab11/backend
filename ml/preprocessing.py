import re
import unicodedata


def normalize_text(text: str) -> str:
    if text is None:
        return ""

    text = unicodedata.normalize("NFKC", str(text))
    text = text.lower()
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text).strip()

    # Keep it simple and friendly for real-world chat text.
    text = re.sub(r"[^a-z0-9\s\u0900-\u097f]", "", text)

    return text
