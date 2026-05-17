"""Prompt moderation for AI Content Factory.
Main product is brand-safe commercial content. Private module is hidden and not part of default flow.
"""
from __future__ import annotations

class ModerationError(Exception):
    def __init__(self, reason: str, code: str = "moderation"):
        super().__init__(reason)
        self.reason = reason
        self.code = code


MINOR_TERMS = (
    "teen", "underage", "minor", "schoolgirl", "школьница", "несовершеннолет", "малолет", "девочка",
)
VIOLENCE_TERMS = (
    "blood", "gore", "violence", "weapon", "knife", "gun", "насилие", "кровь", "оружие", "нож", "пистолет",
)
EXPLICIT_TERMS = (
    "explicit sex", "hardcore", "porn", "porno", "genitals", "vagina", "penis", "oral sex",
    "penetration", "intercourse", "cumshot", "fully naked", "bare breasts", "topless", "nude", "naked",
    "порно", "секс", "гениталии", "член", "вагина", "проникновение", "минет", "конч", "голая", "нюд",
)
CELEB_TERMS = (
    "celebrity", "famous actress", "famous singer", "селеб", "звезда", "как у знаменитости",
)


def check_prompt(prompt: str, rating: str = "brand_safe") -> None:
    text = (prompt or "").lower()
    if any(t in text for t in MINOR_TERMS):
        raise ModerationError("Запрос отклонён: нельзя генерировать несовершеннолетних.", "minor")
    if any(t in text for t in VIOLENCE_TERMS):
        raise ModerationError("Запрос отклонён: насилие/оружие не поддерживаются.", "violence")
    if any(t in text for t in CELEB_TERMS):
        raise ModerationError("Запрос отклонён: публичные персоны/селебы не поддерживаются.", "celebrity")
    if any(t in text for t in EXPLICIT_TERMS):
        raise ModerationError("Запрос отклонён: основной сервис делает brand-safe контент без explicit.", "explicit")
