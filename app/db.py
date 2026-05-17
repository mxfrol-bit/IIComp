"""Supabase client + helpers. Service-role key, server-side only."""
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import httpx
from supabase import Client, create_client

from app.config import settings

supabase: Client = create_client(settings.supabase_url, settings.supabase_service_key)


# ---------- Users ----------

def get_or_create_user(tg_id: int, tg_username: Optional[str] = None) -> dict:
    res = supabase.table("users").select("*").eq("tg_id", tg_id).execute()
    if res.data:
        return res.data[0]

    inserted = supabase.table("users").insert({
        "tg_id": tg_id,
        "tg_username": tg_username,
        "credits": settings.free_daily_credits,
    }).execute()
    return inserted.data[0]


def confirm_age(user_id: int) -> None:
    supabase.table("users").update({
        "age_confirmed": True,
        "age_confirmed_at": datetime.now(timezone.utc).isoformat(),
    }).eq("id", user_id).execute()


def set_content_mode(user_id: int, mode: str) -> None:
    if mode not in ("safe", "romantic", "soft18"):
        mode = "safe"
    supabase.table("users").update({"content_mode": mode}).eq("id", user_id).execute()


def refresh_daily_credits(user: dict) -> dict:
    """Reset credits if reset window passed."""
    reset_at_str = user.get("credits_reset_at")
    if not reset_at_str:
        return user
    reset_at = datetime.fromisoformat(reset_at_str.replace("Z", "+00:00"))
    if datetime.now(timezone.utc) < reset_at:
        return user

    daily = settings.pro_daily_credits if user["tier"] in ("pro", "premium") else settings.free_daily_credits
    new_reset = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    updated = supabase.table("users").update({
        "credits": daily,
        "credits_reset_at": new_reset,
    }).eq("id", user["id"]).execute()

    supabase.table("credits_ledger").insert({
        "user_id": user["id"],
        "delta": daily,
        "reason": "daily_grant",
    }).execute()
    return updated.data[0]


def spend_credit(user_id: int, reason: str = "generation") -> bool:
    """Atomic-ish decrement. Returns False if no credits."""
    user = supabase.table("users").select("credits").eq("id", user_id).execute().data[0]
    if user["credits"] <= 0:
        return False
    supabase.table("users").update({"credits": user["credits"] - 1}).eq("id", user_id).execute()
    supabase.table("credits_ledger").insert({
        "user_id": user_id,
        "delta": -1,
        "reason": reason,
    }).execute()
    return True


def grant_credits(user_id: int, amount: int, reason: str, meta: Optional[dict] = None) -> None:
    user = supabase.table("users").select("credits").eq("id", user_id).execute().data[0]
    supabase.table("users").update({"credits": user["credits"] + amount}).eq("id", user_id).execute()
    supabase.table("credits_ledger").insert({
        "user_id": user_id,
        "delta": amount,
        "reason": reason,
        "meta": meta or {},
    }).execute()


def upgrade_tier(user_id: int, tier: str, days: int = 30) -> None:
    until = (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()
    supabase.table("users").update({"tier": tier, "tier_until": until}).eq("id", user_id).execute()


# ---------- Characters ----------

def create_character(user_id: int, name: str, persona: dict, seed: int) -> dict:
    res = supabase.table("characters").insert({
        "user_id": user_id,
        "name": name,
        "persona": persona,
        "seed": seed,
    }).execute()
    return res.data[0]


def get_user_characters(user_id: int) -> list[dict]:
    res = supabase.table("characters").select("*").eq("user_id", user_id).order("created_at").execute()
    return res.data


def get_character(character_id: int) -> Optional[dict]:
    res = supabase.table("characters").select("*").eq("id", character_id).execute()
    return res.data[0] if res.data else None


def set_character_reference(character_id: int, image_url: str) -> None:
    supabase.table("characters").update({"reference_url": image_url}).eq("id", character_id).execute()


def set_character_avatar(character_id: int, avatar_url: str) -> None:
    """Set character avatar (first generated photo). Idempotent — only sets if empty."""
    res = supabase.table("characters").select("avatar_url").eq("id", character_id).execute()
    if res.data and not res.data[0].get("avatar_url"):
        supabase.table("characters").update({"avatar_url": avatar_url}).eq("id", character_id).execute()


def delete_character(character_id: int, user_id: int) -> bool:
    """Delete a character. Returns True if deleted, False if not owned by user."""
    res = supabase.table("characters").select("user_id").eq("id", character_id).execute()
    if not res.data or res.data[0]["user_id"] != user_id:
        return False
    supabase.table("characters").delete().eq("id", character_id).execute()
    return True


# ---------- Generations ----------

def create_generation(user_id: int, character_id: int, preset_key: str, prompt: str) -> dict:
    res = supabase.table("generations").insert({
        "user_id": user_id,
        "character_id": character_id,
        "preset_key": preset_key,
        "prompt": prompt,
    }).execute()
    return res.data[0]


def update_generation(gen_id: int, **fields: Any) -> None:
    supabase.table("generations").update(fields).eq("id", gen_id).execute()


def get_recent_generations(user_id: int, limit: int = 10) -> list[dict]:
    """Fetch last N successful generations for the user."""
    res = supabase.table("generations").select("*") \
        .eq("user_id", user_id).eq("status", "done") \
        .order("created_at", desc=True).limit(limit).execute()
    return res.data


# ---------- Referrals ----------

def get_referrer(user_id: int) -> Optional[dict]:
    res = supabase.table("referrals").select("*").eq("referred_id", user_id).execute()
    return res.data[0] if res.data else None


def create_referral(referrer_id: int, referred_id: int) -> Optional[dict]:
    """Create referral link. No-op if user already has a referrer or refers themselves."""
    if referrer_id == referred_id:
        return None
    if get_referrer(referred_id):
        return None
    try:
        res = supabase.table("referrals").insert({
            "referrer_id": referrer_id,
            "referred_id": referred_id,
        }).execute()
        return res.data[0]
    except Exception:
        return None


def grant_referral_bonus(referred_id: int, bonus_credits: int = 5) -> Optional[int]:
    """Give bonus credits to the referrer when the referred user does their first action.
    Returns referrer_id if granted, None otherwise."""
    referral = get_referrer(referred_id)
    if not referral or referral.get("bonus_granted"):
        return None

    referrer_id = referral["referrer_id"]
    grant_credits(referrer_id, bonus_credits, "referral_bonus",
                  meta={"referred_user_id": referred_id})
    supabase.table("referrals").update({"bonus_granted": True}) \
        .eq("id", referral["id"]).execute()
    return referrer_id


def count_referrals(user_id: int) -> int:
    res = supabase.table("referrals").select("id", count="exact") \
        .eq("referrer_id", user_id).execute()
    return res.count or 0


# ---------- Admin ----------

def is_admin(user_id: int) -> bool:
    res = supabase.table("users").select("is_admin").eq("id", user_id).execute()
    return bool(res.data and res.data[0].get("is_admin"))


def find_user_by_username(username: str) -> Optional[dict]:
    username = username.lstrip("@")
    res = supabase.table("users").select("*").eq("tg_username", username).execute()
    return res.data[0] if res.data else None


# ---------- Storage ----------

async def upload_image_from_url(remote_url: str, dest_path: str) -> str:
    """Download image from Replicate and upload to Supabase Storage. Returns public URL."""
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.get(remote_url)
        resp.raise_for_status()
        data = resp.content

    supabase.storage.from_("generations").upload(
        dest_path, data,
        file_options={"content-type": "image/jpeg", "upsert": "true"},
    )
    return supabase.storage.from_("generations").get_public_url(dest_path)


# ---------- Companion chat / game state ----------

def set_active_character(user_id: int, character_id: int | None, enabled: bool = True) -> None:
    fields = {"active_character_id": character_id, "chat_enabled": enabled}
    supabase.table("users").update(fields).eq("id", user_id).execute()


def get_active_character_for_user(user_id: int) -> Optional[dict]:
    res = supabase.table("users").select("active_character_id").eq("id", user_id).execute()
    if not res.data or not res.data[0].get("active_character_id"):
        return None
    return get_character(res.data[0]["active_character_id"])


def update_relationship(user_id: int, delta: int) -> int:
    res = supabase.table("users").select("relationship_score").eq("id", user_id).execute()
    current = 0
    if res.data:
        current = int(res.data[0].get("relationship_score") or 0)
    new_score = max(0, min(100, current + delta))
    supabase.table("users").update({"relationship_score": new_score}).eq("id", user_id).execute()
    return new_score


def get_relationship(user_id: int) -> int:
    res = supabase.table("users").select("relationship_score").eq("id", user_id).execute()
    if not res.data:
        return 0
    return int(res.data[0].get("relationship_score") or 0)


def add_chat_message(user_id: int, character_id: int, role: str, content: str, event_type: str = "chat", meta: Optional[dict] = None) -> None:
    supabase.table("chat_messages").insert({
        "user_id": user_id,
        "character_id": character_id,
        "role": role,
        "content": content,
        "event_type": event_type,
        "meta": meta or {},
    }).execute()


def get_chat_history(user_id: int, character_id: int, limit: int = 12) -> list[dict]:
    res = supabase.table("chat_messages").select("role, content, created_at") \
        .eq("user_id", user_id).eq("character_id", character_id) \
        .order("created_at", desc=True).limit(limit).execute()
    return list(reversed(res.data or []))


def get_generation(gen_id: int, user_id: Optional[int] = None) -> Optional[dict]:
    q = supabase.table("generations").select("*").eq("id", gen_id)
    if user_id is not None:
        q = q.eq("user_id", user_id)
    res = q.execute()
    return res.data[0] if res.data else None


def update_generation_video(gen_id: int, video_url: str | None = None, status: str = "done", prompt: str | None = None) -> None:
    fields: dict[str, Any] = {"video_status": status}
    if video_url is not None:
        fields["video_url"] = video_url
    if prompt is not None:
        fields["video_prompt"] = prompt
    supabase.table("generations").update(fields).eq("id", gen_id).execute()


async def upload_file_from_url(remote_url: str, dest_path: str, content_type: str = "application/octet-stream") -> str:
    async with httpx.AsyncClient(timeout=180) as client:
        resp = await client.get(remote_url)
        resp.raise_for_status()
        data = resp.content

    supabase.storage.from_("generations").upload(
        dest_path, data,
        file_options={"content-type": content_type, "upsert": "true"},
    )
    return supabase.storage.from_("generations").get_public_url(dest_path)

# ---------- Payments ----------

def record_payment(user_id: int, telegram_payment_id: str, provider_payment_id: str,
                   amount_stars: int, tier: str) -> None:
    supabase.table("payments").insert({
        "user_id": user_id,
        "telegram_payment_id": telegram_payment_id,
        "provider_payment_id": provider_payment_id,
        "amount_stars": amount_stars,
        "tier": tier,
        "status": "completed",
    }).execute()
