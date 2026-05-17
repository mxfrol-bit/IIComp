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
    suggestion_to_user_text,
)
from app.config import settings
from app.image_client import generate_image
from app.keyboards import after_chat_photo_kb, chat_home_kb, chat_suggestions_kb, free_chat_hint_kb, roleplay_kb
from app.moderation import ModerationError, check_prompt

router = Router()
log = logging.getLogger(__name__)

ROLEPLAY_SCENES = {
    "date": {
        "context": "Вы впервые встретились в маленьком кафе у окна. За стеклом дождь. Она уже ждёт, слегка волнуется, но старается держаться уверенно.",
        "line": "Я уже думала, что ты не решишься подойти… но, кажется, мне нравится, что ты всё-таки здесь.",
    },
    "walk": {
        "context": "Поздняя прогулка после дождя. Ночной город, мокрый асфальт, тёплый свет витрин. Она идёт рядом слишком близко и иногда задевает твою руку.",
        "line": "Странно… мы вроде просто гуляем, а у меня ощущение, будто вечер уже стал слишком личным.",
    },
    "home": {
        "context": "Вечер у неё дома. Фильм давно стоит на паузе, свет приглушён. Она сидит рядом на диване и смотрит прямо на тебя.",
        "line": "Фильм уже полчаса на паузе… ты правда хочешь делать вид, что мы его смотрим?",
    },
    "surprise": {
        "context": "Ты приехал к ней с маленьким сюрпризом. Она открывает дверь, улыбается и пытается скрыть, что ей приятно.",
        "line": "Ты правда решил меня удивить? Теперь мне интересно, что ты задумал.",
    },
    "tease": {
        "context": "Поздний вечер. Она пишет первой, не может уснуть и явно хочет, чтобы разговор стал ближе.",
        "line": "Я не могу уснуть. И почему-то мне кажется, что ты можешь в этом помочь.",
    },
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
        f"💬 *{char['name']} онлайн*\n\n"
        f"Близость: *{score}/100*\n\n"
        "Она ждёт твоё сообщение. Просто напиши ей как в личном чате — коротко, честно, как хочешь.\n\n"
        "Подсказки ниже можно не нажимать, они просто помогают начать."
    )
    try:
        await cb.message.edit_text(text, reply_markup=free_chat_hint_kb(char_id), parse_mode="Markdown")
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
    scene = ROLEPLAY_SCENES.get(key, ROLEPLAY_SCENES["date"])
    context = scene["context"]
    line = scene["line"]
    db.add_chat_message(user["id"], char_id, "system", f"Текущая сцена: {context}", event_type="roleplay_start")
    db.add_chat_message(user["id"], char_id, "assistant", line, event_type="roleplay_start")
    await cb.message.answer(
        f"*{char['name']}:* {line}",
        reply_markup=chat_suggestions_kb(char_id, db.get_relationship(user["id"])),
        parse_mode="Markdown",
    )
    await cb.answer()



async def _process_free_chat(message: Message, user: dict, char: dict, text: str, *, from_suggestion: bool = False) -> None:
    try:
        check_prompt(text)
    except ModerationError as e:
        await message.answer(e.reason)
        return

    db.set_active_character(user["id"], char["id"], enabled=True)
    db.add_chat_message(user["id"], char["id"], "user", text, event_type="suggestion" if from_suggestion else "chat")

    delta = relationship_delta(text)
    # Any meaningful free-text interaction should slowly warm the relationship.
    if delta == 0 and len(text) >= 12:
        delta = 1
    score = db.update_relationship(user["id"], delta) if delta else db.get_relationship(user["id"])

    history = db.get_chat_history(user["id"], char["id"], limit=16)
    reply = await generate_companion_reply(
        user=user,
        character=char,
        history=history,
        user_text=text,
        relationship_score=score,
    )
    db.add_chat_message(user["id"], char["id"], "assistant", reply)

    intent = detect_intent(text)
    suffix = f"\n\n💕 Близость: {score}/100" if delta else ""
    await message.answer(reply + suffix, reply_markup=chat_suggestions_kb(char["id"], score))

    if intent == "photo":
        await _send_chat_photo(message, user, char, text)
    elif intent == "video":
        await message.answer("Она улыбается: «Я могу отправить короткое видео из того момента, который тебе понравился. Выбери кадр ниже — и я пришлю его живым».")


@router.callback_query(F.data.startswith("chat:suggest:"))
async def on_chat_suggestion(cb: CallbackQuery):
    _, _, char_id_str, key = cb.data.split(":")
    char_id = int(char_id_str)
    user = db.get_or_create_user(cb.from_user.id, cb.from_user.username)
    user = db.refresh_daily_credits(user)
    char = db.get_character(char_id)
    if not char or char["user_id"] != user["id"]:
        await cb.answer("Персонаж не найден", show_alert=True)
        return
    text = suggestion_to_user_text(key)
    await cb.answer("Она читает…")
    await _process_free_chat(cb.message, user, char, text, from_suggestion=True)


@router.message(lambda m: bool(m.text) and not m.text.startswith("/"))
async def on_chat_message(message: Message):
    user = db.get_or_create_user(message.from_user.id, message.from_user.username)
    if not user.get("chat_enabled") or not user.get("active_character_id"):
        return

    char = db.get_character(user["active_character_id"])
    if not char or char["user_id"] != user["id"]:
        db.set_active_character(user["id"], None, enabled=False)
        await message.answer("Диалог сбросился. Открой героиню заново — и она снова напишет тебе.")
        return

    text = message.text.strip()
    await _process_free_chat(message, user, char, text)
