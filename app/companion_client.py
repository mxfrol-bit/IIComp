"""Companion chat client.

Uses Anthropic Messages API when ANTHROPIC_API_KEY is provided.
If no key is configured, falls back to a lightweight scripted reply so the bot
keeps working during MVP tests.
"""
from __future__ import annotations

import logging
import random
from typing import Any

import httpx

from app.config import settings

log = logging.getLogger(__name__)

PHOTO_WORDS = (
    "фото", "селфи", "сфот", "покажи", "пришли", "скинь", "выглядишь",
    "photo", "selfie", "picture", "send pic", "show me",
)
VIDEO_WORDS = ("видео", "ролик", "оживи", "анимируй", "video", "animate")
ROMANTIC_WORDS = ("обними", "поцел", "скуч", "люб", "роман", "kiss", "hug", "miss")


def detect_intent(text: str) -> str:
    t = text.lower()
    if any(w in t for w in VIDEO_WORDS):
        return "video"
    if any(w in t for w in PHOTO_WORDS):
        return "photo"
    return "chat"


def relationship_delta(text: str) -> int:
    t = text.lower()
    if any(w in t for w in ROMANTIC_WORDS):
        return 2
    if any(w in t for w in ("спасибо", "класс", "краси", "мила", "нрав", "thank", "nice", "cute")):
        return 1
    if any(w in t for w in ("дура", "туп", "пошла", "hate", "stupid")):
        return -2
    return 0


def _persona_summary(character: dict) -> str:
    persona = character.get("persona") or {}
    parts = []
    for k, v in persona.items():
        parts.append(f"{k}: {v}")
    return "; ".join(parts) if parts else "персонаж без подробного описания"


def _fallback_reply(character: dict, user_text: str, score: int) -> str:
    name = character.get("name") or "она"
    intent = detect_intent(user_text)
    if intent == "photo":
        return random.choice([
            f"Хорошо… сделаю для тебя кадр. Только выбери настроение — уютно, романтично или смелее 😉",
            f"Могу прислать фото. Давай сделаем его живым, как будто это момент прямо сейчас.",
            f"Ладно, уговорил. Сейчас попробую поймать нужное настроение для фото.",
        ])
    if intent == "video":
        return "Видео лучше делать из уже готового фото. Выбери любимый кадр и нажми под ним «🎥 Оживить»."
    if score > 60:
        return random.choice([
            f"Мне нравится, как ты со мной разговариваешь. Продолжай… я начинаю привыкать к тебе.",
            f"Я улыбнулась, когда прочитала это. Расскажи, что ты хочешь сделать дальше?",
            f"С тобой становится спокойнее. Давай сыграем сцену: вечер, город, мы случайно остаёмся вдвоём…",
        ])
    return random.choice([
        f"Я слушаю. Расскажи подробнее — хочу понять, какой ты на самом деле.",
        f"Интересно. А если представить это как сцену — где мы сейчас находимся?",
        f"Давай сыграем. Ты задаёшь ситуацию, а я отвечаю как {name}.",
    ])


async def generate_companion_reply(
    *,
    user: dict,
    character: dict,
    history: list[dict[str, Any]],
    user_text: str,
    relationship_score: int,
) -> str:
    """Return a roleplay reply for the companion."""
    if not settings.anthropic_api_key:
        return _fallback_reply(character, user_text, relationship_score)

    name = character.get("name") or "Аня"
    system = (
        f"Ты — AI-компаньон по имени {name}. Это интерактивная романтическая игра для взрослых 18+. "
        "Твой стиль: живой, тёплый, немного игривый, но не пошлый. "
        "Ты можешь поддерживать романтику, флирт, свидания, ролевые сцены и просьбы о tasteful фото. "
        "Нельзя генерировать explicit sexual content, нельзя вовлекать несовершеннолетних, нельзя насилие, принуждение, публичных персон. "
        "Если пользователь просит фото — мягко согласись и предложи настроение; система отдельно сгенерирует фото. "
        "Если просит видео — объясни, что видео оживляется из готового фото. "
        f"Описание персонажа: {_persona_summary(character)}. "
        f"Текущая шкала отношений с пользователем: {relationship_score}/100. "
        "Отвечай по-русски, 1–3 коротких абзаца, без канцелярита."
    )

    messages: list[dict[str, str]] = []
    for m in history[-10:]:
        role = m.get("role")
        if role not in ("user", "assistant"):
            continue
        messages.append({"role": role, "content": m.get("content", "")[:1200]})
    messages.append({"role": "user", "content": user_text[:2000]})

    try:
        async with httpx.AsyncClient(timeout=45) as client:
            resp = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": settings.anthropic_api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": settings.anthropic_model,
                    "max_tokens": 450,
                    "temperature": 0.85,
                    "system": system,
                    "messages": messages,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            blocks = data.get("content") or []
            text = "".join(b.get("text", "") for b in blocks if b.get("type") == "text").strip()
            return text or _fallback_reply(character, user_text, relationship_score)
    except Exception as e:
        log.warning("Anthropic chat failed, using fallback: %s", e)
        return _fallback_reply(character, user_text, relationship_score)


def build_chat_photo_prompt(character: dict, user_text: str) -> str:
    """Build a tasteful selfie prompt from chat context."""
    from app.persona import build_base_prompt
    from app.presets import BASE_TRIGGERS, QUALITY_TAIL, ROMANTIC_TAIL, SOFT18_TAIL

    persona_base = build_base_prompt(character["persona"])
    text = user_text.lower()
    if any(w in text for w in ("роман", "поцел", "обними", "свидан", "вечер")):
        scene = "romantic candid selfie, warm evening light, gentle smile, tasteful non-explicit mood"
        tail = ROMANTIC_TAIL
    elif any(w in text for w in ("бель", "купаль", "халат", "плед", "кровать")):
        scene = "tasteful soft romantic mirror selfie, elegant home outfit, no nudity, non-explicit"
        tail = SOFT18_TAIL
    else:
        scene = "natural phone selfie sent during a chat, cozy background, soft smile, everyday candid moment"
        tail = QUALITY_TAIL
    return f"{BASE_TRIGGERS}, {persona_base}, {scene}, {tail}"
