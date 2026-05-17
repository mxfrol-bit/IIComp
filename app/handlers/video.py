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


def get_video_prompt(preset_key: str | None, gen: dict) -> str:
    """Возвращает подходящий промпт для видео в зависимости от сцены."""
    
    # Секс-сцены (самые пошлые)
    if preset_key and preset_key.startswith("sex_"):
        return (
            "explicit realistic sex motion, hard thrusting, body moving intensely, "
            "moaning facial expression, heavy breathing, sweaty skin, hair moving, "
            "detailed body movement, raw and vulgar sex animation, cinematic"
        )
    
    # Soft18 сцены
    if preset_key and preset_key.startswith("soft_"):
        return (
            "seductive erotic movement, slow sensual body motion, hand sliding over body, "
            "arching back, heavy breathing, aroused expression, subtle hip movement, "
            "teasing and dirty vibe, realistic phone video"
        )
    
    # Романтические сцены
    if preset_key and preset_key in ["taxi_after_date", "doorway_goodnight", "slow_dance_home"]:
        return (
            "romantic sensual movement, leaning closer, gentle touching, "
            "soft breathing, aroused expression, slow and intimate motion, "
            "cinematic romantic atmosphere"
        )
    
    # По умолчанию (обычные сцены)
    return (
        "subtle natural movement, slight head movement, natural blinking, "
        "gentle breathing, soft smile, realistic handheld phone video, "
        "calm and natural motion"
    )


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
            caption="🎥 Она уже присылала это видео",
            reply_markup=after_video_kb(gen.get("character_id")),
        )
        await cb.answer()
        return

    cost = settings.video_cost_credits
    if not _has_unlimited(user):
        if int(user.get("credits") or 0) < cost:
            await cb.answer(f"Для видео нужно {cost} кредитов.", show_alert=True)
            return
        for _ in range(cost):
            if not db.spend_credit(user["id"], "video_generation"):
                await cb.answer("Не хватило кредитов", show_alert=True)
                return

    await cb.answer("Генерирую видео…")
    placeholder = await cb.message.answer("🎥 Она записывает видео… Это может занять 30–60 секунд.")

    # === Главное изменение: динамический промпт ===
    preset_key = gen.get("preset_key")
    video_prompt = get_video_prompt(preset_key, gen)

    db.update_generation_video(gen_id, status="pending", prompt=video_prompt)

    try:
        provider_url = await generate_video_from_image(gen["image_url"], prompt=video_prompt)

        dest_path = f"u{user['id']}/videos/gen_{gen_id}_{int(time.time())}.mp4"
        try:
            stored_url = await db.upload_file_from_url(provider_url, dest_path, content_type="video/mp4")
        except Exception as e:
            log.warning("Video storage upload failed: %s", e)
            stored_url = provider_url

        db.update_generation_video(gen_id, video_url=stored_url, status="done", prompt=video_prompt)

        try:
            await placeholder.delete()
        except Exception:
            pass

        await cb.message.answer_video(
            URLInputFile(stored_url),
            caption="🎥 Она прислала тебе видео",
            reply_markup=after_video_kb(gen.get("character_id")),
        )

    except Exception as e:
        log.exception("Video generation failed")
        db.update_generation_video(gen_id, status="failed", prompt=video_prompt)
        if not _has_unlimited(user):
            db.grant_credits(user["id"], cost, "refund_failed_video", {"gen_id": gen_id})
        await placeholder.edit_text("😞 Не получилось сделать видео. Кредиты вернули.")
