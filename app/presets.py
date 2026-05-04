"""Scene presets. Each: Russian label + English prompt fragment.

Prompt structure when generating:
    [BASE_TRIGGERS] + [persona base] + [scene fragment] + [QUALITY_TAIL]
"""

# Trigger words for the UltraRealistic LoRA (from the model card)
BASE_TRIGGERS = "amateurish photo, low lighting, shot on iPhone, slightly noisy"
QUALITY_TAIL = "natural skin texture, candid moment, soft daylight, depth of field"

PRESETS: dict[str, dict] = {
    # --- Morning / home ---
    "morning_kitchen":  {"label": "☕ Утро на кухне",
                         "scene": "in a cozy kitchen in the morning, holding a coffee mug, soft window light, wearing oversized t-shirt"},
    "bed_selfie":       {"label": "🛏 Селфи в кровати",
                         "scene": "selfie lying in bed in the morning, messy hair, white sheets, sleepy smile"},
    "mirror_selfie":    {"label": "🪞 Селфи в зеркале",
                         "scene": "mirror selfie at home, holding phone, casual outfit, bedroom in background"},
    "balcony_morning":  {"label": "🌅 Утро на балконе",
                         "scene": "on a balcony in the morning, holding coffee, looking at the city, soft sunrise light"},

    # --- Cafe / city ---
    "cafe_window":      {"label": "🥐 Кафе у окна",
                         "scene": "sitting in a cafe by the window, laptop on table, warm afternoon light"},
    "city_walk_autumn": {"label": "🍂 Прогулка осенью",
                         "scene": "walking in the city in autumn, wearing a coat and scarf, fallen leaves, golden hour"},
    "city_walk_summer": {"label": "🌞 Прогулка летом",
                         "scene": "walking on a summer city street, sundress, warm evening light"},
    "park_bench":       {"label": "🌳 На скамейке в парке",
                         "scene": "sitting on a bench in a park, holding a book, dappled sunlight"},
    "rain_umbrella":    {"label": "☔ Под зонтом",
                         "scene": "standing under an umbrella on a rainy city street, wet pavement reflections"},

    # --- Sport / active ---
    "gym_mirror":       {"label": "💪 Селфи в зале",
                         "scene": "mirror selfie in a gym, sportswear, post-workout glow"},
    "yoga":             {"label": "🧘 Йога",
                         "scene": "doing yoga at home, yoga mat, leggings and crop top, morning light"},
    "running_park":     {"label": "🏃 Пробежка в парке",
                         "scene": "running in a park, athletic outfit, slightly out of breath, motion blur"},
    "tennis":           {"label": "🎾 Теннис",
                         "scene": "on a tennis court, holding racket, white tennis outfit"},

    # --- Outdoors / travel ---
    "beach":            {"label": "🏖 На пляже",
                         "scene": "on a beach, sundress fluttering, ocean in background, golden hour"},
    "mountain":         {"label": "🏔 В горах",
                         "scene": "hiking in mountains, backpack, fleece jacket, alpine vista"},
    "forest_walk":      {"label": "🌲 В лесу",
                         "scene": "walking in a forest path, sweater, soft natural light through trees"},
    "lake":             {"label": "🚣 У озера",
                         "scene": "by a calm lake at sunset, sitting on a wooden dock"},
    "snow":             {"label": "❄ В снегу",
                         "scene": "in winter snow, warm coat, knit hat, snowflakes, smiling"},

    # --- Casual / cozy ---
    "couch_cozy":       {"label": "🛋 На диване",
                         "scene": "curled up on a couch, blanket, holding a mug, warm lamp light"},
    "bookshop":         {"label": "📚 В книжном",
                         "scene": "browsing books in a bookshop, glasses, cozy sweater"},
    "cooking":          {"label": "🍳 Готовит дома",
                         "scene": "cooking pasta in a home kitchen, apron, laughing"},
    "studying":         {"label": "📖 Учится дома",
                         "scene": "at a desk studying, glasses, notebook, focused expression"},

    # --- Going out ---
    "restaurant":       {"label": "🍷 В ресторане",
                         "scene": "at a restaurant table in the evening, glass of wine, candlelight, elegant outfit"},
    "rooftop_night":    {"label": "🌃 Крыша ночью",
                         "scene": "on a rooftop at night, city lights bokeh, leather jacket"},
    "concert":          {"label": "🎵 На концерте",
                         "scene": "at a concert, stage lights in background, smiling"},
    "club":             {"label": "💃 В клубе",
                         "scene": "in a nightclub, neon and bokeh lights, party outfit"},

    # --- Cars / transport ---
    "car_passenger":    {"label": "🚗 В машине",
                         "scene": "sitting in a car passenger seat at night, city lights through window"},
    "metro":            {"label": "🚇 В метро",
                         "scene": "standing in a metro car, holding a handle, candid moment"},
    "airport":          {"label": "✈ В аэропорту",
                         "scene": "at an airport waiting area, suitcase, casual travel outfit"},

    # --- Festive ---
    "christmas":        {"label": "🎄 Новый год",
                         "scene": "by a Christmas tree, fairy lights, knit sweater, holding a mug of cocoa"},
}


def build_prompt(persona_base: str, preset_key: str) -> str:
    preset = PRESETS[preset_key]
    return f"{BASE_TRIGGERS}, {persona_base}, {preset['scene']}, {QUALITY_TAIL}"
