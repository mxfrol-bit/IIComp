from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.factory_catalog import (
    AGE_RANGES, APPEARANCE_TYPES, HAIR_COLORS, HAIR_LENGTHS, MODEL_STYLES,
    NICHES, PHOTO_SCENARIOS, PRODUCT_CATEGORIES, VIDEO_DURATIONS,
    VIDEO_FORMATS, VIDEO_SCENARIOS,
)


def main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧬 Создать AI-модель", callback_data="fm:new")],
        [InlineKeyboardButton(text="👤 Мои модели", callback_data="fm:list"), InlineKeyboardButton(text="📦 Мои товары", callback_data="fp:list")],
        [InlineKeyboardButton(text="📸 Фото-контент", callback_data="fc:photo_home"), InlineKeyboardButton(text="🎥 Видео / Reels", callback_data="fc:video_home")],
        [InlineKeyboardButton(text="🧾 Контент-план", callback_data="fc:plan_home"), InlineKeyboardButton(text="💎 Тарифы", callback_data="billing:menu")],
        [InlineKeyboardButton(text="🔒 Private", callback_data="private:home"), InlineKeyboardButton(text="❓ Помощь", callback_data="help")],
    ])


def back_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀ В меню", callback_data="menu")]])


def billing_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐ Pro — больше генераций", callback_data="billing:buy:pro")],
        [InlineKeyboardButton(text="💎 Premium — безлимит + private", callback_data="billing:buy:premium")],
        [InlineKeyboardButton(text="◀ В меню", callback_data="menu")],
    ])


def grid_from_dict(data: dict, prefix: str, cols: int = 2) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for key, label in data.items():
        kb.button(text=str(label), callback_data=f"{prefix}:{key}")
    kb.adjust(cols)
    return kb.as_markup()


def model_age_kb():
    return grid_from_dict(AGE_RANGES, "fmage", 2)


def model_hair_color_kb():
    return grid_from_dict(HAIR_COLORS, "fmhair", 2)


def model_hair_length_kb():
    return grid_from_dict(HAIR_LENGTHS, "fmlen", 2)


def model_appearance_kb():
    return grid_from_dict(APPEARANCE_TYPES, "fmap", 1)


def model_style_kb():
    return grid_from_dict(MODEL_STYLES, "fmstyle", 2)


def model_niche_kb():
    return grid_from_dict(NICHES, "fmniche", 2)


def models_kb(models: list[dict]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for m in models:
        kb.button(text=f"👤 {m['name']}", callback_data=f"fm:open:{m['id']}")
    kb.button(text="➕ Создать AI-модель", callback_data="fm:new")
    kb.button(text="◀ В меню", callback_data="menu")
    kb.adjust(1)
    return kb.as_markup()


def model_card_kb(model_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📸 Instagram-съёмка", callback_data=f"fc:photo:{model_id}:0")],
        [InlineKeyboardButton(text="📢 Реклама с товаром", callback_data=f"fc:ad_products:{model_id}")],
        [InlineKeyboardButton(text="🎥 Видео / Reels", callback_data=f"fc:video_model:{model_id}")],
        [InlineKeyboardButton(text="🧬 Закрепить лицо", callback_data=f"fm:identity:{model_id}")],
        [InlineKeyboardButton(text="🧾 Контент-план", callback_data=f"fc:plan_model:{model_id}:0")],
        [InlineKeyboardButton(text="📦 Добавить товар", callback_data="fp:new")],
        [InlineKeyboardButton(text="🗑 Удалить модель", callback_data=f"fm:delq:{model_id}")],
        [InlineKeyboardButton(text="◀ Мои модели", callback_data="fm:list")],
    ])


def model_delete_kb(model_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да, удалить", callback_data=f"fm:del:{model_id}")],
        [InlineKeyboardButton(text="Отмена", callback_data=f"fm:open:{model_id}")],
    ])


def product_category_kb() -> InlineKeyboardMarkup:
    return grid_from_dict(PRODUCT_CATEGORIES, "fpcat", 1)


def product_upload_kb(has_photos: bool = False) -> InlineKeyboardMarkup:
    rows = []
    if has_photos:
        rows.append([InlineKeyboardButton(text="✅ Готово, сохранить товар", callback_data="fp:done")])
    rows.append([InlineKeyboardButton(text="◀ Отмена", callback_data="menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def products_kb(products: list[dict]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for p in products:
        kb.button(text=f"📦 {p['title']}", callback_data=f"fp:open:{p['id']}")
    kb.button(text="➕ Добавить товар", callback_data="fp:new")
    kb.button(text="◀ В меню", callback_data="menu")
    kb.adjust(1)
    return kb.as_markup()


def product_card_kb(product_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📸 Фото с моделью", callback_data=f"fp:pick_model_photo:{product_id}")],
        [InlineKeyboardButton(text="🎥 Видео с моделью", callback_data=f"fp:pick_model_video:{product_id}")],
        [InlineKeyboardButton(text="📢 Рекламная съёмка", callback_data=f"fp:pick_model_photo:{product_id}")],
        [InlineKeyboardButton(text="🧾 Идеи постов", callback_data=f"fp:pick_model_plan:{product_id}")],
        [InlineKeyboardButton(text="🗑 Удалить товар", callback_data=f"fp:delq:{product_id}")],
        [InlineKeyboardButton(text="◀ Мои товары", callback_data="fp:list")],
    ])


def pick_model_for_product_kb(models: list[dict], product_id: int, mode: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for m in models:
        cb = {
            "photo": f"fc:photo:{m['id']}:{product_id}",
            "video": f"fc:photo:{m['id']}:{product_id}",
            "plan": f"fc:plan_model:{m['id']}:{product_id}",
        }.get(mode, f"fc:photo:{m['id']}:{product_id}")
        kb.button(text=f"👤 {m['name']}", callback_data=cb)
    kb.button(text="➕ Создать AI-модель", callback_data="fm:new")
    kb.button(text="◀ Назад", callback_data=f"fp:open:{product_id}")
    kb.adjust(1)
    return kb.as_markup()


def photo_categories_kb(model_id: int, product_id: int = 0) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for cat_key, cat in PHOTO_SCENARIOS.items():
        kb.button(text=cat["title"], callback_data=f"fc:pcat:{model_id}:{product_id}:{cat_key}")
    kb.button(text="◀ К модели", callback_data=f"fm:open:{model_id}")
    kb.adjust(1)
    return kb.as_markup()


def photo_scenarios_kb(model_id: int, product_id: int, cat_key: str) -> InlineKeyboardMarkup:
    cat = PHOTO_SCENARIOS[cat_key]
    kb = InlineKeyboardBuilder()
    for key, (label, _, _) in cat["items"].items():
        kb.button(text=label, callback_data=f"fc:pgen:{model_id}:{product_id}:{key}")
    kb.button(text="◀ Категории", callback_data=f"fc:photo:{model_id}:{product_id}")
    kb.adjust(1)
    return kb.as_markup()


def after_photo_kb(model_id: int, product_id: int, scenario_key: str, gen_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Ещё вариант", callback_data=f"fc:pgen:{model_id}:{product_id}:{scenario_key}")],
        [InlineKeyboardButton(text="🎥 Сделать Reels/видео", callback_data=f"fv:cat:{gen_id}")],
        [InlineKeyboardButton(text="🧾 Идеи к этому товару", callback_data=f"fc:plan_model:{model_id}:{product_id}")],
        [InlineKeyboardButton(text="◀ К модели", callback_data=f"fm:open:{model_id}")],
    ])


def video_categories_kb(gen_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for cat_key, cat in VIDEO_SCENARIOS.items():
        kb.button(text=cat["title"], callback_data=f"fv:sc:{gen_id}:{cat_key}")
    kb.button(text="◀ В меню", callback_data="menu")
    kb.adjust(1)
    return kb.as_markup()


def video_scenarios_kb(gen_id: int, cat_key: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for key, (label, _) in VIDEO_SCENARIOS[cat_key]["items"].items():
        kb.button(text=label, callback_data=f"fv:fmt:{gen_id}:{key}")
    kb.button(text="◀ Категории", callback_data=f"fv:cat:{gen_id}")
    kb.adjust(1)
    return kb.as_markup()


def video_formats_kb(gen_id: int, scenario_key: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for key, (label, _) in VIDEO_FORMATS.items():
        kb.button(text=label, callback_data=f"fv:dur:{gen_id}:{scenario_key}:{key}")
    kb.adjust(1)
    return kb.as_markup()


def video_durations_kb(gen_id: int, scenario_key: str, fmt_key: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for dur_key, label in VIDEO_DURATIONS.items():
        kb.button(text=label, callback_data=f"fv:gen:{gen_id}:{scenario_key}:{fmt_key}:{dur_key}")
    kb.adjust(1)
    return kb.as_markup()
