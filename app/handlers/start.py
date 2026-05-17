from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import CallbackQuery, Message, URLInputFile

from app import db
from app.config import settings
from app.factory_keyboards import back_menu_kb, main_menu_kb

router = Router()
log = logging.getLogger(__name__)

WELCOME = (
    "🏭 AI Content Factory\n\n"
    "Создавай виртуальных AI-моделей, загружай товары и производи контент для Instagram, Reels, Stories и рекламы.\n\n"
    "Главный путь:\n"
    "1. 🧬 Создать AI-модель\n"
    "2. 📦 Загрузить товар\n"
    "3. 📸 Сделать рекламный кадр\n"
    "4. 🎥 Превратить кадр в Reels\n"
    "5. 🧾 Получить контент-план\n"
)

HELP = (
    "❓ Помощь\n\n"
    "🧬 AI-модель — виртуальный инфлюенсер с закреплённым hero face и identity pack.\n"
    "📦 Товар — фото/описание бутылки, шоколадки, платья, косметики, гаджета и т.д.\n"
    "📸 Фото-контент — Instagram, fashion, beauty, product placement, travel/hotel, UGC.\n"
    "🎥 Видео / Reels — делается из готового кадра: выбираешь движение, формат и длину.\n"
    "🧾 Контент-план — идеи постов, Reels, рекламных креативов и hooks.\n\n"
    "Важно: основной продукт — профессиональный контент-завод. Private-раздел спрятан отдельно и не участвует в основном флоу."
)


@router.message(CommandStart(deep_link=True))
async def start_deep(message: Message, command: CommandObject):
    user = db.get_or_create_user(message.from_user.id, message.from_user.username)
    payload = command.args or ""
    prefix = ""
    if payload.lower() == settings.promo_ref_code.lower():
        try:
            granted, credits = db.claim_promo_bonus(user["id"], settings.promo_ref_code, settings.promo_ref_bonus_credits)
            prefix = f"🎁 Бонус {'начислен' if granted else 'уже был активирован'}: баланс {credits} кредитов.\n\n"
        except Exception as e:
            log.warning("Promo claim failed: %s", e)
    elif payload.startswith("ref_"):
        try:
            db.create_referral(int(payload[4:]), user["id"])
            prefix = "🤝 Реферальная ссылка принята.\n\n"
        except Exception:
            pass
    await message.answer(prefix + WELCOME, reply_markup=main_menu_kb())


@router.message(CommandStart())
async def start(message: Message):
    db.get_or_create_user(message.from_user.id, message.from_user.username)
    await message.answer(WELCOME, reply_markup=main_menu_kb())


@router.message(Command("menu"))
async def menu_cmd(message: Message):
    await message.answer(WELCOME, reply_markup=main_menu_kb())


@router.message(Command("help"))
async def help_cmd(message: Message):
    await message.answer(HELP, reply_markup=back_menu_kb())


@router.message(Command("balance"))
async def balance_cmd(message: Message):
    user = db.get_or_create_user(message.from_user.id, message.from_user.username)
    user = db.refresh_daily_credits(user)
    credits = "∞" if user.get("is_admin") or user.get("tier") == "premium" else user.get("credits", 0)
    await message.answer(
        f"ℹ️ Баланс\n\nТариф: {str(user.get('tier', 'free')).upper()}\nКредиты: {credits}",
        reply_markup=back_menu_kb(),
    )


@router.callback_query(F.data == "menu")
async def menu_cb(cb: CallbackQuery):
    try:
        await cb.message.edit_text(WELCOME, reply_markup=main_menu_kb())
    except Exception:
        await cb.message.answer(WELCOME, reply_markup=main_menu_kb())
    await cb.answer()


@router.callback_query(F.data == "help")
async def help_cb(cb: CallbackQuery):
    try:
        await cb.message.edit_text(HELP, reply_markup=back_menu_kb())
    except Exception:
        await cb.message.answer(HELP, reply_markup=back_menu_kb())
    await cb.answer()


@router.callback_query(F.data == "balance")
async def balance_cb(cb: CallbackQuery):
    user = db.get_or_create_user(cb.from_user.id, cb.from_user.username)
    user = db.refresh_daily_credits(user)
    credits = "∞" if user.get("is_admin") or user.get("tier") == "premium" else user.get("credits", 0)
    await cb.message.answer(
        f"ℹ️ Баланс\n\nТариф: {str(user.get('tier', 'free')).upper()}\nКредиты: {credits}",
        reply_markup=back_menu_kb(),
    )
    await cb.answer()


@router.callback_query(F.data == "recent")
async def recent_cb(cb: CallbackQuery):
    user = db.get_or_create_user(cb.from_user.id, cb.from_user.username)
    gens = db.get_recent_content_generations(user["id"], limit=5)
    if not gens:
        await cb.message.answer("Пока нет готового контента.", reply_markup=main_menu_kb())
        await cb.answer()
        return
    for gen in gens:
        if gen.get("image_url"):
            await cb.message.answer_photo(URLInputFile(gen["image_url"]), caption=f"Кадр #{gen['id']} · {gen.get('scenario_key')}")
        if gen.get("video_url"):
            await cb.message.answer_video(URLInputFile(gen["video_url"]), caption=f"Видео #{gen['id']}")
    await cb.message.answer("Готово.", reply_markup=main_menu_kb())
    await cb.answer()
