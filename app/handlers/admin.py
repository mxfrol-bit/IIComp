"""Admin commands. Only users with users.is_admin=true can run these.

Available:
  /admin grant <username> <credits>     — give credits
  /admin tier <username> <free|pro|premium>   — set tier (30 days for paid)
  /admin stats                            — quick numbers
  /admin makeadmin <username>             — promote user to admin (use carefully)
"""
import logging

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from app import db
from app.config import settings
from app.db import supabase

router = Router()
log = logging.getLogger(__name__)


HELP = (
    "🛠 *Admin*\n\n"
    "`/admin grant <username> <credits>` — выдать N кредитов\n"
    "`/admin tier <username> <free|pro|premium>` — сменить тариф на 30 дней\n"
    "`/admin stats` — общая статистика\n"
    "`/admin makeadmin <username>` — назначить админа\n"
    "`/admin web` — ссылка на web admin панель\n"
)


@router.message(Command("admin"))
async def cmd_admin(message: Message, command: CommandObject):
    user = db.get_or_create_user(message.from_user.id, message.from_user.username)
    if not db.is_admin(user["id"]):
        # silent fail: don't leak admin existence
        return

    args = (command.args or "").strip().split()
    if not args:
        await message.answer(HELP, parse_mode="Markdown")
        return

    sub = args[0].lower()

    if sub == "stats":
        await _stats(message)
        return

    if sub == "web":
        if not settings.web_public_url:
            await message.answer("WEB_PUBLIC_URL не задан в Railway. Добавь публичный URL Railway сервиса.")
            return
        if not settings.admin_web_token:
            await message.answer("ADMIN_WEB_TOKEN не задан в Railway. Добавь секретный токен для админки.")
            return
        base = settings.web_public_url.rstrip("/")
        url = base + "/admin?token=" + settings.admin_web_token
        mini = base + "/mini"
        studio = base + "/studio"
        pitch = base + "/pitch"
        await message.answer(
            "🛠 Web admin:\n" + url +
            "\n\n🏭 Studio Web App:\n" + studio +
            "\n\n📲 Mini App:\n" + mini +
            "\n\n📊 Investor Pitch:\n" + pitch
        )
        return

    if sub == "grant" and len(args) == 3:
        username, amount_str = args[1], args[2]
        try:
            amount = int(amount_str)
        except ValueError:
            await message.answer("⚠️ credits должно быть числом")
            return
        target = db.find_user_by_username(username)
        if not target:
            await message.answer(f"⚠️ Юзер @{username.lstrip('@')} не найден")
            return
        db.grant_credits(target["id"], amount, "admin_grant",
                         meta={"by_admin": user["id"]})
        await message.answer(
            f"✅ @{username.lstrip('@')} получил +{amount} фото."
        )
        return

    if sub == "tier" and len(args) == 3:
        username, tier = args[1], args[2].lower()
        if tier not in ("free", "pro", "premium"):
            await message.answer("⚠️ tier: free / pro / premium")
            return
        target = db.find_user_by_username(username)
        if not target:
            await message.answer(f"⚠️ Юзер @{username.lstrip('@')} не найден")
            return
        if tier == "free":
            supabase.table("users").update({"tier": "free", "tier_until": None}) \
                .eq("id", target["id"]).execute()
        else:
            db.upgrade_tier(target["id"], tier, days=30)
        await message.answer(f"✅ @{username.lstrip('@')} → tier={tier}")
        return

    if sub == "makeadmin" and len(args) == 2:
        username = args[1]
        target = db.find_user_by_username(username)
        if not target:
            await message.answer(f"⚠️ Юзер @{username.lstrip('@')} не найден")
            return
        supabase.table("users").update({"is_admin": True}) \
            .eq("id", target["id"]).execute()
        await message.answer(f"✅ @{username.lstrip('@')} теперь админ.")
        return

    await message.answer(HELP, parse_mode="Markdown")


async def _stats(message: Message):
    users_total = supabase.table("users").select("id", count="exact").execute().count or 0
    users_paid = supabase.table("users").select("id", count="exact") \
        .neq("tier", "free").execute().count or 0
    chars_total = supabase.table("characters").select("id", count="exact").execute().count or 0
    gens_done = supabase.table("generations").select("id", count="exact") \
        .eq("status", "done").execute().count or 0
    gens_failed = supabase.table("generations").select("id", count="exact") \
        .eq("status", "failed").execute().count or 0
    refs = supabase.table("referrals").select("id", count="exact").execute().count or 0

    text = (
        "📊 *Статистика*\n\n"
        f"👥 Юзеров: *{users_total}* (платных: *{users_paid}*)\n"
        f"💕 Персонажей создано: *{chars_total}*\n"
        f"📸 Моментов создано: *{gens_done}* (провалов: {gens_failed})\n"
        f"🤝 Рефералов: *{refs}*"
    )
    await message.answer(text, parse_mode="Markdown")
