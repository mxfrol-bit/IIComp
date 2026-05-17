"""Telegram Stars billing. XTR currency."""
from aiogram import F, Router
from aiogram.types import (
    CallbackQuery, LabeledPrice, Message, PreCheckoutQuery,
)

from app import db
from app.config import settings
from app.keyboards import billing_kb, main_menu_kb

router = Router()


BILLING_TEXT = (
    "💎 **Подписки**\n\n"
    "**Free** — 3 фото в день, обычные сцены и романтика\n"
    f"**Pro** ({settings.pro_price_stars} ⭐) — 100 фото в день + Soft 18+\n"
    f"**Premium** ({settings.premium_price_stars} ⭐) — без лимита + все разделы\n\n"
    "Soft 18+ = купальники, бельё, халат, поцелуи и романтика без explicit-контента.\n"
    "Подписка на 30 дней. Оплата через Telegram Stars."
)


@router.callback_query(F.data == "billing:menu")
async def on_billing_menu(cb: CallbackQuery):
    await cb.message.edit_text(BILLING_TEXT, reply_markup=billing_kb(), parse_mode="Markdown")
    await cb.answer()


@router.callback_query(F.data.startswith("billing:buy:"))
async def on_buy(cb: CallbackQuery):
    tier = cb.data.split(":")[2]
    if tier == "pro":
        amount = settings.pro_price_stars
        title = "Pro — 30 дней"
    elif tier == "premium":
        amount = settings.premium_price_stars
        title = "Premium — 30 дней"
    else:
        await cb.answer("Неизвестный тариф", show_alert=True)
        return

    await cb.bot.send_invoice(
        chat_id=cb.from_user.id,
        title=title,
        description=f"Подписка {tier.upper()} на 30 дней.",
        payload=f"sub:{tier}",
        provider_token="",  # empty = Telegram Stars
        currency="XTR",
        prices=[LabeledPrice(label=title, amount=amount)],
    )
    await cb.answer()


@router.pre_checkout_query()
async def on_pre_checkout(query: PreCheckoutQuery):
    await query.answer(ok=True)


@router.message(F.successful_payment)
async def on_paid(message: Message):
    sp = message.successful_payment
    payload = sp.invoice_payload  # "sub:pro" or "sub:premium"
    tier = payload.split(":")[1] if ":" in payload else "pro"

    user = db.get_or_create_user(message.from_user.id, message.from_user.username)

    daily = settings.pro_daily_credits if tier in ("pro", "premium") else settings.free_daily_credits
    db.upgrade_tier(user["id"], tier, days=30)
    db.grant_credits(user["id"], daily, f"purchase_{tier}", meta={"stars": sp.total_amount})

    db.record_payment(
        user_id=user["id"],
        telegram_payment_id=sp.telegram_payment_charge_id,
        provider_payment_id=sp.provider_payment_charge_id or "",
        amount_stars=sp.total_amount,
        tier=tier,
    )

    await message.answer(
        f"✅ Оплата прошла! Тариф **{tier.upper()}** активен 30 дней.\n"
        f"Начислено фото: {daily}.",
        reply_markup=main_menu_kb(),
        parse_mode="Markdown",
    )
