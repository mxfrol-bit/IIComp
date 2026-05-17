import logging

from aiogram import F, Router
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.types import (
    CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message, URLInputFile,
)

from app import db
from app.keyboards import age_gate_kb, back_to_menu_kb, content_home_kb, main_menu_kb

router = Router()
log = logging.getLogger(__name__)


WELCOME = (
    "Привет 👋\n\n"
    "Это сервис, который создаёт фотографии твоего AI-персонажа в любых сценах "
    "и развивает с тобой историю в формате интерактивного сериала.\n\n"
    "Перед началом подтверди, что тебе **18+**."
)

MENU_TEXT = (
    "🏠 *Главное меню*\n\n"
    "📺 Сериал — интерактивная история с героиней\n"
    "✨ Создать — сделай свою героиню\n"
    "📸 Мои персонажи — генерация фото в разных сценах\n"
    "❤️ Романтика — свидания, поцелуи, тёплые сцены\n"
    "🔞 Soft 18+ — купальники, бельё, халат, без explicit\n"
    "🎁 Что нового — последние твои фото\n"
    "🤝 Друзья — позови друзей и получи бонусные фото\n"
    "💎 Подписка — Pro / Premium тарифы\n"
    "ℹ️ Баланс — сколько фото осталось"
)

HELP_TEXT = (
    "❓ *Помощь*\n\n"
    "*Команды:*\n"
    "/start — главное меню\n"
    "/help — это сообщение\n"
    "/balance — мой баланс\n"
    "/menu — главное меню\n\n"
    "*Как пользоваться:*\n\n"
    "1️⃣ Создай персонажа в меню «✨ Создать»\n"
    "2️⃣ Открой её в «📸 Мои персонажи»\n"
    "3️⃣ Жми «📸 Сгенерировать фото» → выбери сцену\n"
    "4️⃣ Выбирай раздел: обычные сцены, романтика или soft 18+\n"
    "5️⃣ Жди ~15 секунд — фото придёт в чат\n"
    "6️⃣ Можешь нажать «🔄 Ещё фото в этой сцене» — другой ракурс\n\n"
    "*Сериал:* открой «📺 Сериал» в меню — там история с готовой героиней Анной, "
    "проходишь биты, делаешь выборы, открываешь следующие эпизоды.\n\n"
    "*Бонусы:* пригласи друга через «🤝 Друзья» — получите по 5 фото.\n\n"
    "Если что-то сломалось — напиши @ваш_саппорт."
)


# ---------- Commands ----------

@router.message(CommandStart(deep_link=True))
async def on_start_with_payload(message: Message, command: CommandObject):
    """Handles /start with referral payload like /start ref_123."""
    user = db.get_or_create_user(message.from_user.id, message.from_user.username)
    payload = command.args or ""

    if payload.startswith("ref_"):
        try:
            referrer_id = int(payload[4:])
            db.create_referral(referrer_id=referrer_id, referred_id=user["id"])
            log.info("Referral linked: referrer=%s referred=%s", referrer_id, user["id"])
        except (ValueError, Exception) as e:
            log.warning("Bad referral payload: %s — %s", payload, e)

    if not user["age_confirmed"]:
        await message.answer(WELCOME, reply_markup=age_gate_kb(), parse_mode="Markdown")
        return
    await message.answer(MENU_TEXT, reply_markup=main_menu_kb(), parse_mode="Markdown")


@router.message(CommandStart())
async def on_start(message: Message):
    user = db.get_or_create_user(message.from_user.id, message.from_user.username)
    if not user["age_confirmed"]:
        await message.answer(WELCOME, reply_markup=age_gate_kb(), parse_mode="Markdown")
        return
    await message.answer(MENU_TEXT, reply_markup=main_menu_kb(), parse_mode="Markdown")


@router.message(Command("menu"))
async def cmd_menu(message: Message):
    await message.answer(MENU_TEXT, reply_markup=main_menu_kb(), parse_mode="Markdown")


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(HELP_TEXT, reply_markup=back_to_menu_kb(), parse_mode="Markdown")


@router.message(Command("balance"))
async def cmd_balance(message: Message):
    user = db.get_or_create_user(message.from_user.id, message.from_user.username)
    user = db.refresh_daily_credits(user)
    text = (
        f"ℹ️ *Баланс*\n\n"
        f"Тариф: *{user['tier'].upper()}*\n"
        f"Фото осталось сегодня: *{user['credits']}*\n\n"
        f"Лимит обновляется раз в сутки."
    )
    await message.answer(text, reply_markup=back_to_menu_kb(), parse_mode="Markdown")


# ---------- Age gate ----------

@router.callback_query(F.data == "age:yes")
async def on_age_yes(cb: CallbackQuery):
    user = db.get_or_create_user(cb.from_user.id, cb.from_user.username)
    db.confirm_age(user["id"])
    await cb.message.edit_text(
        "Отлично! Теперь добро пожаловать в главное меню.\n\n" + MENU_TEXT,
        reply_markup=main_menu_kb(),
        parse_mode="Markdown",
    )
    await cb.answer()


@router.callback_query(F.data == "age:no")
async def on_age_no(cb: CallbackQuery):
    await cb.message.edit_text(
        "Извини, сервис только для 18+. Возвращайся, когда подрастёшь."
    )
    await cb.answer()


# ---------- Menu ----------

@router.callback_query(F.data == "menu")
async def on_menu(cb: CallbackQuery):
    try:
        await cb.message.edit_text(MENU_TEXT, reply_markup=main_menu_kb(), parse_mode="Markdown")
    except Exception:
        # If previous message was a photo, edit_text fails — send fresh
        await cb.message.answer(MENU_TEXT, reply_markup=main_menu_kb(), parse_mode="Markdown")
    await cb.answer()


@router.callback_query(F.data == "balance")
async def on_balance(cb: CallbackQuery):
    user = db.get_or_create_user(cb.from_user.id, cb.from_user.username)
    user = db.refresh_daily_credits(user)
    text = (
        f"ℹ️ *Баланс*\n\n"
        f"Тариф: *{user['tier'].upper()}*\n"
        f"Фото осталось сегодня: *{user['credits']}*\n\n"
        f"Лимит обновляется раз в сутки."
    )
    try:
        await cb.message.edit_text(text, reply_markup=back_to_menu_kb(), parse_mode="Markdown")
    except Exception:
        await cb.message.answer(text, reply_markup=back_to_menu_kb(), parse_mode="Markdown")
    await cb.answer()


@router.callback_query(F.data == "help")
async def on_help(cb: CallbackQuery):
    try:
        await cb.message.edit_text(HELP_TEXT, reply_markup=back_to_menu_kb(), parse_mode="Markdown")
    except Exception:
        await cb.message.answer(HELP_TEXT, reply_markup=back_to_menu_kb(), parse_mode="Markdown")
    await cb.answer()




@router.callback_query(F.data == "romance:home")
async def on_romance_home(cb: CallbackQuery):
    text = (
        "❤️ *Романтика*\n\n"
        "Свидания, поцелуи, объятия, утренние сообщения, вечерние сцены.\n\n"
        "Открой персонажа и выбери раздел «❤️ Романтика»."
    )
    try:
        await cb.message.edit_text(text, reply_markup=content_home_kb(), parse_mode="Markdown")
    except Exception:
        await cb.message.answer(text, reply_markup=content_home_kb(), parse_mode="Markdown")
    await cb.answer()


@router.callback_query(F.data == "soft18:home")
async def on_soft18_home(cb: CallbackQuery):
    text = (
        "🔞 *Soft 18+*\n\n"
        "Купальники, бельё, халат, утро под пледом, романтические сцены — "
        "без explicit-контента.\n\n"
        "Раздел доступен для 18+ пользователей на Pro/Premium."
    )
    try:
        await cb.message.edit_text(text, reply_markup=content_home_kb(), parse_mode="Markdown")
    except Exception:
        await cb.message.answer(text, reply_markup=content_home_kb(), parse_mode="Markdown")
    await cb.answer()


# ---------- Recent generations ----------

@router.callback_query(F.data == "recent")
async def on_recent(cb: CallbackQuery):
    user = db.get_or_create_user(cb.from_user.id, cb.from_user.username)
    gens = db.get_recent_generations(user["id"], limit=5)

    if not gens:
        try:
            await cb.message.edit_text(
                "🎁 *Что нового*\n\nУ тебя пока нет сгенерированных фото.\n"
                "Создай персонажа и сделай первое фото!",
                reply_markup=back_to_menu_kb(),
                parse_mode="Markdown",
            )
        except Exception:
            await cb.message.answer(
                "🎁 *Что нового*\n\nУ тебя пока нет сгенерированных фото.",
                reply_markup=back_to_menu_kb(),
                parse_mode="Markdown",
            )
        await cb.answer()
        return

    await cb.answer(f"Показываю последние {len(gens)} фото")
    for gen in gens:
        if gen.get("image_url"):
            try:
                await cb.message.answer_photo(
                    URLInputFile(gen["image_url"]),
                    caption=f"📸 {gen.get('preset_key', '')}",
                )
            except Exception as e:
                log.warning("Could not send recent photo %s: %s", gen["id"], e)

    await cb.message.answer("◀ В меню", reply_markup=back_to_menu_kb())


# ---------- Referrals ----------

@router.callback_query(F.data == "referral")
async def on_referral(cb: CallbackQuery):
    user = db.get_or_create_user(cb.from_user.id, cb.from_user.username)
    bot = await cb.bot.get_me()
    ref_link = f"https://t.me/{bot.username}?start=ref_{user['id']}"
    invited = db.count_referrals(user["id"])

    text = (
        "🤝 *Позови друзей*\n\n"
        f"Твоя реферальная ссылка:\n`{ref_link}`\n\n"
        "💚 За каждого друга, который перейдёт по ссылке и подтвердит 18+, "
        "ты получаешь *+5 бонусных фото* на баланс.\n\n"
        f"Уже пригласил: *{invited}* человек."
    )
    try:
        await cb.message.edit_text(text, reply_markup=back_to_menu_kb(), parse_mode="Markdown")
    except Exception:
        await cb.message.answer(text, reply_markup=back_to_menu_kb(), parse_mode="Markdown")
    await cb.answer()
