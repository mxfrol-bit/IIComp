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
    "фото", "селфи", "сфот", "покажи", "пришли", "скинь", "выглядишь", "что пришлешь", "что пришлёшь", "как ты сейчас", "увидеть тебя",
    "photo", "selfie", "picture", "send pic", "show me",
)
VIDEO_WORDS = ("видео", "ролик", "оживи", "анимируй", "отправь видео", "короткое видео", "video", "animate")
ROMANTIC_WORDS = ("обними", "поцел", "скуч", "люб", "роман", "хочу тебя увидеть", "тянет", "не могу оторваться", "kiss", "hug", "miss")


SUGGESTION_TEXTS = {
    "ask_day": "Как прошёл твой день? Хочу знать о тебе чуть больше.",
    "meet": "Давай представим, что мы встретились сегодня вечером. Где бы ты хотела меня увидеть?",
    "flirt": "Ты опасно мило отвечаешь. Что бы ты сделала, если бы я сейчас был рядом?",
    "photo": "Хочу увидеть тебя сейчас. Покажешь мне один момент?",
    "closer": "Мне нравится, как между нами становится ближе. Продолжай, я слушаю.",
    "video": "Мне хочется увидеть этот момент живым. Пришлёшь короткое видео?",
}


def suggestion_to_user_text(key: str) -> str:
    return SUGGESTION_TEXTS.get(key, SUGGESTION_TEXTS["ask_day"])


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
            f"Могу прислать тебе один момент… только не смейся, я немного волнуюсь 😉",
            f"Хочешь увидеть, как я сейчас выгляжу? Тогда подожди пару секунд…",
            f"Ладно. Только это будет не просто фото, а настроение, которое я хочу тебе оставить.",
        ])
    if intent == "video":
        return "Могу отправить тебе короткое видео из одного момента. Выбери кадр, который тебе понравился, и я будто пришлю его живым."
    if score > 60:
        return random.choice([
            f"Мне нравится, как ты со мной разговариваешь. Продолжай… я начинаю привыкать к тебе.",
            f"Я улыбнулась, когда прочитала это. Расскажи, что ты хочешь сделать дальше?",
            f"С тобой становится спокойнее. Давай сыграем сцену: вечер, город, мы случайно остаёмся вдвоём…",
        ])
    return random.choice([
        f"Я читаю и улыбаюсь. Расскажи подробнее — мне правда интересно, какой ты, когда не стараешься казаться серьёзным.",
        f"Хм… звучит как начало сцены. Представь, что я сейчас напротив. Что бы ты сказал мне тише, чем обычно?",
        f"Давай без лишних правил. Просто пиши мне как есть — мне нравится ловить твои паузы и намёки.",
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
        "Пиши как девушка в личном чате: коротко, живо, с эмоцией, лёгким флиртом и ощущением диалога здесь-и-сейчас. "
        "Не отвечай как бот, помощник или сервис. Не используй технические слова вроде 'генерация', 'модель', 'кнопка', 'промпт'. "
        "Не утверждай, что ты реальный человек вне игры; просто держи иммерсивный стиль персонажа. "
        "Почти в каждом ответе должен быть мягкий флирт, личный крючок или вопрос, чтобы пользователю хотелось ответить. "
        "Ты можешь поддерживать романтику, свидания, напряжение между вами, tasteful фото/видео и ролевые сцены, но без explicit. "
        "Нельзя explicit sexual content, несовершеннолетние, насилие, принуждение, публичные персоны. "
        "Если пользователь просит увидеть тебя — отвечай естественно: 'могу прислать тебе один момент'; система отдельно отправит фото. "
        "Если просит видео — скажи: 'могу отправить короткое видео из этого момента'; система отдельно отправит видео. "
        f"Описание персонажа: {_persona_summary(character)}. "
        f"Текущая шкала отношений с пользователем: {relationship_score}/100. "
        "Отвечай по-русски, 1–3 коротких сообщения/абзаца. В конце часто задавай вопрос или делай флиртующий намёк."
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
        scene = "intimate romantic phone photo, warm evening light, direct eye contact, playful smile, tasteful non-explicit mood"
        tail = ROMANTIC_TAIL
    elif any(w in text for w in ("бель", "купаль", "халат", "плед", "кровать")):
        scene = "tasteful soft romantic mirror photo, elegant home outfit, covered body, non-explicit, playful private mood"
        tail = SOFT18_TAIL
    else:
        scene = "natural phone photo sent during a private chat, cozy background, direct eye contact, soft teasing smile, candid moment"
        tail = QUALITY_TAIL
    return f"{BASE_TRIGGERS}, {persona_base}, {scene}, {tail}"
