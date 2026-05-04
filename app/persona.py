"""Persona builder — options shown via inline keyboards. All adults."""

AGE_RANGES = {
    "20_22": ("20–22", "20-22 years old"),
    "23_26": ("23–26", "23-26 years old"),
    "27_30": ("27–30", "27-30 years old"),
}

HAIR = {
    "long_blonde":   ("Длинные блонд", "long blonde hair"),
    "long_brown":    ("Длинные шатен",  "long brown hair"),
    "long_black":    ("Длинные брюнет", "long black hair"),
    "long_red":      ("Длинные рыжие",  "long red hair"),
    "short_blonde":  ("Короткие блонд", "short blonde hair, bob cut"),
    "short_brown":   ("Короткие шатен", "short brown hair, bob cut"),
}

BODY = {
    "slim":      ("Стройная",     "slim build"),
    "athletic":  ("Спортивная",   "athletic build, toned"),
    "curvy":     ("Фигуристая",   "curvy build, hourglass figure"),
    "average":   ("Средняя",      "average build"),
}

STYLE = {
    "student":   ("Студентка",    "casual student style, jeans and hoodies"),
    "sporty":    ("Спортивная",   "sporty athleisure style"),
    "business":  ("Деловая",      "smart business casual style"),
    "alt":       ("Альт",         "alternative style, dark clothes, tattoos"),
    "boho":      ("Бохо",         "boho style, flowy dresses"),
    "elegant":   ("Элегантная",   "elegant minimal style"),
}


def build_base_prompt(persona: dict) -> str:
    """Compose the persistent character description used in every generation."""
    parts = [
        persona["age_desc"],
        persona["hair_desc"],
        persona["body_desc"],
        persona["style_desc"],
    ]
    return ", ".join(parts)
