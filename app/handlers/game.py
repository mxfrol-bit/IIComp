import logging
import random
import time

from aiogram import F, Router
from aiogram.types import CallbackQuery, URLInputFile

from app import db
from app.companion_client import generate_companion_reply
from app.game_flow import answer_text, build_first_meeting_prompt, first_companion_message, first_meeting_text
from app.image_client import generate_image
from app.keyboards import characters_kb, chat_home_kb, first_meeting_kb, main_menu_kb
from app.moderation import ModerationError, check_prompt

router = Router()
log = logging.getLogger(__name__)


async def _send_first_meeting_photo(cb: CallbackQuery, user: dict, char: dict) -> None:
    prompt = build_first_meeting_prompt(char)
    try:
        check_prompt(prompt)
    except ModerationError as e:
        await cb.message.answer(e.reason)
        return

    gen = db.create_generation(user["id"], char["id"], "first_meeting", prompt)
    placeholder = await cb.message.answer("☕ Она уже в кафе. Сейчас пришлёт момент встречи…")
    try:
        image_url = await generate_image(prompt=prompt, seed=random.randint(1, 2_000_000_000))
        dest_path = f"u{user['id']}/c{char['id']}/first_meeting_{int(time.time())}.jpg"
        try:
            stored_url = await db.upload_image_from_url(image_url, dest_path)
        except Exception as e:
            log.warning("First meeting upload failed, using provider URL: %s", e)
            stored_url = image_url

        db.update_generation(gen["id"], status="done", image_url=stored_url)
        db.set_character_avatar(char["id"], stored_url)
        if not char.get("reference_url"):
            db.set_character_reference(char["id"], stored_url)

        db.set_active_character(user["id"], char["id"], enabled=True)
        db.update_relationship(user["id"], 3)
        db.add_chat_message(user["id"], char["id"], "system", "Началась первая встреча в кафе.", event_type="first_meeting")
        db.add_chat_message(user["id"], char["id"], "assistant", first_meeting_text(char), event_type="first_meeting")

        try:
            await placeholder.delete()
        except Exception:
            pass

        await cb.message.answer_photo(
            URLInputFile(stored_url),
            caption=first_meeting_text(char),
            reply_markup=first_meeting_kb(char["id"]),
            parse_mode="Markdown",
        )
    except Exception as e:
        log.exception("First meeting generation failed")
        db.update_generation(gen["id"], status="failed", error=str(e)[:500])
        await placeholder.edit_text(
            first_meeting_text(char),
            reply_markup=first_meeting_kb(char["id"]),
            parse_mode="Markdown",
        )


@router.callback_query(F.data == "game:continue")
async def on_game_continue(cb: CallbackQuery):
    user = db.get_or_create_user(cb.from_user.id, cb.from_user.username)
    char = db.get_active_character_for_user(user["id"])
    if not char:
        chars = db.get_user_characters(user["id"])
        if not chars:
            await cb.message.answer(
                "Пока истории нет: сначала создай героиню. После создания она сама напишет первой и пришлёт первый момент.",
                reply_markup=main_menu_kb(),
            )
        else:
            await cb.message.answer("Выбери героиню, с которой продолжить историю:", reply_markup=characters_kb(chars))
        await cb.answer()
        return

    score = db.get_relationship(user["id"])
    text = (
        f"💕 *Продолжаем историю с {char['name']}*\n\n"
        f"Отношения: *{score}/100*\n\n"
        "Она уже в диалоге. Просто напиши ей обычным сообщением.\n"
        "Например: «как ты?», «давай встретимся», «я бы хотел увидеть тебя сейчас»."
    )
    await cb.message.answer(text, reply_markup=chat_home_kb(char["id"]), parse_mode="Markdown")
    await cb.answer()


@router.callback_query(F.data.startswith("game:intro_reply:"))
async def on_intro_reply(cb: CallbackQuery):
    char_id = int(cb.data.split(":")[-1])
    user = db.get_or_create_user(cb.from_user.id, cb.from_user.username)
    char = db.get_character(char_id)
    if not char or char["user_id"] != user["id"]:
        await cb.answer("Персонаж не найден", show_alert=True)
        return
    db.set_active_character(user["id"], char_id, enabled=True)
    msg = first_companion_message(char)
    await cb.message.answer(
        f"💬 *{char['name']} пишет первой:*\n\n{msg}\n\nОтветь ей обычным сообщением — дальше она будет вести диалог сама.",
        reply_markup=chat_home_kb(char_id),
        parse_mode="Markdown",
    )
    await cb.answer()


@router.callback_query(F.data.startswith("game:meet:"))
async def on_first_meeting(cb: CallbackQuery):
    char_id = int(cb.data.split(":")[-1])
    user = db.get_or_create_user(cb.from_user.id, cb.from_user.username)
    char = db.get_character(char_id)
    if not char or char["user_id"] != user["id"]:
        await cb.answer("Персонаж не найден", show_alert=True)
        return
    await cb.answer("Она уже ждёт тебя…")
    await _send_first_meeting_photo(cb, user, char)


@router.callback_query(F.data.startswith("game:answer:"))
async def on_first_meeting_answer(cb: CallbackQuery):
    _, _, char_id_str, choice = cb.data.split(":")
    char_id = int(char_id_str)
    user = db.get_or_create_user(cb.from_user.id, cb.from_user.username)
    char = db.get_character(char_id)
    if not char or char["user_id"] != user["id"]:
        await cb.answer("Персонаж не найден", show_alert=True)
        return

    user_text = answer_text(choice)
    db.set_active_character(user["id"], char_id, enabled=True)
    db.add_chat_message(user["id"], char_id, "user", user_text, event_type="first_meeting_choice")
    score = db.update_relationship(user["id"], 8 if choice in ("bold", "funny") else 5)
    history = db.get_chat_history(user["id"], char_id, limit=12)
    reply = await generate_companion_reply(
        user=user,
        character=char,
        history=history,
        user_text=user_text,
        relationship_score=score,
    )
    db.add_chat_message(user["id"], char_id, "assistant", reply, event_type="first_meeting_reply")
    await cb.message.answer(
        f"*Ты:* {user_text}\n\n*{char['name']}:* {reply}\n\n💕 Отношения: *{score}/100*",
        reply_markup=chat_home_kb(char_id),
        parse_mode="Markdown",
    )
    await cb.answer()
