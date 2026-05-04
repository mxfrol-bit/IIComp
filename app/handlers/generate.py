import logging
import time

from aiogram import F, Router
from aiogram.types import CallbackQuery, URLInputFile

from app import db
from app.keyboards import presets_kb
from app.moderation import ModerationError, check_prompt
from app.persona import build_base_prompt
from app.presets import PRESETS, build_prompt
from app.image_client import generate_image

router = Router()
log = logging.getLogger(__name__)


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

    if user["credits"] <= 0:
        await cb.answer(
            "Лимит на сегодня исчерпан. Купи Pro в меню «💎 Подписка».",
            show_alert=True,
        )
        return

    persona_base = build_base_prompt(char["persona"])
    prompt = build_prompt(persona_base, preset_key)

    try:
        check_prompt(prompt)
    except ModerationError as e:
        await cb.answer(e.reason, show_alert=True)
        return

    if not db.spend_credit(user["id"]):
        await cb.answer("Лимит исчерпан", show_alert=True)
        return

    gen = db.create_generation(user["id"], char_id, preset_key, prompt)

    await cb.answer("Генерирую…")
    placeholder = await cb.message.answer(
        f"🎨 Создаю фото «{PRESETS[preset_key]['label']}» — обычно 20–40 секунд…"
    )

    try:
        image_url = await generate_image(prompt=prompt, seed=char["seed"])

        # Upload to Supabase Storage for permanent URL
        dest_path = f"u{user['id']}/c{char_id}/{int(time.time())}.jpg"
        try:
            stored_url = await db.upload_image_from_url(image_url, dest_path)
        except Exception as e:
            log.warning("Storage upload failed, using Replicate URL: %s", e)
            stored_url = image_url

        db.update_generation(gen["id"], status="done", image_url=stored_url)

        # Save first generation as character reference (for future PuLID upgrade)
        if not char.get("reference_url"):
            db.set_character_reference(char_id, stored_url)

        await placeholder.delete()
        await cb.message.answer_photo(
            URLInputFile(image_url),
            caption=f"💕 {char['name']} — {PRESETS[preset_key]['label']}\nОсталось фото сегодня: {user['credits'] - 1}",
            reply_markup=presets_kb(char_id),
        )

    except Exception as e:
        log.exception("Generation failed")
        db.update_generation(gen["id"], status="failed", error=str(e)[:500])
        # Refund the credit
        db.grant_credits(user["id"], 1, "refund_failed_generation", {"gen_id": gen["id"]})
        await placeholder.edit_text(
            "😞 Не получилось сгенерировать. Кредит вернул, попробуй ещё раз или другую сцену."
        )
