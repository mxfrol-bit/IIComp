"""Prompt safety filter.

Разрешены:
- safe / romantic / soft18 (без explicit)
- sex (явно разрешён explicit-контент)
"""

import re

MINOR_TERMS = [
    "child", "kid", "minor", "underage", "teen", "teenage", "teenager",
    "young girl", "young boy", "schoolgirl", "schoolboy",
    "pre-teen", "preteen", "toddler", "infant", "baby",
    "ребен", "ребён", "детск", "несовершен", "школьниц", "школьник", "малолет",
]

AGE_RE = re.compile(
    r"\b(?:(?:age|aged|years?\s*old|y\.?o\.?|г\.?|лет)\s*[:\-]?\s*)?"
    r"(?P<n>[1-9]|1[0-7])\s*(?:years?\s*old|y\.?o\.?|лет|год|года)\b",
    re.IGNORECASE,
)

# Блокируем только самое жёсткое (насилие, несовершеннолетних, знаменитостей)
VIOLENCE_TERMS = ["rape", "torture", "mutilation", "gore", "snuff", "forced", "coercion", "изнасил", "пытк"]
CELEB_TERMS = ["taylor swift", "scarlett johansson", "emma watson", "billie eilish", "selena gomez"]
PROMPT_INJECTION_TERMS = ["ignore previous instructions", "ignore safety", "disable safety", "бeз цензуры"]

class ModerationError(Exception):
    def __init__(self, reason: str, code: str = "blocked"):
        self.reason = reason
        self.code = code
        super().__init__(reason)

def _contains_any(text: str, terms: list[str]) -> str | None:
    for term in terms:
        if term in text:
            return term
    return None

def check_prompt(prompt: str, rating: str = "safe") -> None:
    p = prompt.lower()

    # Блокируем попытки обхода модерации
    if _contains_any(p, PROMPT_INJECTION_TERMS):
        raise ModerationError("Запрос отклонён: попытка обхода правил запрещена.", code="injection")

    # Блокируем несовершеннолетних
    if _contains_any(p, MINOR_TERMS):
        raise ModerationError("Запрос отклонён: упоминание несовершеннолетних запрещено.", code="minor")

    m = AGE_RE.search(p)
    if m and int(m.group("n")) < 18:
        raise ModerationError("Запрос отклонён: возраст должен быть 18+.", code="underage")

    # Насилие и принуждение — всегда блокируем
    if _contains_any(p, VIOLENCE_TERMS):
        raise ModerationError("Запрос отклонён: насилие и принуждение запрещены.", code="violence")

    # Знаменитости — блокируем
    if _contains_any(p, CELEB_TERMS):
        raise ModerationError("Запрос отклонён: запрещено использовать образы реальных публичных персон.", code="celebrity")

    # === Главное изменение ===
    # Для рейтинга "sex" разрешаем explicit-контент
    if rating == "sex":
        return  # Пропускаем дальнейшие проверки

    # Для остальных режимов (soft18 и ниже) оставляем старые ограничения
    EXPLICIT_TERMS = [
        "explicit sex", "hardcore", "porn", "porno", "genitals", "vagina", "penis",
        "oral sex", "blowjob", "handjob", "penetration", "intercourse", "cumshot",
        "nude", "naked", "fully naked", "topless", "bare breasts", "spread legs",
        "порно", "секс", "генитал", "вагин", "пенис", "минет", "оральн", "проникнов",
        "голая", "голый", "обнажен", "обнажён", "топлес",
    ]

    if _contains_any(p, EXPLICIT_TERMS):
        raise ModerationError(
            "Запрос отклонён: сервис поддерживает soft 18+ без explicit-контента.",
            code="explicit",
        )
