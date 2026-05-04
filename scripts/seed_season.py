"""Load a season+character+episodes JSON into Supabase.

Usage:
    python -m scripts.seed_season content/season_anna_pilot.json

Idempotent: re-running updates existing records by slug/number.
"""
import json
import sys
from pathlib import Path

from app.db import supabase


def upsert_character(char_data: dict) -> int:
    existing = supabase.table("story_characters").select("*").eq("slug", char_data["slug"]).execute()
    payload = {
        "slug": char_data["slug"],
        "name": char_data["name"],
        "bio": char_data.get("bio"),
        "persona": char_data["persona"],
        "master_seed": char_data["master_seed"],
    }
    if existing.data:
        cid = existing.data[0]["id"]
        supabase.table("story_characters").update(payload).eq("id", cid).execute()
        print(f"  Updated character: {char_data['name']} (id={cid})")
        return cid
    res = supabase.table("story_characters").insert(payload).execute()
    cid = res.data[0]["id"]
    print(f"  Created character: {char_data['name']} (id={cid})")
    return cid


def upsert_season(season_data: dict, character_id: int) -> int:
    existing = supabase.table("seasons").select("*").eq("slug", season_data["slug"]).execute()
    payload = {
        "slug": season_data["slug"],
        "title": season_data["title"],
        "description": season_data.get("description"),
        "character_id": character_id,
        "is_active": season_data.get("is_active", True),
    }
    if existing.data:
        sid = existing.data[0]["id"]
        supabase.table("seasons").update(payload).eq("id", sid).execute()
        print(f"  Updated season: {season_data['title']} (id={sid})")
        return sid
    res = supabase.table("seasons").insert(payload).execute()
    sid = res.data[0]["id"]
    print(f"  Created season: {season_data['title']} (id={sid})")
    return sid


def upsert_episode(season_id: int, ep: dict) -> int:
    existing = supabase.table("episodes").select("*") \
        .eq("season_id", season_id).eq("number", ep["number"]).execute()
    payload = {
        "season_id": season_id,
        "number": ep["number"],
        "title": ep["title"],
        "hook_text": ep.get("hook_text"),
        "is_premium": ep.get("is_premium", False),
        "beats_json": ep["beats_json"],
        "unlock_after_hours": ep.get("unlock_after_hours", 24),
    }
    if existing.data:
        eid = existing.data[0]["id"]
        supabase.table("episodes").update(payload).eq("id", eid).execute()
        print(f"  Updated episode {ep['number']}: {ep['title']} (id={eid})")
        return eid
    res = supabase.table("episodes").insert(payload).execute()
    eid = res.data[0]["id"]
    print(f"  Created episode {ep['number']}: {ep['title']} (id={eid})")
    return eid


def main(path: str) -> None:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    print(f"Loading: {path}")

    cid = upsert_character(data["character"])
    sid = upsert_season(data["season"], cid)
    for ep in data["episodes"]:
        upsert_episode(sid, ep)

    print("\n✅ Done.")
    print("\n⚠️  Reminder: image_url fields are empty in the JSON.")
    print("   Run `python -m scripts.pregenerate_episode <ep_number>` to generate")
    print("   images for each beat and update them in the DB.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m scripts.seed_season <path/to/season.json>")
        sys.exit(1)
    main(sys.argv[1])
