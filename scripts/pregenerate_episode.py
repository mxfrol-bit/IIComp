"""Pre-generate images for all beats of an episode and update DB.

Usage:
    python -m scripts.pregenerate_episode <season_slug> <episode_number>

Example:
    python -m scripts.pregenerate_episode anna_s1 1

Strategy:
- Read episode from DB
- For each beat without image_url, build prompt:
    BASE_TRIGGERS + character.persona + beat.image_prompt_hint + QUALITY_TAIL
- Generate via Replicate using master_seed for face consistency
- Upload to Supabase Storage at: seasons/<slug>/ep<n>/<beat>.jpg
- Update beats_json[beat_key].image_url
- Save back to DB
"""
import asyncio
import sys
import time

from app import db
from app.db import supabase
from app.presets import BASE_TRIGGERS, QUALITY_TAIL
from app.image_client import generate_image


def build_persona_base(persona: dict) -> str:
    parts = [
        persona.get("age_desc", ""),
        persona.get("hair_desc", ""),
        persona.get("face_desc", ""),
        persona.get("body_desc", ""),
        persona.get("style_desc", ""),
    ]
    return ", ".join(p for p in parts if p)


async def main(season_slug: str, episode_number: int) -> None:
    # Load season
    season_res = supabase.table("seasons").select("*").eq("slug", season_slug).execute()
    if not season_res.data:
        print(f"❌ Season not found: {season_slug}")
        sys.exit(1)
    season = season_res.data[0]

    # Load character
    char_res = supabase.table("story_characters").select("*").eq("id", season["character_id"]).execute()
    character = char_res.data[0]
    persona_base = build_persona_base(character["persona"])
    seed = character["master_seed"]

    # Load episode
    ep_res = supabase.table("episodes").select("*") \
        .eq("season_id", season["id"]).eq("number", episode_number).execute()
    if not ep_res.data:
        print(f"❌ Episode {episode_number} not found in season {season_slug}")
        sys.exit(1)
    episode = ep_res.data[0]

    beats_json = episode["beats_json"]
    beats = beats_json["beats"]

    print(f"Pre-generating ep.{episode_number} '{episode['title']}'")
    print(f"Character: {character['name']} (seed={seed})")
    print(f"Persona base: {persona_base}\n")

    for beat_key, beat in beats.items():
        if beat.get("image_url"):
            print(f"  [skip] {beat_key} — already has image_url")
            continue
        hint = beat.get("image_prompt_hint")
        if not hint:
            print(f"  [skip] {beat_key} — no image_prompt_hint")
            continue

        prompt = f"{BASE_TRIGGERS}, {persona_base}, {hint}, {QUALITY_TAIL}"
        print(f"  [gen ] {beat_key}: {hint[:60]}...")

        try:
            image_url = await generate_image(prompt=prompt, seed=seed)
        except Exception as e:
            print(f"  ❌ Generation failed for {beat_key}: {e}")
            continue

        # Upload to Storage
        dest = f"seasons/{season_slug}/ep{episode_number}/{beat_key}_{int(time.time())}.jpg"
        try:
            stored_url = await db.upload_image_from_url(image_url, dest)
        except Exception as e:
            print(f"  ⚠️  Storage upload failed for {beat_key}: {e}")
            stored_url = image_url

        beats[beat_key]["image_url"] = stored_url
        print(f"  ✅ {beat_key} → {stored_url}")

        # Save partial progress on every beat (in case of crash)
        supabase.table("episodes").update({"beats_json": beats_json}) \
            .eq("id", episode["id"]).execute()

    print(f"\n✅ Episode {episode_number} pre-generation complete.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python -m scripts.pregenerate_episode <season_slug> <episode_number>")
        sys.exit(1)
    asyncio.run(main(sys.argv[1], int(sys.argv[2])))
