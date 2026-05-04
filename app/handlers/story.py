"""Story flow: home → seasons → episodes → beats."""
import logging
from datetime import datetime, timezone

from aiogram import F, Router
from aiogram.types import (
    CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, URLInputFile,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app import db, story
from app.config import settings

router = Router()
log = logging.getLogger(__name__)


# ---------- Keyboards ----------

def seasons_kb(seasons: list[dict]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for s in seasons:
        kb.button(text=f"📺 {s['title']}", callback_data=f"season:{s['id']}")
    kb.button(text="◀ Меню", callback_data="menu")
    kb.adjust(1)
    return kb.as_markup()


def episodes_kb(season_id: int, episodes: list[dict],
                user_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for ep in episodes:
        unlocked, unlock_at = story.is_episode_unlocked(user_id, ep)
        progress = story.get_progress(user_id, ep["id"])

        if not unlocked:
            label = f"🔒 Эп. {ep['number']}: {ep['title']}"
            kb.button(text=label, callback_data=f"ep:locked:{ep['id']}")
        elif progress and progress.get("completed_at"):
            label = f"✅ Эп. {ep['number']}: {ep['title']}"
            kb.button(text=label, callback_data=f"ep:replay:{ep['id']}")
        elif progress:
            label = f"▶ Эп. {ep['number']}: {ep['title']} (продолжить)"
            kb.button(text=label, callback_data=f"ep:start:{ep['id']}")
        else:
            label = f"▶ Эп. {ep['number']}: {ep['title']}"
            kb.button(text=label, callback_data=f"ep:start:{ep['id']}")
    kb.button(text="◀ Назад", callback_data="story:home")
    kb.adjust(1)
    return kb.as_markup()


def beat_kb(episode_id: int, beat: dict, current_key: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    # Linear pilot: just "next" button. Branching support is built-in via "choices".
    if "choices" in beat:
        for ch in beat["choices"]:
            label = ch["label"]
            if ch.get("premium"):
                label = f"💎 {label}"
            kb.button(
                text=label,
                callback_data=f"beat:{episode_id}:{ch['next']}:{ch.get('id','c')}",
            )
        kb.adjust(1)
    elif "next" in beat:
        kb.button(text="Дальше →", callback_data=f"beat:{episode_id}:{beat['next']}:next")
        kb.adjust(1)
    else:
        kb.button(text="Завершить эпизод", callback_data=f"ep:finish:{episode_id}")
        kb.adjust(1)
    return kb.as_markup()


def episode_completed_kb(season_id: int, next_ep: dict | None,
                         next_unlocked: bool, unlock_at) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    if next_ep:
        if next_unlocked:
            kb.button(text=f"▶ Смотреть эпизод {next_ep['number']}",
                      callback_data=f"ep:start:{next_ep['id']}")
        else:
            kb.button(text=f"💎 Открыть эпизод {next_ep['number']} сейчас (Stars)",
                      callback_data=f"ep:unlock:{next_ep['id']}")
            kb.button(text=f"⏰ Жду {unlock_at.strftime('%H:%M %d.%m')}",
                      callback_data="noop")
    kb.button(text="◀ К сезону", callback_data=f"season:{season_id}")
    kb.adjust(1)
    return kb.as_markup()


# ---------- Handlers ----------

@router.callback_query(F.data == "story:home")
async def on_story_home(cb: CallbackQuery):
    seasons = story.get_active_seasons()
    if not seasons:
        await cb.message.edit_text(
            "Сериалы скоро появятся 📺\nПока их нет — мы готовим первый сезон.",
        )
        await cb.answer()
        return
    text = "📺 **Доступные сериалы**\n\nВыбери, что смотреть:"
    await cb.message.edit_text(text, reply_markup=seasons_kb(seasons), parse_mode="Markdown")
    await cb.answer()


@router.callback_query(F.data.startswith("season:"))
async def on_season(cb: CallbackQuery):
    season_id = int(cb.data.split(":")[1])
    season = story.get_season(season_id)
    if not season:
        await cb.answer("Сезон не найден", show_alert=True)
        return

    user = db.get_or_create_user(cb.from_user.id, cb.from_user.username)
    episodes = story.get_episodes(season_id)

    text = (
        f"📺 **{season['title']}**\n\n"
        f"{season.get('description') or ''}\n\n"
        f"Эпизодов: {len(episodes)}"
    )
    await cb.message.edit_text(
        text,
        reply_markup=episodes_kb(season_id, episodes, user["id"]),
        parse_mode="Markdown",
    )
    await cb.answer()


@router.callback_query(F.data.startswith("ep:locked:"))
async def on_locked(cb: CallbackQuery):
    ep_id = int(cb.data.split(":")[2])
    ep = story.get_episode(ep_id)
    user = db.get_or_create_user(cb.from_user.id, cb.from_user.username)
    _, unlock_at = story.is_episode_unlocked(user["id"], ep)
    if unlock_at:
        await cb.answer(
            f"Эпизод откроется {unlock_at.strftime('%d.%m в %H:%M')}.\n"
            "Можно открыть сразу за Stars в меню эпизода.",
            show_alert=True,
        )
    else:
        await cb.answer("Сначала пройди предыдущий эпизод.", show_alert=True)


@router.callback_query(F.data.startswith("ep:start:") | F.data.startswith("ep:replay:"))
async def on_episode_start(cb: CallbackQuery):
    ep_id = int(cb.data.split(":")[2])
    ep = story.get_episode(ep_id)
    if not ep:
        await cb.answer("Эпизод не найден", show_alert=True)
        return

    user = db.get_or_create_user(cb.from_user.id, cb.from_user.username)
    unlocked, _ = story.is_episode_unlocked(user["id"], ep)
    if not unlocked:
        await cb.answer("Эпизод ещё не открыт.", show_alert=True)
        return

    progress = story.start_episode(user["id"], ep["season_id"], ep)
    await _show_beat(cb, ep, progress["current_beat"])


@router.callback_query(F.data.startswith("beat:"))
async def on_beat(cb: CallbackQuery):
    parts = cb.data.split(":")
    ep_id = int(parts[1])
    next_beat = parts[2]
    choice_id = parts[3] if len(parts) > 3 else "next"

    ep = story.get_episode(ep_id)
    if not ep:
        await cb.answer("Эпизод не найден", show_alert=True)
        return

    user = db.get_or_create_user(cb.from_user.id, cb.from_user.username)

    # Check if next beat is premium-gated
    target = story.get_beat(ep, next_beat)
    if target and target.get("is_premium") and user["tier"] == "free":
        await cb.answer(
            "Эта ветка только для Pro-подписчиков. Открой подписку в меню «💎».",
            show_alert=True,
        )
        return

    story.advance_beat(user["id"], ep_id, next_beat)
    story.log_event(user["id"], "beat_viewed", episode_id=ep_id,
                    beat_key=next_beat, meta={"choice": choice_id})

    if story.is_end_beat(ep, next_beat):
        # Show end beat THEN finish button
        await _show_beat(cb, ep, next_beat, force_end=True)
    else:
        await _show_beat(cb, ep, next_beat)


@router.callback_query(F.data.startswith("ep:finish:"))
async def on_episode_finish(cb: CallbackQuery):
    ep_id = int(cb.data.split(":")[2])
    ep = story.get_episode(ep_id)
    user = db.get_or_create_user(cb.from_user.id, cb.from_user.username)
    story.complete_episode(user["id"], ep_id)

    # Find next episode
    next_ep = story.get_episode_by_number(ep["season_id"], ep["number"] + 1)
    next_unlocked, unlock_at = (False, None)
    if next_ep:
        next_unlocked, unlock_at = story.is_episode_unlocked(user["id"], next_ep)

    if next_ep:
        if next_unlocked:
            text = (
                f"✨ Эпизод {ep['number']} завершён.\n\n"
                f"Следующий эпизод **{next_ep['title']}** уже открыт."
            )
        else:
            text = (
                f"✨ Эпизод {ep['number']} завершён.\n\n"
                f"Следующий эпизод **{next_ep['title']}** откроется "
                f"{unlock_at.strftime('%d.%m в %H:%M') if unlock_at else 'скоро'}.\n\n"
                "Хочешь увидеть прямо сейчас? Открой за Stars."
            )
    else:
        text = f"🏁 Сезон завершён. Спасибо, что был со мной до конца."

    await cb.message.edit_text(
        text,
        reply_markup=episode_completed_kb(ep["season_id"], next_ep, next_unlocked, unlock_at),
        parse_mode="Markdown",
    )
    await cb.answer()


@router.callback_query(F.data.startswith("ep:unlock:"))
async def on_unlock_paid(cb: CallbackQuery):
    """Stars-paid early unlock for next episode."""
    from aiogram.types import LabeledPrice
    ep_id = int(cb.data.split(":")[2])
    ep = story.get_episode(ep_id)
    if not ep:
        await cb.answer("Эпизод не найден", show_alert=True)
        return

    price = 50  # Stars per early unlock
    await cb.bot.send_invoice(
        chat_id=cb.from_user.id,
        title=f"Открыть «{ep['title']}» сейчас",
        description=f"Эпизод {ep['number']} становится доступен немедленно.",
        payload=f"unlock_ep:{ep_id}",
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(label=ep["title"], amount=price)],
    )
    await cb.answer()


@router.callback_query(F.data == "noop")
async def on_noop(cb: CallbackQuery):
    await cb.answer()


# ---------- Beat rendering ----------

async def _show_beat(cb: CallbackQuery, episode: dict, beat_key: str,
                     force_end: bool = False) -> None:
    beat = story.get_beat(episode, beat_key)
    if not beat:
        await cb.answer("Сцена не найдена", show_alert=True)
        return

    image_url = beat.get("image_url")
    text = beat.get("text", "")
    header = f"📺 *Эп. {episode['number']}: {episode['title']}*\n\n"
    full_text = header + text

    if force_end:
        # On end beats: show with "Finish episode" button
        kb_builder = InlineKeyboardBuilder()
        kb_builder.button(text="Завершить эпизод ✨",
                          callback_data=f"ep:finish:{episode['id']}")
        kb = kb_builder.as_markup()
    else:
        kb = beat_kb(episode["id"], beat, beat_key)

    try:
        if image_url:
            await cb.message.answer_photo(
                URLInputFile(image_url),
                caption=full_text,
                parse_mode="Markdown",
                reply_markup=kb,
            )
        else:
            await cb.message.answer(full_text, parse_mode="Markdown", reply_markup=kb)
        await cb.answer()
    except Exception as e:
        log.exception("Beat render failed: %s", e)
        await cb.message.answer(full_text, parse_mode="Markdown", reply_markup=kb)
        await cb.answer()
