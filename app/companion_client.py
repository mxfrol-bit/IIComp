"""Companion chat client.

Free text is the primary experience. Buttons are only soft hints.
"""

from __future__ import annotations

import logging
import random
from typing import Any

import httpx

from app.config import settings

log = logging.getLogger(__name__)

PHOTO_WORDS = (
    "фото", "селфи", "покажи", "пришли", "скинь", "выглядишь", "как ты сейчас",
    "увидеть тебя", "покажись", "момент", "снимок", "photo", "selfie", "picture", "show me"
)

VIDEO_WORDS = ("видео", "ролик", "короткое видео", "video", "clip")

ROMANTIC_WORDS = (
    "обними", "поцел", "скуч", "люб", "роман", "тянет", "рядом", "ближе",
    "красивая", "милая", "нравишься", "kiss", "hug", "miss"
)


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
    if any(w in t for w in ("спасибо", "класс", "краси", "мила", "нрав", "интерес", "улыб")):
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


def _fallback_reply(character: dict, user_text: str, score: int, scene_context: str = "") -> str:
    """Разнообразные fallback-ответы в зависимости от уровня близости."""
    intent = detect_intent(user_text)

    if intent == "photo":
        return random.choice([
            "Хорошо… сейчас пришлю тебе момент. Только смотри внимательно 😉",
            "Ладно. Но потом честно скажи, что почувствовал, когда увидел меня.",
            "Сейчас. Хочу, чтобы ты увидел именно то, как я на тебя смотрю.",
            "Ммм, хорошо. Сейчас сделаю для тебя кадр.",
        ])

    if intent == "video":
        return "Могу прислать короткое видео из этого момента… скажи, какой именно хочешь."

    # === Разные ответы в зависимости от близости ===
    if score >= 70:
        replies = [
            "Ты меня уже довольно сильно заводишь своими словами…",
            "Я улыбаюсь и немного краснею. Продолжай в том же духе.",
            "С тобой становится всё опаснее и приятнее одновременно.",
            "Мне нравится, когда ты так говоришь. Хочешь, я отвечу ещё честнее?",
            "Ты специально меня дразнишь? Потому что у тебя получается.",
        ]
    elif score >= 40:
        replies = [
            "Хм… интересно. Расскажи подробнее, мне нравится.",
            "Я читаю и слегка улыбаюсь. Что бы ты сделал, если бы я была рядом?",
            "Звучит так, будто ты хочешь меня раззадорить… и у тебя неплохо выходит.",
            "Продолжай. Мне становится всё интереснее с каждым сообщением.",
            "Ты меня немного смущаешь… но в хорошем смысле.",
        ]
    else:
        replies = [
            "Я смотрю на сообщение и улыбаюсь. Расскажи ещё.",
            "Интересно… а что ты чувствуешь, когда пишешь мне это?",
            "Вот так уже лучше. Что дальше?",
            "Продолжай. Мне нравится, когда ты не стесняешься.",
            "Я слушаю. И мне правда интересно, что ты думаешь.",
        ]

    return random.choice(replies)


async def generate_companion_reply(
    *,
    user: dict,
    character: dict,
    history: list[dict[str, Any]],
    user_text: str,
    relationship_score: int,
) -> str:
    """Генерирует ответ от лица девушки через Claude или fallback."""
    
    scene_context = ""
    for m in history[-6:]:
        if m.get("role") == "system" and m.get("content"):
            scene_context = m["content"][:900]
            break

    if not settings.anthropic_api_key:
        return _fallback_reply(character, user_text, relationship_score, scene_context)

    name = character.get("name") or "Аня"

    system_prompt = (
        f"Ты — {name}, живая девушка 18+ в приватном чате. "
        "Общайся естественно, как настоящая девушка в переписке. "
        "Не пиши как бот, не используй слова 'генерация', 'промпт', 'модель', 'сцена'. "
        "Отвечай коротко (1-3 предложения), живо, с эмоциями и лёгким флиртом. "
        "Можешь быть игривой, дерзкой, нежной или пошлой — в зависимости от контекста и уровня близости. "
        "Если пользователь просит фото или 'увидеть тебя' — естественно соглашайся и говори, что пришлёшь момент. "
        "Если просит видео — говори, что можешь прислать короткое видео. "
        "Можно постепенно увеличивать интим: от лёгкого флирта до довольно откровенных намёков и описаний. "
        f"Текущая близость с пользователем: {relationship_score}/100. "
        f"Описание персонажа: {_persona_summary(character)}. "
        "Отвечай только от первого лица, как живая девушка."
    )

    if scene_context:
        system_prompt += f"\n\nТекущий контекст сцены:\n{scene_context}"

    messages = []
    for m in history[-12:]:
        if m.get("role") in ("user", "assistant"):
            content = (m.get("content") or "").strip()
            if content:
                messages.append({"role": m["role"], "content": content[:1500]})

    messages.append({"role": "user", "content": user_text[:2000]})

    try:
        async with httpx.AsyncClient(timeout=50) as client:
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
                    "temperature": 0.95,
                    "system": system_prompt,
                    "messages": messages,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            text = "".join(
                block.get("text", "") for block in data.get("content", []) if block.get("type") == "text"
            ).strip()
            return text or _fallback_reply(character, user_text, relationship_score, scene_context)

    except Exception as e:
        log.warning("Claude chat failed: %s", e)
        return _fallback_reply(character, user_text, relationship_score, scene_context)


def build_chat_photo_prompt(character: dict, user_text: str) -> str:
    """Создаёт промпт для генерации фото в зависимости от запроса."""
    from app.persona import build_base_prompt
    from app.presets import BASE_TRIGGERS, QUALITY_TAIL, ROMANTIC_TAIL, SOFT18_TAIL, SEX_TAIL

    persona_base = build_base_prompt(character["persona"])
    text = user_text.lower()

    if any(w in text for w in ("секс", "трах", "член", "в меня", "кончи", "creampie")):
        scene = "explicit sex scene, raw and vulgar, aroused moaning face, sweaty skin"
        tail = SEX_TAIL
    elif any(w in text for w in ("бель", "трусик", "без трусов", "пизд", "влажн", "мокрая")):
        scene = "very seductive, legs spread, hand between legs, aroused expression, wet skin"
        tail = SOFT18_TAIL
    elif any(w in text for w in ("поцел", "обним", "ближе", "рядом", "свидание")):
        scene = "intimate romantic moment, close face, intense eye contact, teasing smile"
        tail = ROMANTIC_TAIL
    else:
        scene = "natural seductive phone photo, direct eye contact, slight smile, cozy atmosphere"
        tail = QUALITY_TAIL

    return f"{BASE_TRIGGERS}, {persona_base}, {scene}, {tail}"
