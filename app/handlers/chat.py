import logging
import random
import time

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message, URLInputFile

from app import db
from app.companion_client import (
    build_chat_photo_prompt,
    detect_intent,
    generate_companion_reply,
    relationship_delta,
)
from app.config import settings
from app.image_client import generate_image
from app.keyboards import after_chat_photo_kb, chat_home_kb, roleplay_kb
from app.moderation import ModerationError, check_prompt

router = Router()
log = logging.getLogger(__name__)

ROLEPLAY_STARTERS = {
    "date": "Сцена: вы впервые встретились в маленьком кафе. Она уже ждёт у окна, улыбается и говорит: «Я думала, ты не решишься подойти». Ответь ей.",
    "walk": "Сцена: поздняя прогулка после дождя. Она идёт рядом слишком близко, иногда задевает твою руку и делает вид, что случайно. Что ты скажешь?",
    "home": "Сцена: вечер у неё дома. Фильм давно на паузе, свет приглушён, она смотрит прямо на тебя и спрашивает: «И что мы теперь будем делать?»",
    "surprise": "Сцена: ты сделал ей неожиданный сюрприз. Она открывает дверь, улыбается и говорит: «Ты правда решил меня удивить?» Что ты приготовил?",
    "tease": "Сцена: она прислала сообщение поздно вечером: «Я не могу уснуть. Развлечёшь меня?» Ответь ей так, чтобы она улыбнулась.",
}


def _has_unlimited(user: dict) -> bool:
    return bool(user.get("is_admin") or user.get("tier") == "premium")


async def _send_chat_photo(cb_or_msg, user: dict, char: dict, user_text: str = "") -> None:
    if not _has_unlimited(user):
        if user.get("credits", 0) <= 0:
            await cb_or_msg.answer("🚫 Лимит фото на сегодня исчерпан. Открой Pro/Premium в меню подписки.")
            return
        if not db.spend_credit(user["id"], "chat_photo"):
            await cb_or_msg.answer("🚫 Лимит фото на сегодня исчерпан.")
            return

    prompt = build_chat_photo_prompt(char, user_text)
    try:
        check_prompt(prompt)
    except ModerationError as e:
        await cb_or_msg.answer(e.reason)
        return

    gen = db.create_generation(user["id"], char["id"], "chat_photo", prompt)
    placeholder = await cb_or_msg.answer("Она набирает сообщение…\n\n«Я могу прислать тебе один момент. Только это будет между нами…»")

    try:
        image_url = await generate_image(prompt=prompt, seed=random.randint(1, 2_000_000_000))
        dest_path = f"u{user['id']}/c{char['id']}/chat_{int(time.time())}.jpg"
        try:
            stored_url = await db.upload_image_from_url(image_url, dest_path)
        except Exception as e:
            log.warning("Storage upload failed, using provider URL: %s", e)
            stored_url = image_url

        db.update_generation(gen["id"], status="done", image_url=stored_url)
        db.set_character_avatar(char["id"], stored_url)
        if not char.get("reference_url"):
            db.set_character_reference(char["id"], stored_url)

        try:
            await placeholder.delete()
        except Exception:
            pass

        await cb_or_msg.answer_photo(
            URLInputFile(stored_url),
            caption=f"💌 {char['name']} прислала момент только для тебя",
            reply_markup=after_chat_photo_kb(char["id"], gen["id"]),
        )
    except Exception as e:
        log.exception("Chat photo generation failed")
        db.update_generation(gen["id"], status="failed", error=str(e)[:500])
        if not _has_unlimited(user):
            db.grant_credits(user["id"], 1, "refund_failed_chat_photo", {"gen_id": gen["id"]})
        await placeholder.edit_text("😞 Фото не получилось. Кредит вернул, попробуй ещё раз.")


@router.callback_query(F.data.startswith("chat:start:"))
async def on_chat_start(cb: CallbackQuery):
    char_id = int(cb.data.split(":")[-1])
    user = db.get_or_create_user(cb.from_user.id, cb.from_user.username)
    char = db.get_character(char_id)
    if not char or char["user_id"] != user["id"]:
        await cb.answer("Персонаж не найден", show_alert=True)
        return

    db.set_active_character(user["id"], char_id, enabled=True)
    score = db.get_relationship(user["id"])
    text = (
        f"💬 *{char['name']} на связи*\n\n"
        f"Отношения: *{score}/100*\n\n"
        "Пиши ей обычным сообщением — как в чате. Она отвечает от своего характера и помнит последние реплики.\n\n"
        "Пиши естественно: «как ты?», «я бы хотел увидеть тебя», «давай встретимся», «что бы ты сделала, если бы я был рядом?»."
    )
    try:
        await cb.message.edit_text(text, reply_markup=chat_home_kb(char_id), parse_mode="Markdown")
    except Exception:
        await cb.message.answer(text, reply_markup=chat_home_kb(char_id), parse_mode="Markdown")
    await cb.answer()


@router.callback_query(F.data == "chat:stop")
async def on_chat_stop(cb: CallbackQuery):
    user = db.get_or_create_user(cb.from_user.id, cb.from_user.username)
    db.set_active_character(user["id"], None, enabled=False)
    await cb.message.answer("🚪 Диалог завершён. Когда захочешь — открой персонажа и нажми «💬 Общаться».")
    await cb.answer()


@router.callback_query(F.data.startswith("chat:photo:"))
async def on_chat_photo(cb: CallbackQuery):
    char_id = int(cb.data.split(":")[-1])
    user = db.get_or_create_user(cb.from_user.id, cb.from_user.username)
    user = db.refresh_daily_credits(user)
    char = db.get_character(char_id)
    if not char or char["user_id"] != user["id"]:
        await cb.answer("Персонаж не найден", show_alert=True)
        return
    await cb.answer("Она готовит момент…")
    await _send_chat_photo(cb.message, user, char, "хочу увидеть тебя сейчас")


@router.callback_query(F.data.startswith("chat:roleplay:"))
async def on_roleplay_home(cb: CallbackQuery):
    char_id = int(cb.data.split(":")[-1])
    await cb.message.answer(
        "🎭 Выбери настроение сцены. Дальше просто отвечай ей как в настоящем диалоге — без меню и команд.",
        reply_markup=roleplay_kb(char_id),
    )
    await cb.answer()


@router.callback_query(F.data.startswith("chat:rp:"))
async def on_roleplay_start(cb: CallbackQuery):
    _, _, char_id_str, key = cb.data.split(":")
    char_id = int(char_id_str)
    user = db.get_or_create_user(cb.from_user.id, cb.from_user.username)
    char = db.get_character(char_id)
    if not char or char["user_id"] != user["id"]:
        await cb.answer("Персонаж не найден", show_alert=True)
        return
    db.set_active_character(user["id"], char_id, enabled=True)
    starter = ROLEPLAY_STARTERS.get(key, ROLEPLAY_STARTERS["date"])
    db.add_chat_message(user["id"], char_id, "system", starter, event_type="roleplay_start")
    await cb.message.answer(
        f"🎭 *Сцена началась*\n\n{starter}\n\nПиши ей обычным сообщением — будто вы уже внутри этого момента.",
        reply_markup=chat_home_kb(char_id),
        parse_mode="Markdown",
    )
    await cb.answer()


@router.message(lambda m: bool(m.text) and not m.text.startswith("/"))
async def on_chat_message(message: Message):
    user = db.get_or_create_user(message.from_user.id, message.from_user.username)
    if not user.get("chat_enabled") or not user.get("active_character_id"):
        return

    char = db.get_character(user["active_character_id"])
    if not char or char["user_id"] != user["id"]:
        db.set_active_character(user["id"], None, enabled=False)
        await message.answer("Диалог сбросился: персонаж не найден. Открой персонажа заново.")
        return

    text = message.text.strip()
    try:
        check_prompt(text)
    except ModerationError as e:
        await message.answer(e.reason)
        return

    db.add_chat_message(user["id"], char["id"], "user", text)
    delta = relationship_delta(text)
    score = db.update_relationship(user["id"], delta) if delta else db.get_relationship(user["id"])
    history = db.get_chat_history(user["id"], char["id"], limit=12)
    reply = await generate_companion_reply(
        user=user,
        character=char,
        history=history,
        user_text=text,
        relationship_score=score,
    )
    db.add_chat_message(user["id"], char["id"], "assistant", reply)

    intent = detect_intent(text)
    suffix = f"\n\n💕 Отношения: {score}/100" if delta else ""
    await message.answer(reply + suffix, reply_markup=chat_home_kb(char["id"]))

    if intent == "photo":
        await _send_chat_photo(message, user, char, text)
    elif intent == "video":
        await message.answer("Она может отправить короткое видео из уже понравившегося момента. Открой кадр и нажми «🎥 Да, хочу видео».")
