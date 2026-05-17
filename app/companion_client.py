"""Legacy compatibility shim.
The active product is AI Content Factory, not companion chat.
"""
from __future__ import annotations


def detect_intent(text: str) -> str:
    return "chat"


def relationship_delta(text: str) -> int:
    return 0


def suggestion_to_user_text(key: str) -> str:
    return "Расскажи подробнее."


async def generate_companion_reply(*, user: dict, character: dict, history: list, user_text: str, relationship_score: int) -> str:
    return "Этот режим перенесён в отдельный private-модуль. Основной продукт — AI Content Factory."


def build_chat_photo_prompt(character: dict, user_text: str) -> str:
    return "professional brand-safe influencer photo"
