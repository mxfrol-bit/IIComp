import logging
import random
import time

from aiogram import F, Router
from aiogram.types import CallbackQuery, URLInputFile

from app import db
from app.image_client import generate_image
from app.keyboards import after_generation_kb, billing_kb, presets_kb
from app.moderation import ModerationError, check_prompt
from app.persona import build_base_prompt
from app.presets import PRESETS, build_prompt

router = Router()
log = logging.getLogger(__name__)


def _has_unlimited(user: dict) -> bool:
    return bool(user.get("is_admin") or user.get("tier") == "premium")


def _can_use_soft18(user: dict) -> bool:
    return bool(user.get("is_admin") or user.get("tier") in ("pro", "premium"))


@router.callback_query(F.data.startswith("gen:"))
async def on_generate(cb: CallbackQuery):
    parts = cb.data.split(":")
    if len(parts) != 3:
        await cb.answer("Bad callback", show_alert=True)
        return
    _, char_id_str, preset_key = parts
    char_id = int(char_id_str)

    user = db.get_or_create_user(cb.from_user.id, cb.from_user.username)
    user = db.refresh_daily_credits(user)

    char = db.get_character(char_id)
    if not char or char["user_id"] != user["id"]:
        await cb.answer("Персонаж не найден", show_alert=True)
        return

    if preset_key not in PRESETS:
        await cb.answer("Неизвестная сцена", show_alert=True)
        return

    preset = PRESETS[preset_key]
    rating = preset.get("rating", "safe")
    mode = rating if rating in ("safe", "romantic", "soft18") else "safe"

    if rating == "soft18" and not _can_use_soft18(user):
        await cb.message.answer(
            "🔞 Эта сцена доступна на тарифах *Pro* и *Premium*.\n"
            "Контент: soft 18+ без explicit.",
            reply_markup=billing_kb(),
            parse_mode="Markdown",
        )
        await cb.answer("Нужен Pro / Premium", show_alert=True)
        return

    if not _has_unlimited(user) and user["credits"] <= 0:
        await cb.answer(
            "🚫 Лимит на сегодня исчерпан.\nКупи Pro в меню «💎 Подписка».",
            show_alert=True,
        )
        return

    persona_base = build_base_prompt(char["persona"])
    seed = random.randint(1, 2_000_000_000)
    prompt = build_prompt(persona_base, preset_key)

    try:
        check_prompt(prompt)
    except ModerationError as e:
        await cb.answer(e.reason, show_alert=True)
        return

    credit_spent = False
    if not _has_unlimited(user):
        if not db.spend_credit(user["id"]):
            await cb.answer("Лимит исчерпан", show_alert=True)
            return
        credit_spent = True

    gen = db.create_generation(user["id"], char_id, preset_key, prompt)

    await cb.answer("Она готовит момент…")
    placeholder = await cb.message.answer(
        f"{char['name']} набирает…\n\n«Подожди, я хочу показать тебе кое-что.»"
    )

    try:
        image_url = await generate_image(prompt=prompt, seed=seed)

        dest_path = f"u{user['id']}/c{char_id}/{int(time.time())}.jpg"
        try:
            stored_url = await db.upload_image_from_url(image_url, dest_path)
        except Exception as e:
            log.warning("Storage upload failed, using provider URL: %s", e)
            stored_url = image_url

        db.update_generation(gen["id"], status="done", image_url=stored_url)
        db.set_character_avatar(char_id, stored_url)

        if not char.get("reference_url"):
            db.set_character_reference(char_id, stored_url)

        granted = db.grant_referral_bonus(user["id"], bonus_credits=5)
        if granted:
            log.info("Referral bonus granted to user %s", granted)

        fresh = db.get_or_create_user(cb.from_user.id, cb.from_user.username)
        remaining = "∞" if _has_unlimited(fresh) else str(fresh["credits"])

        try:
            await placeholder.delete()
        except Exception:
            pass

        await cb.message.answer_photo(
            URLInputFile(stored_url),
            caption=(
                f"💌 *{char['name']}* прислала момент: {preset['label']}\n"
                f"Осталось сегодня: *{remaining}*"
            ),
            parse_mode="Markdown",
            reply_markup=after_generation_kb(char_id, preset_key, gen["id"]),
        )

    except Exception as e:
        log.exception("Generation failed")
        db.update_generation(gen["id"], status="failed", error=str(e)[:500])
        if credit_spent:
            db.grant_credits(user["id"], 1, "refund_failed_generation", {"gen_id": gen["id"]})

        err_str = str(e).lower()
        if "safety" in err_str or "nsfw" in err_str or "filter" in err_str:
            msg = (
                "🚫 Сцена не прошла фильтр модерации.\n"
                "Кредит вернул. Попробуй другую сцену."
            )
        else:
            msg = (
                "😞 Не получилось сгенерировать.\n"
                "Кредит вернул, попробуй ещё раз или другую сцену."
            )
        try:
            await placeholder.edit_text(msg, reply_markup=presets_kb(char_id, mode))
        except Exception:
            await cb.message.answer(msg, reply_markup=presets_kb(char_id, mode))
