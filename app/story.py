"""Story engine: episode loading, beat progression, unlock logic."""
from datetime import datetime, timedelta, timezone
from typing import Optional

from app.db import supabase


# ---------- Seasons & characters ----------

def get_active_seasons() -> list[dict]:
    res = supabase.table("seasons").select("*").eq("is_active", True).order("id").execute()
    return res.data


def get_season(season_id: int) -> Optional[dict]:
    res = supabase.table("seasons").select("*").eq("id", season_id).execute()
    return res.data[0] if res.data else None


def get_story_character(character_id: int) -> Optional[dict]:
    res = supabase.table("story_characters").select("*").eq("id", character_id).execute()
    return res.data[0] if res.data else None


# ---------- Episodes ----------

def get_episodes(season_id: int) -> list[dict]:
    res = supabase.table("episodes").select("*").eq("season_id", season_id).order("number").execute()
    return res.data


def get_episode(episode_id: int) -> Optional[dict]:
    res = supabase.table("episodes").select("*").eq("id", episode_id).execute()
    return res.data[0] if res.data else None


def get_episode_by_number(season_id: int, number: int) -> Optional[dict]:
    res = supabase.table("episodes").select("*").eq("season_id", season_id).eq("number", number).execute()
    return res.data[0] if res.data else None


# ---------- Progress ----------

def get_progress(user_id: int, episode_id: int) -> Optional[dict]:
    res = supabase.table("user_progress").select("*") \
        .eq("user_id", user_id).eq("episode_id", episode_id).execute()
    return res.data[0] if res.data else None


def start_episode(user_id: int, season_id: int, episode: dict) -> dict:
    """Create or return existing progress for an episode."""
    existing = get_progress(user_id, episode["id"])
    if existing:
        return existing

    start_beat = episode["beats_json"]["start_beat"]
    res = supabase.table("user_progress").insert({
        "user_id": user_id,
        "season_id": season_id,
        "episode_id": episode["id"],
        "current_beat": start_beat,
        "completed_beats": [],
    }).execute()

    log_event(user_id, "episode_started", episode_id=episode["id"])
    return res.data[0]


def advance_beat(user_id: int, episode_id: int, next_beat: str) -> dict:
    progress = get_progress(user_id, episode_id)
    if not progress:
        raise ValueError("No progress for this episode")

    completed = progress.get("completed_beats", []) or []
    if progress["current_beat"] not in completed:
        completed.append(progress["current_beat"])

    res = supabase.table("user_progress").update({
        "current_beat": next_beat,
        "completed_beats": completed,
        "last_beat_at": datetime.now(timezone.utc).isoformat(),
    }).eq("id", progress["id"]).execute()

    return res.data[0]


def complete_episode(user_id: int, episode_id: int) -> None:
    supabase.table("user_progress").update({
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }).eq("user_id", user_id).eq("episode_id", episode_id).execute()
    log_event(user_id, "episode_completed", episode_id=episode_id)

    # Schedule next episode unlock
    episode = get_episode(episode_id)
    if not episode:
        return
    next_ep = get_episode_by_number(episode["season_id"], episode["number"] + 1)
    if not next_ep:
        return

    unlock_at = datetime.now(timezone.utc) + timedelta(hours=episode.get("unlock_after_hours") or 24)
    # Free unlock — record it as future-unlocked
    existing = supabase.table("episode_unlocks").select("*") \
        .eq("user_id", user_id).eq("episode_id", next_ep["id"]).execute()
    if not existing.data:
        supabase.table("episode_unlocks").insert({
            "user_id": user_id,
            "episode_id": next_ep["id"],
            "unlocked_at": unlock_at.isoformat(),
            "unlock_reason": "completed_previous",
        }).execute()


def is_episode_unlocked(user_id: int, episode: dict) -> tuple[bool, Optional[datetime]]:
    """Return (unlocked, unlock_time_if_future)."""
    # Episode 1 is always unlocked
    if episode["number"] == 1:
        return True, None

    res = supabase.table("episode_unlocks").select("*") \
        .eq("user_id", user_id).eq("episode_id", episode["id"]).execute()
    if not res.data:
        return False, None

    unlock_at = datetime.fromisoformat(res.data[0]["unlocked_at"].replace("Z", "+00:00"))
    if datetime.now(timezone.utc) >= unlock_at:
        return True, None
    return False, unlock_at


def force_unlock_episode(user_id: int, episode_id: int, reason: str = "paid_skip") -> None:
    now = datetime.now(timezone.utc).isoformat()
    existing = supabase.table("episode_unlocks").select("*") \
        .eq("user_id", user_id).eq("episode_id", episode_id).execute()
    if existing.data:
        supabase.table("episode_unlocks").update({
            "unlocked_at": now, "unlock_reason": reason,
        }).eq("user_id", user_id).eq("episode_id", episode_id).execute()
    else:
        supabase.table("episode_unlocks").insert({
            "user_id": user_id,
            "episode_id": episode_id,
            "unlocked_at": now,
            "unlock_reason": reason,
        }).execute()
    log_event(user_id, "unlock_purchased", episode_id=episode_id, meta={"reason": reason})


# ---------- Beat resolution ----------

def get_beat(episode: dict, beat_key: str) -> Optional[dict]:
    return episode["beats_json"].get("beats", {}).get(beat_key)


def is_end_beat(episode: dict, beat_key: str) -> bool:
    return beat_key in episode["beats_json"].get("end_beats", [])


# ---------- Events / analytics ----------

def log_event(user_id: int, event: str, episode_id: Optional[int] = None,
              beat_key: Optional[str] = None, meta: Optional[dict] = None) -> None:
    supabase.table("story_events").insert({
        "user_id": user_id,
        "event": event,
        "episode_id": episode_id,
        "beat_key": beat_key,
        "meta": meta or {},
    }).execute()
