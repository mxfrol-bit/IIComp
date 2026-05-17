"""Companion chat client.

Free text is the primary experience. Buttons are only soft hints; every click is
converted into a natural user message and processed by the same chat pipeline.
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
    "как ты выглядишь", "хочу тебя увидеть", "покажись", "момент", "снимок", "кадр",
    "photo", "selfie", "picture", "send pic", "show me",
)
VIDEO_WORDS = ("видео", "ролик", "короткое видео", "video", "clip")
ROMANTIC_WORDS = (
    "обними", "поцел", "скуч", "люб", "роман", "хочу тебя увидеть", "тянет", "не могу оторваться", "рядом", "ближе",
    "красивая", "милая", "нравишься", "kiss", "hug", "miss",
)

SUGGESTION_TEXTS = {
    "ask_day": "Как прошёл твой день? Мне правда интересно, что у тебя было сегодня.",
    "meet": "Давай представим, что мы встретились сегодня вечером. Где бы ты хотела меня увидеть?",
    "flirt": "Ты слишком мило отвечаешь. Что бы ты сделала, если бы я сейчас оказался рядом?",
    "photo": "Мне хочется увидеть тебя сейчас. Покажешь мне один момент?",
    "closer": "Мне нравится, как между нами становится ближе. Не останавливайся.",
    "video": "Мне хочется увидеть этот момент чуть живее. Ты бы прислала мне короткое видео?",
    "bold_home": "Я бы не стал делать вид, что мы всё ещё смотрим фильм. Я бы сел ближе к тебе.",
    "soft_tease": "Ты специально так смотришь, чтобы я не смог нормально ответить?",
    "slow": "Я бы не торопился. Просто остался бы рядом и посмотрел, что ты сделаешь первой.",
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
    if any(w in t for w in ("спасибо", "класс", "краси", "мила", "нрав", "интерес", "улыб", "thank", "nice", "cute")):
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


def _scene_context(history: list[dict[str, Any]]) -> str:
    """Pull recent system scene notes into the model prompt.

    Earlier builds stored scene starts as role='system' but then filtered them
    out before calling Claude. This made the character forget the scene and ask
    dumb questions like 'where are we?'.
    """
    notes = []
    for m in history[-8:]:
        if m.get("role") == "system" and m.get("content"):
            notes.append(m["content"][:900])
    return "\n".join(notes[-3:])


def _fallback_reply(character: dict, user_text: str, score: int, scene_context: str = "") -> str:
    intent = detect_intent(user_text)
    if intent == "photo":
        return random.choice([
            "Хорошо… я пришлю тебе один момент. Только не смотри на него слишком спокойно 😉",
            "Сейчас. Хочу, чтобы ты увидел именно настроение, а не просто картинку.",
            "Ладно. Но потом скажешь честно, что почувствовал, когда увидел меня.",
        ])
    if intent == "video":
        return "Могу прислать короткое видео из этого момента… но выбери кадр, который тебе правда зацепил."
    if scene_context:
        return random.choice([
            "Она чуть улыбается и не отводит взгляд. «Вот так уже интереснее… продолжай». ",
            "Она делает паузу, будто специально тянет момент. «Мне нравится, как ты это сказал. А если честнее?»",
            "Она становится ближе на полшага. «Я слушаю. Только не уходи в шутки, скажи как есть». ",
        ]).strip()
    if score > 60:
        return random.choice([
            "Мне нравится, как ты со мной разговариваешь. Есть в этом что-то опасно привычное…",
            "Я улыбнулась, когда прочитала это. И теперь хочу понять, что ты скажешь дальше.",
            "С тобой становится спокойнее. Но не слишком расслабляйся — мне нравится, когда между нами есть искра.",
        ])
    return random.choice([
        "Я читаю и улыбаюсь. Расскажи подробнее — мне интересно, какой ты, когда не стараешься казаться серьёзным.",
        "Хм… звучит как начало хорошего вечера. Что бы ты сказал мне, если бы я сейчас сидела напротив?",
        "Давай без лишних правил. Просто пиши мне как есть — мне нравится ловить твои паузы и намёки.",
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
    scene_context = _scene_context(history)
    if not settings.anthropic_api_key:
        return _fallback_reply(character, user_text, relationship_score, scene_context)

    name = character.get("name") or "Аня"
    system = (
        f"Ты — AI-персонаж по имени {name} в интерактивной романтической истории 18+. "
        "Пользователь знает, что это AI-история, но внутри чата нужно держать иммерсивный стиль личной переписки. "
        "Не пиши как бот, сервис, помощник, игра, ведущий или сценарист. Не используй слова: генерация, модель, промпт, кнопка, сценарий, механика. "
        "Не объясняй правила. Просто отвечай как героиня в личном чате. "
        "Ответы должны быть короткими, живыми, с мягким флиртом, паузами, реакцией на пользователя и вопросом/крючком в конце. "
        "Если есть текущая сцена, не спрашивай где вы находитесь — продолжай именно эту сцену. "
        "Допустимы романтика, свидания, напряжение, поцелуи, tasteful фото/видео и soft-18+ настроение без explicit. "
        "Запрещены explicit sexual content, несовершеннолетние, насилие, принуждение, публичные персоны. "
        "Если пользователь просит увидеть тебя — естественно согласись прислать момент; система отдельно отправит фото. "
        "Если просит видео — скажи, что можешь прислать короткое видео из понравившегося момента; система отдельно отправит видео. "
        f"Описание персонажа: {_persona_summary(character)}. "
        f"Текущая близость: {relationship_score}/100. "
    )
    if scene_context:
        system += f"\nТекущий контекст сцены, который надо продолжать:\n{scene_context}\n"
    system += "Отвечай по-русски, 1–3 коротких абзаца."

    messages: list[dict[str, str]] = []
    for m in history[-14:]:
        role = m.get("role")
        if role not in ("user", "assistant"):
            continue
        content = (m.get("content") or "").strip()
        if not content:
            continue
        messages.append({"role": role, "content": content[:1200]})
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
                    "max_tokens": 420,
                    "temperature": 0.9,
                    "system": system,
                    "messages": messages,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            blocks = data.get("content") or []
            text = "".join(b.get("text", "") for b in blocks if b.get("type") == "text").strip()
            return text or _fallback_reply(character, user_text, relationship_score, scene_context)
    except Exception as e:
        log.warning("Anthropic chat failed, using fallback: %s", e)
        return _fallback_reply(character, user_text, relationship_score, scene_context)


def build_chat_photo_prompt(character: dict, user_text: str) -> str:
    """Build a tasteful photo prompt from chat context."""
    from app.persona import build_base_prompt
    from app.presets import BASE_TRIGGERS, QUALITY_TAIL, ROMANTIC_TAIL, SOFT18_TAIL

    persona_base = build_base_prompt(character["persona"])
    text = user_text.lower()
    if any(w in text for w in ("поцел", "обними", "свидан", "вечер", "рядом", "ближе")):
        scene = "intimate romantic phone photo, warm evening light, direct eye contact, playful smile, tasteful non-explicit mood"
        tail = ROMANTIC_TAIL
    elif any(w in text for w in ("бель", "купаль", "халат", "плед", "кровать", "дом", "вечер у нее", "вечер у неё")):
        scene = "tasteful soft romantic private photo, elegant home outfit, covered body, non-explicit, playful private mood"
        tail = SOFT18_TAIL
    else:
        scene = "natural phone photo sent during a private chat, cozy background, direct eye contact, soft teasing smile, candid moment"
        tail = QUALITY_TAIL
    return f"{BASE_TRIGGERS}, {persona_base}, {scene}, {tail}"
