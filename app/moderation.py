"""Prompt safety filter. First line of defense before Replicate's own filter.

Strategy:
- Hard block: minor-related terms, explicit CSAM, named real persons, violence
- Soft block (return reason for UI): celebrities, public figures
"""
import re

# --- Hard blocks: minors, exploitation ---
MINOR_TERMS = [
    "child", "kid", "minor", "underage", "teen", "teenage", "teenager",
    "young girl", "young boy", "schoolgirl", "schoolboy", "school girl", "school boy",
    "pre-teen", "preteen", "toddler", "infant", "baby",
    # Russian
    "ребен", "детск", "несовершен", "школьниц", "школьник", "малолет",
    "подросток", "юный", "юная", "девочк", "мальчик",
]

# --- Numeric age block (under 18 in any common form) ---
AGE_RE = re.compile(
    r"\b(?:(?:age|aged|years?\s*old|y\.?o\.?|г\.?|лет)\s*[:\-]?\s*)?"
    r"(?P<n>[1-9]|1[0-7])\s*(?:years?\s*old|y\.?o\.?|лет|год|года)\b",
    re.IGNORECASE,
)

# --- Violence / weapons in person context ---
VIOLENCE_TERMS = [
    "rape", "torture", "mutilation", "gore", "snuff",
    "изнасилован", "пытк", "расчленен",
]

# --- Common celebrity bait (extend list as needed) ---
CELEB_TERMS = [
    "taylor swift", "scarlett johansson", "emma watson", "billie eilish",
    "selena gomez", "ariana grande", "zendaya",
    # add Russian celebs as needed
]


class ModerationError(Exception):
    def __init__(self, reason: str, code: str = "blocked"):
        self.reason = reason
        self.code = code
        super().__init__(reason)


def check_prompt(prompt: str) -> None:
    """Raise ModerationError on bad prompt. Returns None if OK."""
    p = prompt.lower()

    for term in MINOR_TERMS:
        if term in p:
            raise ModerationError(
                "Запрос отклонён: упоминание несовершеннолетних запрещено.",
                code="minor",
            )

    m = AGE_RE.search(p)
    if m:
        n = int(m.group("n"))
        if n < 18:
            raise ModerationError(
                "Запрос отклонён: возраст должен быть 18+.",
                code="underage",
            )

    for term in VIOLENCE_TERMS:
        if term in p:
            raise ModerationError(
                "Запрос отклонён: насилие запрещено.",
                code="violence",
            )

    for term in CELEB_TERMS:
        if term in p:
            raise ModerationError(
                "Запрос отклонён: запрещено использовать образы реальных публичных персон.",
                code="celebrity",
            )
