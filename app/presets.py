"""Scene presets with heavy 18+ and vulgar content."""

BASE_TRIGGERS = "amateurish phone photo, shot on iPhone, slightly noisy, natural skin texture, realistic"

QUALITY_TAIL = "natural skin texture, candid moment, soft daylight, depth of field, realistic everyday photo"

ROMANTIC_TAIL = (
    "intense sexual tension, heavy bedroom eyes, slightly parted wet lips, "
    "flushed skin, subtle arching back, teasing and aroused expression, "
    "cinematic erotic mood, realistic"
)

SOFT18_TAIL = (
    "extremely seductive and vulgar, highly aroused expression, heavy bedroom eyes, "
    "mouth slightly open, tongue visible, flushed face and chest, hard nipples, "
    "wet fabric clinging to pussy, hand between legs or touching herself, "
    "legs slightly spread, back arched, wet skin, erotic and dirty mood, "
    "realistic skin texture, cinematic soft lighting"
)

SEX_TAIL = (
    "explicit sex scene, raw and vulgar, heavy moaning expression, "
    "sweaty skin, hard thrusting, detailed penetration, wet pussy, "
    "creampie, messy hair, realistic anatomy, cinematic erotic lighting"
)

PRESETS: dict[str, dict] = {
    # ==================== ROMANTIC ====================
    "date_close_table": {
        "label": "🔥 Близко за столиком",
        "rating": "romantic",
        "scene": "sitting very close, intense eye contact, biting lower lip, leaning forward, hand on thigh, aroused expression"
    },
    "taxi_after_date": {
        "label": "🔥 Такси после свидания",
        "rating": "romantic",
        "scene": "back seat of taxi, skirt pulled up, sitting close, hand between legs, aroused teasing face"
    },
    "doorway_goodnight": {
        "label": "🔥 У двери",
        "rating": "romantic",
        "scene": "standing in doorway, skirt hiked up, looking back horny, hand sliding down body"
    },

    # ==================== SOFT 18+ ====================
    "soft_pajama": {
        "label": "🔞 Пижама",
        "rating": "soft18",
        "scene": "lying on bed in thin pajamas, top unbuttoned, hard nipples, hand inside panties, legs spread, aroused moaning face"
    },
    "soft_lingerie_shirt": {
        "label": "🔞 Только его рубашка",
        "rating": "soft18",
        "scene": "wearing only open white shirt, no panties, legs spread, fingers touching pussy, dirty seductive look"
    },
    "soft_beach_bikini": {
        "label": "🔞 Мокрый купальник",
        "rating": "soft18",
        "scene": "tiny wet bikini, fabric stuck to pussy, hard nipples visible, aroused expression"
    },
    "soft_late_text": {
        "label": "🔥 Позднее сообщение",
        "rating": "soft18",
        "scene": "lying on stomach in tiny panties, ass up, looking back slutty, hand pulling panties aside"
    },
    "soft_his_hoodie": {
        "label": "🔥 В его худи",
        "rating": "soft18",
        "scene": "only oversized hoodie, nothing underneath, legs wide open, pussy visible, horny expression"
    },
    "soft_mirror_selfie": {
        "label": "🔥 Зеркальное селфи",
        "rating": "soft18",
        "scene": "completely naked or tiny thong, leg up, touching or spreading pussy, dirty seductive look"
    },

    # ==================== SEX SCENES (18+) ====================
    "sex_doggy": {
        "label": "🔞 Сзади (doggy)",
        "rating": "sex",
        "scene": "doggy style, taken from behind, back arched, hard pounding, sweaty skin, moaning face"
    },
    "sex_riding": {
        "label": "🔞 Наездница",
        "rating": "sex",
        "scene": "cowgirl, riding hard, bouncing, head thrown back in pleasure, explicit penetration"
    },
    "sex_missionary": {
        "label": "🔞 Миссионер",
        "rating": "sex",
        "scene": "missionary position, legs spread wide, deep penetration, intense moaning, gripping sheets"
    },
    "sex_blowjob": {
        "label": "🔞 Минет",
        "rating": "sex",
        "scene": "on knees giving blowjob, looking up, messy, deepthroat, submissive aroused expression"
    },
    "sex_from_behind_standing": {
        "label": "🔞 Стоя сзади",
        "rating": "sex",
        "scene": "standing doggy against wall, hard fucking from behind, hair pulled, dirty expression"
    },
    "sex_creampie": {
        "label": "🔞 Кремпай",
        "rating": "sex",
        "scene": "after creampie, cum leaking out, legs spread, satisfied used expression, very explicit"
    },
    "sex_against_wall": {
        "label": "🔞 У стены",
        "rating": "sex",
        "scene": "lifted against the wall, legs wrapped, hard deep fucking, intense sex"
    },
}

MODE_TITLES = {
    "safe": "📸 Обычные сцены",
    "romantic": "❤️ Романтика",
    "soft18": "🔥 Ближе (18+)",
    "sex": "🔞 Секс",
    "all": "🎬 Все сцены",
}


def get_presets_for_mode(mode: str) -> dict[str, dict]:
    if mode == "all":
        return PRESETS
    if mode == "safe":
        return {k: v for k, v in PRESETS.items() if v.get("rating") == "safe"}
    if mode == "romantic":
        return {k: v for k, v in PRESETS.items() if v.get("rating") == "romantic"}
    if mode == "soft18":
        return {k: v for k, v in PRESETS.items() if v.get("rating") == "soft18"}
    if mode == "sex":
        return {k: v for k, v in PRESETS.items() if v.get("rating") == "sex"}
    return {k: v for k, v in PRESETS.items() if v.get("rating") == "safe"}


def rating_tail(rating: str) -> str:
    if rating == "romantic":
        return ROMANTIC_TAIL
    if rating == "soft18":
        return SOFT18_TAIL
    if rating == "sex":
        return SEX_TAIL
    return QUALITY_TAIL


def build_prompt(persona_base: str, preset_key: str) -> str:
    preset = PRESETS.get(preset_key)
    if not preset:
        return f"{BASE_TRIGGERS}, {persona_base}, {QUALITY_TAIL}"
    return f"{BASE_TRIGGERS}, {persona_base}, {preset['scene']}, {rating_tail(preset.get('rating', 'safe'))}"
