from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message

from app import db
from app.keyboards import age_gate_kb, main_menu_kb

router = Router()


WELCOME = (
    "Привет 👋\n\n"
    "Это сервис, который создаёт фотографии твоего AI-персонажа в любых сценах.\n\n"
    "Создай свою героиню за минуту — выбери внешность, стиль, имя — "
    "и получай её фото в кафе, на прогулке, в путешествии.\n\n"
    "Перед началом подтверди, что тебе **18+**."
)


MENU_TEXT = (
    "Главное меню. Что делаем?\n\n"
    "✨ Создать персонажа — выбрать внешность и стиль\n"
    "📸 Мои персонажи — генерировать фото\n"
    "💎 Подписка — снять лимиты\n"
    "ℹ️ Баланс — сколько фото осталось"
)


@router.message(CommandStart())
async def on_start(message: Message):
    user = db.get_or_create_user(message.from_user.id, message.from_user.username)
    if not user["age_confirmed"]:
        await message.answer(WELCOME, reply_markup=age_gate_kb(), parse_mode="Markdown")
        return
    await message.answer(MENU_TEXT, reply_markup=main_menu_kb())


@router.callback_query(F.data == "age:yes")
async def on_age_yes(cb: CallbackQuery):
    user = db.get_or_create_user(cb.from_user.id, cb.from_user.username)
    db.confirm_age(user["id"])
    await cb.message.edit_text(
        "Отлично! Теперь давай создадим твоего первого персонажа.",
        reply_markup=main_menu_kb(),
    )
    await cb.answer()


@router.callback_query(F.data == "age:no")
async def on_age_no(cb: CallbackQuery):
    await cb.message.edit_text(
        "Извини, сервис только для 18+. Возвращайся, когда подрастёшь."
    )
    await cb.answer()


@router.callback_query(F.data == "menu")
async def on_menu(cb: CallbackQuery):
    await cb.message.edit_text(MENU_TEXT, reply_markup=main_menu_kb())
    await cb.answer()


@router.callback_query(F.data == "balance")
async def on_balance(cb: CallbackQuery):
    user = db.get_or_create_user(cb.from_user.id, cb.from_user.username)
    user = db.refresh_daily_credits(user)
    text = (
        f"Твой тариф: **{user['tier'].upper()}**\n"
        f"Осталось фото сегодня: **{user['credits']}**\n\n"
        "Лимит обновляется раз в сутки."
    )
    await cb.message.edit_text(text, reply_markup=main_menu_kb(), parse_mode="Markdown")
    await cb.answer()
