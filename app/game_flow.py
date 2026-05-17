"""Game-flow helpers for the companion bot.

Main product logic: create character -> first photo -> she writes first ->
free chat -> first meeting -> relationship growth -> romantic/soft18 unlocks.
"""
from __future__ import annotations

from app.persona import build_base_prompt
from app.presets import BASE_TRIGGERS, QUALITY_TAIL, ROMANTIC_TAIL

SOFT18_RELATIONSHIP_MIN = 8
ROMANTIC_RELATIONSHIP_MIN = 2


def persona_label(character: dict) -> str:
    persona = character.get("persona") or {}
    return ", ".join(
        str(persona.get(k, ""))
        for k in ("age_label", "hair_label", "body_label", "style_label")
        if persona.get(k)
    )


def build_intro_avatar_prompt(character: dict) -> str:
    """First character photo: natural private profile-style portrait."""
    persona_base = build_base_prompt(character["persona"])
    return (
        f"{BASE_TRIGGERS}, {persona_base}, "
        "natural private profile photo, phone portrait, looking into the camera, "
        "warm curious smile, cozy background, stylish casual outfit, tasteful, non-explicit, no nudity, "
        f"{QUALITY_TAIL}"
    )


def build_first_meeting_prompt(character: dict) -> str:
    """First meeting scene image."""
    persona_base = build_base_prompt(character["persona"])
    return (
        f"{BASE_TRIGGERS}, {persona_base}, "
        "first date mood in a cozy cafe near the window, rain outside, warm light, "
        "she notices the viewer and smiles, candid cinematic phone photo, tasteful romantic but non-explicit, casual outfit, "
        f"{ROMANTIC_TAIL}"
    )


def first_companion_message(character: dict) -> str:
    name = character.get("name") or "она"
    return (
        f"Привет… я {name}.\n\n"
        "Я посмотрела на твой профиль и почему-то задержалась. Есть в тебе что-то, из-за чего хочется не просто поставить лайк, а написать первой.\n\n"
        "Расскажешь мне о себе чуть честнее, чем обычно?"
    )


def first_meeting_text(character: dict) -> str:
    name = character.get("name") or "она"
    return (
        f"{name} сидит у окна. На улице дождь, в кафе пахнет кофе и выпечкой. "
        "Она замечает тебя, чуть улыбается и первой нарушает паузу:\n\n"
        "— Ну привет. Я думала, ты так и будешь смотреть издалека."
    )


def answer_text(choice: str) -> str:
    options = {
        "calm": "Привет. Я рад, что ты пришла. Просто не хотел испортить момент.",
        "bold": "Если честно, ты слишком притягательная, чтобы просто пройти мимо.",
        "funny": "Я хотел выглядеть уверенно, но ты сбила меня с роли.",
        "photo": "Мне нравится, как ты смотришь. Хочу увидеть тебя чуть ближе.",
    }
    return options.get(choice, options["calm"])
