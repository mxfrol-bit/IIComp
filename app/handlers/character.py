import random

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, URLInputFile

from app import db
from app.keyboards import (
    age_kb, body_kb, character_detail_kb, characters_kb, delete_confirm_kb,
    hair_kb, locked_soft18_kb, presets_kb, style_kb,
)
from app.persona import AGE_RANGES, BODY, HAIR, STYLE
from app.presets import MODE_TITLES
from app.states import CharacterCreation

router = Router()


@router.callback_query(F.data == "char:new")
async def on_new(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(CharacterCreation.waiting_name)
    await cb.message.answer(
        "✨ *Создание персонажа*\n\n"
        "Как зовут твою героиню? (1–20 символов)\n"
        "_Просто напиши имя в чат._",
        parse_mode="Markdown",
    )
    await cb.answer()


@router.message(CharacterCreation.waiting_name)
async def on_name(message: Message, state: FSMContext):
    name = (message.text or "").strip()
    if not (1 <= len(name) <= 20):
        await message.answer("Имя должно быть от 1 до 20 символов. Попробуй ещё раз.")
        return
    await state.update_data(name=name)
    await state.set_state(CharacterCreation.waiting_age)
    await message.answer(f"Отлично, *{name}*. Выбери возраст:", reply_markup=age_kb(),
                         parse_mode="Markdown")


@router.callback_query(CharacterCreation.waiting_age, F.data.startswith("persona_age:"))
async def on_age(cb: CallbackQuery, state: FSMContext):
    key = cb.data.split(":")[1]
    label, desc = AGE_RANGES[key]
    await state.update_data(age_key=key, age_label=label, age_desc=desc)
    await state.set_state(CharacterCreation.waiting_hair)
    await cb.message.edit_text("Волосы:", reply_markup=hair_kb())
    await cb.answer()


@router.callback_query(CharacterCreation.waiting_hair, F.data.startswith("persona_hair:"))
async def on_hair(cb: CallbackQuery, state: FSMContext):
    key = cb.data.split(":")[1]
    label, desc = HAIR[key]
    await state.update_data(hair_key=key, hair_label=label, hair_desc=desc)
    await state.set_state(CharacterCreation.waiting_body)
    await cb.message.edit_text("Телосложение:", reply_markup=body_kb())
    await cb.answer()


@router.callback_query(CharacterCreation.waiting_body, F.data.startswith("persona_body:"))
async def on_body(cb: CallbackQuery, state: FSMContext):
    key = cb.data.split(":")[1]
    label, desc = BODY[key]
    await state.update_data(body_key=key, body_label=label, body_desc=desc)
    await state.set_state(CharacterCreation.waiting_style)
    await cb.message.edit_text("Стиль:", reply_markup=style_kb())
    await cb.answer()


@router.callback_query(CharacterCreation.waiting_style, F.data.startswith("persona_style:"))
async def on_style(cb: CallbackQuery, state: FSMContext):
    key = cb.data.split(":")[1]
    label, desc = STYLE[key]
    data = await state.update_data(style_key=key, style_label=label, style_desc=desc)
    await state.clear()

    user = db.get_or_create_user(cb.from_user.id, cb.from_user.username)
    seed = random.randint(1, 2_000_000_000)

    persona = {
        "age_key": data["age_key"], "age_desc": data["age_desc"], "age_label": data["age_label"],
        "hair_key": data["hair_key"], "hair_desc": data["hair_desc"], "hair_label": data["hair_label"],
        "body_key": data["body_key"], "body_desc": data["body_desc"], "body_label": data["body_label"],
        "style_key": data["style_key"], "style_desc": data["style_desc"], "style_label": data["style_label"],
    }
    char = db.create_character(user["id"], data["name"], persona, seed)

    summary = (
        f"✨ *Готово!*\n\n"
        f"Героиня: *{char['name']}*\n\n"
        f"📅 Возраст: {data['age_label']}\n"
        f"💇 Волосы: {data['hair_label']}\n"
        f"👤 Телосложение: {data['body_label']}\n"
        f"👗 Стиль: {data['style_label']}\n\n"
        f"Жми «📸 Сгенерировать фото» — выберешь сцену."
    )
    await cb.message.edit_text(summary, reply_markup=character_detail_kb(char["id"]),
                               parse_mode="Markdown")
    await cb.answer()


@router.callback_query(F.data == "char:list")
async def on_list(cb: CallbackQuery):
    user = db.get_or_create_user(cb.from_user.id, cb.from_user.username)
    chars = db.get_user_characters(user["id"])
    if not chars:
        text = "📸 *Мои персонажи*\n\nУ тебя пока нет персонажей.\nСоздай первого!"
    else:
        text = f"📸 *Мои персонажи* ({len(chars)})\n\nВыбери, чтобы открыть карточку:"
    try:
        await cb.message.edit_text(text, reply_markup=characters_kb(chars), parse_mode="Markdown")
    except Exception:
        await cb.message.answer(text, reply_markup=characters_kb(chars), parse_mode="Markdown")
    await cb.answer()


@router.callback_query(F.data.startswith("char:open:"))
async def on_open(cb: CallbackQuery):
    char_id = int(cb.data.split(":")[2])
    char = db.get_character(char_id)
    if not char:
        await cb.answer("Персонаж не найден", show_alert=True)
        return

    user = db.get_or_create_user(cb.from_user.id, cb.from_user.username)
    if char["user_id"] != user["id"]:
        await cb.answer("Это не твой персонаж", show_alert=True)
        return

    persona = char["persona"]
    text = (
        f"💕 *{char['name']}*\n\n"
        f"📅 {persona['age_label']}\n"
        f"💇 {persona['hair_label']}\n"
        f"👤 {persona['body_label']}\n"
        f"👗 {persona['style_label']}"
    )

    avatar = char.get("avatar_url")
    try:
        if avatar:
            # Send as photo with caption
            await cb.message.answer_photo(
                URLInputFile(avatar),
                caption=text,
                reply_markup=character_detail_kb(char_id),
                parse_mode="Markdown",
            )
        else:
            await cb.message.edit_text(
                text + "\n\n_Сгенерируй первое фото — оно станет аватаркой._",
                reply_markup=character_detail_kb(char_id),
                parse_mode="Markdown",
            )
    except Exception:
        await cb.message.answer(
            text,
            reply_markup=character_detail_kb(char_id),
            parse_mode="Markdown",
        )
    await cb.answer()


@router.callback_query(F.data.startswith("char:scenes:"))
async def on_scenes(cb: CallbackQuery):
    parts = cb.data.split(":")
    char_id = int(parts[2])
    mode = parts[3] if len(parts) > 3 else "safe"

    char = db.get_character(char_id)
    if not char:
        await cb.answer("Персонаж не найден", show_alert=True)
        return

    user = db.get_or_create_user(cb.from_user.id, cb.from_user.username)
    if char["user_id"] != user["id"]:
        await cb.answer("Это не твой персонаж", show_alert=True)
        return

    if mode == "soft18" and user.get("tier") not in ("pro", "premium") and not user.get("is_admin"):
        text = (
            "🔞 *Soft 18+*\n\n"
            "Этот раздел: романтика, купальники, бельё, халат, поцелуи — "
            "без explicit-контента.\n\n"
            "Доступ открыт на тарифах *Pro* и *Premium*."
        )
        try:
            await cb.message.edit_text(text, reply_markup=locked_soft18_kb(), parse_mode="Markdown")
        except Exception:
            await cb.message.answer(text, reply_markup=locked_soft18_kb(), parse_mode="Markdown")
        await cb.answer("Раздел доступен на Pro / Premium", show_alert=True)
        return

    db.set_content_mode(user["id"], mode if mode in ("safe", "romantic", "soft18") else "safe")
    title = MODE_TITLES.get(mode, "🎬 Сцены")
    text = f"{title}\n\n*{char['name']}* — выбери сцену:"
    try:
        await cb.message.edit_text(text, reply_markup=presets_kb(char_id, mode), parse_mode="Markdown")
    except Exception:
        await cb.message.answer(text, reply_markup=presets_kb(char_id, mode), parse_mode="Markdown")
    await cb.answer()


@router.callback_query(F.data.startswith("char:delete_confirm:"))
async def on_delete_confirm(cb: CallbackQuery):
    char_id = int(cb.data.split(":")[2])
    char = db.get_character(char_id)
    if not char:
        await cb.answer("Персонаж не найден", show_alert=True)
        return
    text = (
        f"🗑 *Удалить {char['name']}?*\n\n"
        "Это действие необратимо — все сгенерированные фото пропадут."
    )
    try:
        await cb.message.edit_text(text, reply_markup=delete_confirm_kb(char_id), parse_mode="Markdown")
    except Exception:
        await cb.message.answer(text, reply_markup=delete_confirm_kb(char_id), parse_mode="Markdown")
    await cb.answer()


@router.callback_query(F.data.startswith("char:delete:"))
async def on_delete(cb: CallbackQuery):
    char_id = int(cb.data.split(":")[2])
    user = db.get_or_create_user(cb.from_user.id, cb.from_user.username)
    char = db.get_character(char_id)
    name = char["name"] if char else "персонаж"

    if db.delete_character(char_id, user["id"]):
        await cb.answer(f"Удалено: {name}", show_alert=False)
        # Reload characters list
        chars = db.get_user_characters(user["id"])
        if not chars:
            text = "📸 *Мои персонажи*\n\nУ тебя пока нет персонажей.\nСоздай первого!"
        else:
            text = f"📸 *Мои персонажи* ({len(chars)})"
        try:
            await cb.message.edit_text(text, reply_markup=characters_kb(chars), parse_mode="Markdown")
        except Exception:
            await cb.message.answer(text, reply_markup=characters_kb(chars), parse_mode="Markdown")
    else:
        await cb.answer("Не удалось удалить", show_alert=True)
