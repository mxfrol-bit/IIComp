from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.persona import AGE_RANGES, BODY, HAIR, STYLE
from app.presets import MODE_TITLES, PRESETS, get_presets_for_mode


def age_gate_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Мне 18+", callback_data="age:yes")],
        [InlineKeyboardButton(text="❌ Мне меньше 18", callback_data="age:no")],
    ])


def main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💕 Продолжить историю", callback_data="game:continue")],
        [
            InlineKeyboardButton(text="✨ Создать героиню", callback_data="char:new"),
            InlineKeyboardButton(text="👤 Моя героиня", callback_data="char:list"),
        ],
        [
            InlineKeyboardButton(text="🖼 Галерея", callback_data="recent"),
            InlineKeyboardButton(text="🤝 Друзья", callback_data="referral"),
        ],
        [
            InlineKeyboardButton(text="💎 Подписка", callback_data="billing:menu"),
            InlineKeyboardButton(text="ℹ️ Баланс", callback_data="balance"),
        ],
        [InlineKeyboardButton(text="❓ Помощь", callback_data="help")],
    ])


def back_to_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀ В меню", callback_data="menu")],
    ])


def content_home_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✨ Создать персонажа", callback_data="char:new")],
        [InlineKeyboardButton(text="📸 Мои персонажи", callback_data="char:list")],
        [InlineKeyboardButton(text="💎 Подписка", callback_data="billing:menu")],
        [InlineKeyboardButton(text="◀ В меню", callback_data="menu")],
    ])


def locked_soft18_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Открыть Pro / Premium", callback_data="billing:menu")],
        [InlineKeyboardButton(text="📸 Обычные сцены", callback_data="char:list")],
        [InlineKeyboardButton(text="◀ В меню", callback_data="menu")],
    ])


def _grid(items: dict, cb_prefix: str, cols: int = 2) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for key, (label, _) in items.items():
        kb.button(text=label, callback_data=f"{cb_prefix}:{key}")
    kb.adjust(cols)
    return kb.as_markup()


def age_kb() -> InlineKeyboardMarkup:
    return _grid(AGE_RANGES, "persona_age", cols=3)


def hair_kb() -> InlineKeyboardMarkup:
    return _grid(HAIR, "persona_hair", cols=2)


def body_kb() -> InlineKeyboardMarkup:
    return _grid(BODY, "persona_body", cols=2)


def style_kb() -> InlineKeyboardMarkup:
    return _grid(STYLE, "persona_style", cols=2)


def characters_kb(characters: list[dict]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for c in characters:
        kb.button(text=f"💕 {c['name']}", callback_data=f"char:open:{c['id']}")
    kb.button(text="➕ Новый", callback_data="char:new")
    kb.button(text="◀ Меню", callback_data="menu")
    kb.adjust(1)
    return kb.as_markup()


def character_detail_kb(character_id: int) -> InlineKeyboardMarkup:
    """Shown on character detail card: story-first navigation."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Написать ей", callback_data=f"chat:start:{character_id}")],
        [InlineKeyboardButton(text="☕ Первая встреча", callback_data=f"game:meet:{character_id}")],
        [InlineKeyboardButton(text="Хочу увидеть тебя", callback_data=f"chat:photo:{character_id}")],
        [InlineKeyboardButton(text="❤️ Романтика", callback_data=f"char:scenes:{character_id}:romantic")],
        [InlineKeyboardButton(text="🔥 Ближе", callback_data=f"char:scenes:{character_id}:soft18")],
        [InlineKeyboardButton(text="🗑 Удалить", callback_data=f"char:delete_confirm:{character_id}")],
        [InlineKeyboardButton(text="◀ Назад", callback_data="char:list")],
    ])


def intro_after_avatar_kb(character_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Ответить", callback_data=f"game:intro_reply:{character_id}")],
        [InlineKeyboardButton(text="☕ Первая встреча", callback_data=f"game:meet:{character_id}")],
        [InlineKeyboardButton(text="Хочу увидеть тебя", callback_data=f"chat:photo:{character_id}")],
    ])


def first_meeting_kb(character_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Сказать: «Привет. Я рад, что ты пришла»", callback_data=f"game:answer:{character_id}:calm")],
        [InlineKeyboardButton(text="Сказать: «Ты выглядишь опасно красиво»", callback_data=f"game:answer:{character_id}:bold")],
        [InlineKeyboardButton(text="Пошутить, чтобы она улыбнулась", callback_data=f"game:answer:{character_id}:funny")],
        [InlineKeyboardButton(text="Сказать, что хочешь её увидеть ближе", callback_data=f"game:answer:{character_id}:photo")],
    ])


def soft18_progress_locked_kb(character_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Написать ей", callback_data=f"chat:start:{character_id}")],
        [InlineKeyboardButton(text="❤️ Романтика", callback_data=f"char:scenes:{character_id}:romantic")],
        [InlineKeyboardButton(text="💎 Подписка", callback_data="billing:menu")],
    ])


def delete_confirm_kb(character_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Да, удалить", callback_data=f"char:delete:{character_id}")],
        [InlineKeyboardButton(text="◀ Отмена", callback_data=f"char:open:{character_id}")],
    ])


def presets_kb(character_id: int, mode: str = "safe") -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for key, preset in get_presets_for_mode(mode).items():
        label = preset["label"]
        if preset.get("rating") == "romantic" and not label.startswith("❤️"):
            label = f"❤️ {label}"
        kb.button(text=label, callback_data=f"gen:{character_id}:{key}")
    kb.button(text="📸 Обычные", callback_data=f"char:scenes:{character_id}:safe")
    kb.button(text="❤️ Романтика", callback_data=f"char:scenes:{character_id}:romantic")
    kb.button(text="🔞 Soft 18+", callback_data=f"char:scenes:{character_id}:soft18")
    kb.button(text="◀ К персонажу", callback_data=f"char:open:{character_id}")
    kb.adjust(2)
    return kb.as_markup()


def after_generation_kb(character_id: int, preset_key: str, gen_id: int | None = None) -> InlineKeyboardMarkup:
    preset = PRESETS.get(preset_key, {})
    mode = preset.get("rating", "safe")
    rows = [
        [InlineKeyboardButton(text="🔄 Ещё такой момент", callback_data=f"gen:{character_id}:{preset_key}")],
    ]
    if gen_id is not None:
        rows.append([InlineKeyboardButton(text="🎥 Да, хочу видео", callback_data=f"video:gen:{gen_id}")])
    rows.extend([
        [InlineKeyboardButton(text="💬 Общаться", callback_data=f"chat:start:{character_id}")],
        [InlineKeyboardButton(text="💕 Другой момент", callback_data=f"char:scenes:{character_id}:{mode}")],
        [InlineKeyboardButton(text="◀ В меню", callback_data="menu")],
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def billing_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐ Pro — 100 фото/день + Soft 18+", callback_data="billing:buy:pro")],
        [InlineKeyboardButton(text="💎 Premium — без лимита", callback_data="billing:buy:premium")],
        [InlineKeyboardButton(text="◀ Меню", callback_data="menu")],
    ])


def chat_home_kb(character_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Мне хочется увидеть тебя", callback_data=f"chat:photo:{character_id}")],
        [InlineKeyboardButton(text="💕 К её профилю", callback_data=f"char:open:{character_id}")],
    ])


def roleplay_kb(character_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="☕ Встреча в кафе", callback_data=f"chat:rp:{character_id}:date")],
        [InlineKeyboardButton(text="🌃 Прогулка ночью", callback_data=f"chat:rp:{character_id}:walk")],
        [InlineKeyboardButton(text="🛋 Вечер у неё", callback_data=f"chat:rp:{character_id}:home")],
        [InlineKeyboardButton(text="🎁 Сделать сюрприз", callback_data=f"chat:rp:{character_id}:surprise")],
        [InlineKeyboardButton(text="🔥 Позднее сообщение", callback_data=f"chat:rp:{character_id}:tease")],
        [InlineKeyboardButton(text="💬 Вернуться в чат", callback_data=f"chat:start:{character_id}")],
    ])


def after_chat_photo_kb(character_id: int, gen_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎥 Да, хочу видео", callback_data=f"video:gen:{gen_id}")],
        [InlineKeyboardButton(text="📩 Ещё один её момент", callback_data=f"chat:photo:{character_id}")],
        [InlineKeyboardButton(text="💬 Написать ей", callback_data=f"chat:start:{character_id}")],
        [InlineKeyboardButton(text="◀ В меню", callback_data="menu")],
    ])



SUGGESTION_LABELS = {
    "ask_day": "Как прошёл день?",
    "meet": "Позвать встретиться",
    "flirt": "Ответить смелее",
    "photo": "Хочу увидеть тебя",
    "closer": "Сказать теплее",
    "video": "Хочу короткое видео",
    "bold_home": "Сесть ближе",
    "soft_tease": "Поддразнить её",
    "slow": "Не торопиться",
}


def chat_suggestions_kb(character_id: int, score: int = 0) -> InlineKeyboardMarkup:
    """Tiny hint buttons under free-text replies.

    The chat must feel like a private dialogue. These are not menus; each button
    silently becomes a natural user message and the next bot message is only her reply.
    """
    if score < 8:
        keys = ["ask_day", "meet", "photo"]
    elif score < 25:
        keys = ["flirt", "photo", "closer"]
    else:
        keys = ["flirt", "photo", "video"]
    rows = []
    for key in keys:
        rows.append([InlineKeyboardButton(text=SUGGESTION_LABELS[key], callback_data=f"chat:suggest:{character_id}:{key}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def free_chat_hint_kb(character_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Как прошёл день?", callback_data=f"chat:suggest:{character_id}:ask_day")],
        [InlineKeyboardButton(text="Давай встретимся", callback_data=f"chat:suggest:{character_id}:meet")],
        [InlineKeyboardButton(text="Ты мне нравишься", callback_data=f"chat:suggest:{character_id}:flirt")],
    ])


def after_video_kb(character_id: int | None = None) -> InlineKeyboardMarkup:
    rows = []
    if character_id is not None:
        rows.append([InlineKeyboardButton(text="💬 Написать ей", callback_data=f"chat:start:{character_id}")])
    rows.append([InlineKeyboardButton(text="◀ В меню", callback_data="menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
