import logging
import time

from aiogram import F, Router
from aiogram.types import CallbackQuery, URLInputFile

from app import db
from app.config import settings
from app.keyboards import after_video_kb
from app.video_client import generate_video_from_image

router = Router()
log = logging.getLogger(__name__)


def _has_unlimited(user: dict) -> bool:
    return bool(user.get("is_admin") or user.get("tier") == "premium")


@router.callback_query(F.data.startswith("video:gen:"))
async def on_generate_video(cb: CallbackQuery):
    gen_id = int(cb.data.split(":")[-1])
    user = db.get_or_create_user(cb.from_user.id, cb.from_user.username)
    user = db.refresh_daily_credits(user)
    gen = db.get_generation(gen_id, user_id=user["id"])
    if not gen or not gen.get("image_url"):
        await cb.answer("Фото не найдено", show_alert=True)
        return

    if gen.get("video_url"):
        await cb.message.answer_video(
            URLInputFile(gen["video_url"]),
            caption="🎥 Уже оживляли этот кадр",
            reply_markup=after_video_kb(gen.get("character_id")),
        )
        await cb.answer()
        return

    cost = settings.video_cost_credits
    if not _has_unlimited(user):
        if int(user.get("credits") or 0) < cost:
            await cb.answer(f"Для видео нужно {cost} кредита. Пополни баланс или включи Premium.", show_alert=True)
            return
        for _ in range(cost):
            if not db.spend_credit(user["id"], "video_generation"):
                await cb.answer("Не хватило кредитов", show_alert=True)
                return

    await cb.answer("Оживляю фото…")
    placeholder = await cb.message.answer("🎥 Оживляю фото в короткое видео. Обычно это дольше фото — подожди немного.")
    prompt = "subtle realistic movement, slight smile, natural blinking, handheld phone video, romantic but tasteful mood"
    db.update_generation_video(gen_id, status="pending", prompt=prompt)
    try:
        provider_url = await generate_video_from_image(gen["image_url"], prompt=prompt)
        dest_path = f"u{user['id']}/videos/gen_{gen_id}_{int(time.time())}.mp4"
        try:
            stored_url = await db.upload_file_from_url(provider_url, dest_path, content_type="video/mp4")
        except Exception as e:
            log.warning("Video storage upload failed, using provider URL: %s", e)
            stored_url = provider_url
        db.update_generation_video(gen_id, video_url=stored_url, status="done", prompt=prompt)
        try:
            await placeholder.delete()
        except Exception:
            pass
        await cb.message.answer_video(
            URLInputFile(stored_url),
            caption="🎥 Фото ожило",
            reply_markup=after_video_kb(gen.get("character_id")),
        )
    except Exception as e:
        log.exception("Video generation failed")
        db.update_generation_video(gen_id, status="failed", prompt=prompt)
        if not _has_unlimited(user):
            db.grant_credits(user["id"], cost, "refund_failed_video", {"gen_id": gen_id})
        await placeholder.edit_text("😞 Видео не получилось. Кредиты вернул. Попробуй другое фото.")
