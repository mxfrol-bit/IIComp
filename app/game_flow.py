"""Game-flow helpers for the companion bot.

This module keeps the product logic readable: creation -> first portrait -> first
message -> first meeting -> relationship growth -> romantic/soft18 unlocks.
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
    """First character card image: game-like but realistic portrait."""
    persona_base = build_base_prompt(character["persona"])
    return (
        f"{BASE_TRIGGERS}, {persona_base}, "
        "first private profile photo in an interactive romance story, natural phone portrait, "
        "looking into the camera, warm curious smile, clean cozy background, "
        "tasteful stylish outfit, non-explicit, no nudity, first message mood, "
        f"{QUALITY_TAIL}"
    )


def build_first_meeting_prompt(character: dict) -> str:
    """First meeting scene image."""
    persona_base = build_base_prompt(character["persona"])
    return (
        f"{BASE_TRIGGERS}, {persona_base}, "
        "first meeting scene in a cozy cafe near the window, rain outside, warm light, "
        "she notices the viewer and smiles like the story just began, candid cinematic photo, "
        "tasteful romantic but non-explicit, casual outfit, "
        f"{ROMANTIC_TAIL}"
    )


def first_companion_message(character: dict) -> str:
    name = character.get("name") or "она"
    return (
        f"Привет… я {name}. Кажется, мы только что совпали в этой истории 🙂\n\n"
        "Не будем делать вид, что мы давно знакомы. Но мне правда интересно, какой ты: "
        "ты видишь моё первое фото, а я хочу понять, какой ты.\n\n"
        "С чего начнём — поговорим здесь или представим нашу первую встречу?"
    )


def first_meeting_text(character: dict) -> str:
    name = character.get("name") or "она"
    return (
        f"☕ *Первая встреча*\n\n"
        f"{name} сидит у окна. На улице дождь, в кафе пахнет кофе и выпечкой. "
        "Она замечает тебя, чуть улыбается и первой нарушает паузу:\n\n"
        f"— Ну привет. Я думала, ты так и будешь смотреть издалека."
    )


def answer_text(choice: str) -> str:
    options = {
        "calm": "Я спокойно улыбаюсь и говорю: «Привет. Просто не хотел испортить момент.»",
        "bold": "Я смотрю ей в глаза: «Если честно, ты слишком притягательная, чтобы просто пройти мимо.»",
        "funny": "Я улыбаюсь: «Я хотел выглядеть уверенно, но ты сбила меня с роли.»",
        "photo": "Я говорю: «Мне нравится, как ты смотришь. Покажешь мне ещё один момент?»",
    }
    return options.get(choice, options["calm"])
