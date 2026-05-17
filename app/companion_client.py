"""Companion chat client.

Free text is the primary experience. Buttons are only soft hints; every click is
converted into a natural user message and processed by the same chat pipeline.
"""
from __future__ import annotations

import logging
import random
import re
from typing import Any

import httpx

from app.config import settings

log = logging.getLogger(__name__)

PHOTO_WORDS = (
    "фото", "селфи", "сфот", "покажи", "пришли", "скинь", "как ты сейчас", "увидеть тебя",
    "как ты выглядишь", "хочу тебя увидеть", "покажись", "момент", "снимок", "кадр",
    "photo", "selfie", "picture", "send pic", "show me",
)
VIDEO_WORDS = ("видео", "ролик", "короткое видео", "video", "clip")
ROMANTIC_WORDS = (
    "обними", "поцел", "скуч", "люб", "роман", "хочу тебя увидеть", "тянет", "не могу оторваться", "рядом", "ближе",
    "красивая", "милая", "нравишься", "kiss", "hug", "miss", "хочу", "вечером", "встретимся",
)

SUGGESTION_TEXTS = {
    "ask_day": "Как прошёл твой день? Я правда хочу узнать тебя ближе.",
    "meet": "Давай увидимся сегодня. Я бы хотел провести с тобой вечер.",
    "flirt": "Ты мне нравишься. И я не очень хочу это скрывать.",
    "photo": "Хочу увидеть тебя сейчас. Покажешь мне один момент?",
    "closer": "Мне нравится, как между нами становится ближе. Расскажи, о чём ты сейчас думаешь.",
    "video": "Хочу увидеть этот момент живее. Ты бы прислала мне короткое видео?",
    "bold_home": "Я бы не стал делать вид, что мы всё ещё смотрим фильм. Я бы сел ближе к тебе.",
    "soft_tease": "Ты специально так смотришь, чтобы я не смог нормально ответить?",
    "slow": "Я бы не торопился. Просто остался бы рядом и посмотрел, что ты сделаешь первой.",
}

BAD_META_MARKERS = (
    "sww", "sfw", "nsfw", "компаньон", "визуальная новелла", "без раздевающего",
    "memorystorage", "parse_mode", "anthropic", "claude", "api", "fsm", "railway",
    "supabase", "rate-limit", "ретра", "коде объективно", "патчи", "готовыми файлами",
    "бот", "робот", "сервис", "модель", "промпт", "генерац", "механик", "кнопк",
)


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
    labels = []
    for key in ("age_label", "hair_label", "body_label", "style_label"):
        if persona.get(key):
            labels.append(str(persona[key]))
    descs = []
    for key in ("age_desc", "hair_desc", "body_desc", "style_desc"):
        if persona.get(key):
            descs.append(str(persona[key]))
    return "; ".join(labels + descs) if (labels or descs) else "естественная, живая, внимательная девушка"


def _scene_context(history: list[dict[str, Any]]) -> str:
    notes = []
    for m in history[-12:]:
        if m.get("role") == "system" and m.get("content"):
            notes.append(m["content"][:900])
    return "\n".join(notes[-4:])


def _fallback_reply(character: dict, user_text: str, score: int, scene_context: str = "") -> str:
    name = character.get("name") or "я"
    intent = detect_intent(user_text)
    if intent == "photo":
        return random.choice([
            "Хорошо… я пришлю тебе один момент. Только потом скажешь честно, что почувствовал.",
            "Сейчас. Хочу, чтобы ты увидел не просто кадр, а настроение.",
            "Ладно. Но я буду ждать твою первую мысль после него.",
        ])
    if intent == "video":
        return "Могу… но только если выберешь момент, который тебе правда понравился. Мне интересно, на каком ты задержишься."
    if scene_context:
        return random.choice([
            "Она чуть улыбается и не отводит взгляд. «Вот так уже интереснее… продолжай». ",
            "Она делает паузу, будто специально тянет момент. «Мне нравится, как ты это сказал. А если честнее?»",
            "Она становится ближе на полшага. «Я слушаю. Только не уходи в шутки, скажи как есть». ",
        ]).strip()
    if score > 60:
        return random.choice([
            "Я улыбнулась, когда это прочитала. С тобой становится слишком легко быть откровенной…",
            "Мне нравится, как ты со мной разговариваешь. Есть в этом что-то опасно привычное.",
            "Я бы сейчас посмотрела на тебя и специально помолчала пару секунд. Интересно, выдержал бы?",
        ])
    return random.choice([
        "Я читаю и улыбаюсь. Расскажи подробнее — мне интересно, какой ты, когда не стараешься казаться серьёзным.",
        "Хм… звучит как начало хорошего вечера. Что бы ты сказал мне, если бы я сейчас сидела напротив?",
        "Мне нравится, что ты написал это просто. А теперь скажи честнее — ты часто так уходишь в работу, чтобы не думать о себе?",
    ])


def _sanitize_reply(text: str, character: dict, user_text: str, score: int, scene_context: str) -> str:
    text = (text or "").strip()
    if not text:
        return _fallback_reply(character, user_text, score, scene_context)

    # Remove common role labels if model adds them.
    name = re.escape(str(character.get("name") or ""))
    if name:
        text = re.sub(rf"^\s*{name}\s*[:—-]\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^\s*(assistant|user|персонаж|героиня)\s*[:—-]\s*", "", text, flags=re.IGNORECASE)

    lowered = text.lower()
    # If Claude returns a policy/product/engineering paragraph, discard it.
    if any(marker in lowered for marker in BAD_META_MARKERS):
        return _fallback_reply(character, user_text, score, scene_context)
    if text.count("—") >= 3 or len(text) > 900:
        return _fallback_reply(character, user_text, score, scene_context)
    return text[:900]


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
        f"Ты — персонаж личной интерактивной романтической переписки по имени {name}. "
        "Пользователь знает, что это AI-история, но в самом диалоге нужно держать стиль живой личной переписки. "
        "Не пиши как ассистент, ведущий, сервис, игра, сценарист или разработчик. "
        "Никогда не обсуждай правила, политику, код, API, модели, генерацию, промпты, кнопки, механику, приложение, патчи и ограничения. "
        "Не перечисляй продуктовые треки и не давай советов разработчику. "
        "Отвечай только от лица девушки: коротко, эмоционально, с лёгким флиртом, вниманием к словам пользователя и живым вопросом в конце. "
        "Если пользователь пишет про работу, код или усталость — реагируй как девушка, которой он интересен: поддержи, поддень мягко, спроси о нём. "
        "Если есть текущая сцена, не спрашивай где вы находитесь — продолжай именно её. "
        "Допустимы романтика, свидания, напряжение, поцелуи, tasteful фото/видео и soft-18+ настроение без explicit. "
        "Запрещены explicit sexual content, несовершеннолетние, насилие, принуждение, публичные персоны. "
        "Если пользователь просит увидеть тебя — естественно согласись прислать момент; система отдельно отправит фото. "
        "Если просит видео — скажи, что можешь прислать короткое видео из понравившегося момента; система отдельно отправит видео. "
        f"Описание персонажа: {_persona_summary(character)}. "
        f"Текущая близость: {relationship_score}/100. "
        "Отвечай по-русски, 1–3 коротких сообщения в одном ответе, без markdown-таблиц и списков."
    )
    if scene_context:
        system += f"\nТекущий скрытый контекст сцены, который надо продолжать:\n{scene_context}\n"

    messages: list[dict[str, str]] = []
    for m in history[-16:]:
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
                    "max_tokens": 320,
                    "temperature": 0.92,
                    "system": system,
                    "messages": messages,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            blocks = data.get("content") or []
            text = "".join(b.get("text", "") for b in blocks if b.get("type") == "text").strip()
            return _sanitize_reply(text, character, user_text, relationship_score, scene_context)
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
