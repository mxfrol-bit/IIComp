"""Scene presets with content ratings.

Ratings:
- safe: обычные сцены, доступны всем 18+ пользователям.
- romantic: романтика/поцелуи/свидания, доступны всем 18+ пользователям.
- soft18: более смелые, но не explicit: бельё, купальник, халат, утро в постели без обнажения.
  Доступ открывается через Pro/Premium.
"""

BASE_TRIGGERS = "amateurish photo, low lighting, shot on iPhone, slightly noisy, Super Realism"
QUALITY_TAIL = "natural skin texture, candid moment, soft daylight, depth of field, realistic everyday photo"
ROMANTIC_TAIL = "warm romantic mood, gentle expression, cinematic but natural, tasteful and non-explicit"
SOFT18_TAIL = "tasteful soft romantic photo, covered body, non-explicit, elegant, natural body language"

# callback_data лимит Telegram 64 байта, поэтому ключи короткие.
PRESETS: dict[str, dict] = {
    # --- SFW / base scenes ---
    "morning_kitchen":  {"label": "☕ Утро на кухне", "rating": "safe", "category": "home",
                         "scene": "in a cozy kitchen in the morning, holding a coffee mug, soft window light, wearing oversized t-shirt"},
    "bed_selfie":       {"label": "🛏 Селфи в кровати", "rating": "safe", "category": "home",
                         "scene": "selfie lying in bed in the morning, messy hair, white sheets, sleepy smile, wearing comfortable pajamas"},
    "mirror_selfie":    {"label": "🪞 Селфи в зеркале", "rating": "safe", "category": "home",
                         "scene": "mirror selfie at home, holding phone, casual outfit, bedroom in background"},
    "balcony_morning":  {"label": "🌅 Утро на балконе", "rating": "safe", "category": "home",
                         "scene": "on a balcony in the morning, holding coffee, looking at the city, soft sunrise light"},
    "cafe_window":      {"label": "🥐 Кафе у окна", "rating": "safe", "category": "city",
                         "scene": "sitting in a cafe by the window, laptop on table, warm afternoon light"},
    "city_walk_autumn": {"label": "🍂 Прогулка осенью", "rating": "safe", "category": "city",
                         "scene": "walking in the city in autumn, wearing a coat and scarf, fallen leaves, golden hour"},
    "city_walk_summer": {"label": "🌞 Прогулка летом", "rating": "safe", "category": "city",
                         "scene": "walking on a summer city street, sundress, warm evening light"},
    "park_bench":       {"label": "🌳 Парк", "rating": "safe", "category": "city",
                         "scene": "sitting on a bench in a park, holding a book, dappled sunlight"},
    "rain_umbrella":    {"label": "☔ Под зонтом", "rating": "safe", "category": "city",
                         "scene": "standing under an umbrella on a rainy city street, wet pavement reflections"},
    "gym_mirror":       {"label": "💪 Селфи в зале", "rating": "safe", "category": "sport",
                         "scene": "mirror selfie in a gym, sportswear, post-workout glow"},
    "yoga":             {"label": "🧘 Йога", "rating": "safe", "category": "sport",
                         "scene": "doing yoga at home, yoga mat, leggings and crop top, morning light"},
    "running_park":     {"label": "🏃 Пробежка", "rating": "safe", "category": "sport",
                         "scene": "running in a park, athletic outfit, slightly out of breath, motion blur"},
    "tennis":           {"label": "🎾 Теннис", "rating": "safe", "category": "sport",
                         "scene": "on a tennis court, holding racket, white tennis outfit"},
    "beach":            {"label": "🏖 Пляж", "rating": "safe", "category": "travel",
                         "scene": "on a beach, sundress fluttering, ocean in background, golden hour"},
    "mountain":         {"label": "🏔 В горах", "rating": "safe", "category": "travel",
                         "scene": "hiking in mountains, backpack, fleece jacket, alpine vista"},
    "forest_walk":      {"label": "🌲 В лесу", "rating": "safe", "category": "travel",
                         "scene": "walking in a forest path, sweater, soft natural light through trees"},
    "lake":             {"label": "🚣 У озера", "rating": "safe", "category": "travel",
                         "scene": "by a calm lake at sunset, sitting on a wooden dock"},
    "snow":             {"label": "❄ В снегу", "rating": "safe", "category": "travel",
                         "scene": "in winter snow, warm coat, knit hat, snowflakes, smiling"},
    "couch_cozy":       {"label": "🛋 На диване", "rating": "safe", "category": "cozy",
                         "scene": "curled up on a couch, blanket, holding a mug, warm lamp light"},
    "bookshop":         {"label": "📚 В книжном", "rating": "safe", "category": "cozy",
                         "scene": "browsing books in a bookshop, glasses, cozy sweater"},
    "cooking":          {"label": "🍳 Готовит", "rating": "safe", "category": "cozy",
                         "scene": "cooking pasta in a home kitchen, apron, laughing"},
    "studying":         {"label": "📖 Учится", "rating": "safe", "category": "cozy",
                         "scene": "at a desk studying, glasses, notebook, focused expression"},
    "restaurant":       {"label": "🍷 Ресторан", "rating": "safe", "category": "night",
                         "scene": "at a restaurant table in the evening, glass of wine, candlelight, elegant outfit"},
    "rooftop_night":    {"label": "🌃 Крыша", "rating": "safe", "category": "night",
                         "scene": "on a rooftop at night, city lights bokeh, leather jacket"},
    "concert":          {"label": "🎵 Концерт", "rating": "safe", "category": "night",
                         "scene": "at a concert, stage lights in background, smiling"},
    "club":             {"label": "💃 Клуб", "rating": "safe", "category": "night",
                         "scene": "in a nightclub, neon and bokeh lights, party outfit"},
    "car_passenger":    {"label": "🚗 В машине", "rating": "safe", "category": "transport",
                         "scene": "sitting in a car passenger seat at night, city lights through window"},
    "metro":            {"label": "🚇 Метро", "rating": "safe", "category": "transport",
                         "scene": "standing in a metro car, holding a handle, candid moment"},
    "airport":          {"label": "✈ Аэропорт", "rating": "safe", "category": "transport",
                         "scene": "at an airport waiting area, suitcase, casual travel outfit"},
    "christmas":        {"label": "🎄 Новый год", "rating": "safe", "category": "holiday",
                         "scene": "by a Christmas tree, fairy lights, knit sweater, holding a mug of cocoa"},

    # --- Romantic, non-explicit ---
    "date_cafe":        {"label": "❤️ Свидание в кафе", "rating": "romantic", "category": "romance",
                         "scene": "on a cozy first date in a cafe, smiling warmly at camera, soft candle light, elegant casual outfit"},
    "kiss_cheek":       {"label": "💋 Поцелуй в щёку", "rating": "romantic", "category": "romance",
                         "scene": "gentle cheek kiss moment, warm smile, tasteful romantic atmosphere, casual clothing"},
    "hug_evening":      {"label": "🤗 Объятия вечером", "rating": "romantic", "category": "romance",
                         "scene": "soft evening hug near city lights, cozy coat, tender smile, cinematic bokeh"},
    "movie_night":      {"label": "🎬 Вечер кино", "rating": "romantic", "category": "romance",
                         "scene": "cozy movie night on a couch, blanket, popcorn, warm lamp light, wearing comfortable home clothes"},
    "balcony_date":     {"label": "🌙 Балкон ночью", "rating": "romantic", "category": "romance",
                         "scene": "romantic balcony at night, city lights, holding a cup of tea, soft smile, elegant cardigan"},
    "car_date":         {"label": "🚘 Ночное селфи", "rating": "romantic", "category": "romance",
                         "scene": "night car selfie after a date, city lights through window, gentle smile, tasteful romantic mood"},
    "flower_reaction":  {"label": "🌹 Реакция на цветы", "rating": "romantic", "category": "romance",
                         "scene": "holding a small bouquet of flowers, surprised happy smile, home hallway, natural phone photo"},
    "good_morning_msg": {"label": "☀️ Доброе утро", "rating": "romantic", "category": "romance",
                         "scene": "good morning selfie, messy hair, oversized hoodie, warm window light, gentle romantic expression"},

    "date_close_table":  {"label": "🔥 Близко за столиком", "rating": "romantic", "category": "romance",
                         "scene": "sitting very close across a small cafe table, intense eye contact, playful smile, warm candle light, tasteful romantic tension"},
    "taxi_after_date":   {"label": "🔥 Такси после свидания", "rating": "romantic", "category": "romance",
                         "scene": "back seat of a taxi after a date, city lights through window, leaning closer, playful confident smile, tasteful romantic mood"},
    "doorway_goodnight": {"label": "🔥 У двери", "rating": "romantic", "category": "romance",
                         "scene": "standing in a doorway after a date, warm hallway light, almost goodbye moment, teasing smile, tasteful non-explicit tension"},
    "slow_dance_home":   {"label": "🔥 Медленный танец", "rating": "romantic", "category": "romance",
                         "scene": "slow dance at home in dim warm light, close but tasteful, soft smile, romantic tension, elegant home clothes"},

    # --- Soft 18+, non-explicit, Pro/Premium gate ---
    "soft_pajama":      {"label": "🔞 Пижама", "rating": "soft18", "category": "soft18",
                         "scene": "tasteful bedroom selfie in silk pajamas, soft morning light, covered body, elegant and cozy"},
    "soft_lingerie_shirt": {"label": "🔞 Рубашка", "rating": "soft18", "category": "soft18",
                         "scene": "tasteful mirror selfie wearing an oversized white shirt over elegant lingerie, covered body, soft bedroom light"},
    "soft_beach_bikini": {"label": "🔞 Купальник", "rating": "soft18", "category": "soft18",
                         "scene": "beach selfie in a stylish bikini, golden hour, natural smile, tasteful non-explicit summer photo"},
    "soft_bathrobe":    {"label": "🔞 Халат", "rating": "soft18", "category": "soft18",
                         "scene": "after shower in a soft bathrobe, bathroom mirror selfie, wet hair, covered body, tasteful cozy photo"},
    "soft_bed_blanket": {"label": "🔞 Утро под пледом", "rating": "soft18", "category": "soft18",
                         "scene": "morning in bed under a blanket, shoulders covered, soft sleepy smile, covered body, warm natural light"},
    "soft_black_dress": {"label": "🔞 Вечернее платье", "rating": "soft18", "category": "soft18",
                         "scene": "elegant black dress at night, tasteful confident pose, restaurant mirror, soft flash photo"},
    "soft_gym_top":     {"label": "🔞 Спорт-топ", "rating": "soft18", "category": "soft18",
                         "scene": "gym mirror selfie in fitted athletic top and leggings, post-workout glow, tasteful non-explicit photo"},
    "soft_rain_shirt":  {"label": "🔞 Дождь", "rating": "soft18", "category": "soft18",
                         "scene": "rainy evening photo in a slightly wet white shirt over a top, city lights, covered body, tasteful romantic mood"},

    "soft_his_hoodie":   {"label": "🔥 В твоей худи", "rating": "soft18", "category": "soft18",
                         "scene": "private home photo wearing an oversized hoodie, bare legs covered by long hoodie, cozy bed background, playful smile, non-explicit"},
    "soft_late_text":    {"label": "🔥 Позднее сообщение", "rating": "soft18", "category": "soft18",
                         "scene": "late night private phone photo in soft bedroom light, elegant pajama top, messy hair, direct eye contact, playful teasing mood, covered body"},
    "soft_dressing_room": {"label": "🔥 Примерочная", "rating": "soft18", "category": "soft18",
                         "scene": "tasteful dressing room mirror photo trying on an elegant dress, confident playful pose, covered body, non-explicit"},
    "soft_pool_evening": {"label": "🔥 Вечер у бассейна", "rating": "soft18", "category": "soft18",
                         "scene": "evening poolside photo in stylish swimsuit with light shirt, golden lights, confident smile, tasteful non-explicit"},
    "soft_candle_room":  {"label": "🔥 Свечи", "rating": "soft18", "category": "soft18",
                         "scene": "warm candlelit bedroom photo, silk pajama set, sitting on bed, soft teasing smile, covered body, tasteful"},
    "soft_after_date":   {"label": "🔥 После свидания", "rating": "soft18", "category": "soft18",
                         "scene": "private after-date mirror photo, elegant dress slightly relaxed, warm hallway light, playful smile, covered body, non-explicit"},
}

MODE_TITLES = {
    "safe": "📸 Обычные сцены",
    "romantic": "❤️ Романтика",
    "soft18": "🔥 Ближе",
    "all": "🎬 Все сцены",
}


def get_presets_for_mode(mode: str) -> dict[str, dict]:
    if mode == "all":
        return PRESETS
    if mode == "safe":
        return {k: v for k, v in PRESETS.items() if v.get("rating") == "safe"}
    if mode == "romantic":
        return {k: v for k, v in PRESETS.items() if v.get("rating") in ("romantic",)}
    if mode == "soft18":
        return {k: v for k, v in PRESETS.items() if v.get("rating") == "soft18"}
    return {k: v for k, v in PRESETS.items() if v.get("rating") == "safe"}


def rating_tail(rating: str) -> str:
    if rating == "romantic":
        return ROMANTIC_TAIL
    if rating == "soft18":
        return SOFT18_TAIL
    return QUALITY_TAIL


def build_prompt(persona_base: str, preset_key: str) -> str:
    preset = PRESETS[preset_key]
    return f"{BASE_TRIGGERS}, {persona_base}, {preset['scene']}, {rating_tail(preset.get('rating', 'safe'))}"
