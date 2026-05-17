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
        [InlineKeyboardButton(text="📺 Сериал", callback_data="story:home")],
        [
            InlineKeyboardButton(text="✨ Создать", callback_data="char:new"),
            InlineKeyboardButton(text="📸 Мои персонажи", callback_data="char:list"),
        ],
        [
            InlineKeyboardButton(text="❤️ Романтика", callback_data="romance:home"),
            InlineKeyboardButton(text="🔞 Soft 18+", callback_data="soft18:home"),
        ],
        [
            InlineKeyboardButton(text="🎁 Что нового", callback_data="recent"),
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
    """Shown on character detail card."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📸 Обычные сцены", callback_data=f"char:scenes:{character_id}:safe")],
        [InlineKeyboardButton(text="❤️ Романтика", callback_data=f"char:scenes:{character_id}:romantic")],
        [InlineKeyboardButton(text="🔞 Soft 18+", callback_data=f"char:scenes:{character_id}:soft18")],
        [InlineKeyboardButton(text="🗑 Удалить", callback_data=f"char:delete_confirm:{character_id}")],
        [InlineKeyboardButton(text="◀ Назад", callback_data="char:list")],
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


def after_generation_kb(character_id: int, preset_key: str) -> InlineKeyboardMarkup:
    preset = PRESETS.get(preset_key, {})
    mode = preset.get("rating", "safe")
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Ещё фото в этой сцене", callback_data=f"gen:{character_id}:{preset_key}")],
        [InlineKeyboardButton(text="🎬 Другая сцена", callback_data=f"char:scenes:{character_id}:{mode}")],
        [InlineKeyboardButton(text="◀ В меню", callback_data="menu")],
    ])


def billing_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐ Pro — 100 фото/день + Soft 18+", callback_data="billing:buy:pro")],
        [InlineKeyboardButton(text="💎 Premium — без лимита", callback_data="billing:buy:premium")],
        [InlineKeyboardButton(text="◀ Меню", callback_data="menu")],
    ])
