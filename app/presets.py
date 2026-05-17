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

PRESETS: dict[str, dict] = {
    # ==================== ROMANTIC ====================
    "date_close_table": {
        "label": "🔥 Близко за столиком",
        "rating": "romantic",
        "scene": "sitting very close, intense eye contact, biting lower lip, leaning forward showing deep cleavage, hand on thigh, aroused expression, warm candle light"
    },
    "taxi_after_date": {
        "label": "🔥 Такси после свидания",
        "rating": "romantic",
        "scene": "back seat of taxi at night, city lights, sitting very close or on lap, skirt pulled up, hand between her legs, aroused teasing face, messy hair"
    },
    "doorway_goodnight": {
        "label": "🔥 У двери",
        "rating": "romantic",
        "scene": "standing in doorway after date, one leg slightly lifted, skirt hiked up, looking back with horny expression, hand sliding down body"
    },
    "slow_dance_home": {
        "label": "🔥 Медленный танец дома",
        "rating": "romantic",
        "scene": "slow dancing in dim light, pressed tightly against each other, ass grinding, hand on crotch, aroused expression, heavy breathing"
    },

    # ==================== SOFT 18+ (максимально пошлые) ====================
    "soft_pajama": {
        "label": "🔞 Пижама",
        "rating": "soft18",
        "scene": "lying on bed in thin silk pajamas, top unbuttoned, hard nipples visible, hand inside panties, legs spread, aroused moaning face, messy hair"
    },
    "soft_lingerie_shirt": {
        "label": "🔞 Только его рубашка",
        "rating": "soft18",
        "scene": "wearing only oversized open white shirt, no panties, sitting on bed with legs spread, fingers touching pussy, dirty seductive look"
    },
    "soft_beach_bikini": {
        "label": "🔞 Мокрый купальник",
        "rating": "soft18",
        "scene": "on beach in tiny wet bikini, fabric stuck to pussy and nipples, hard nipples and camel toe visible, aroused expression, water on body"
    },
    "soft_bathrobe": {
        "label": "🔞 После душа",
        "rating": "soft18",
        "scene": "standing in front of mirror with open bathrobe, completely naked, wet skin, hard nipples, hand between legs, aroused face, steam"
    },
    "soft_bed_blanket": {
        "label": "🔞 Утро под одеялом",
        "rating": "soft18",
        "scene": "lying in bed, thin blanket slipping off, completely naked, legs spread, touching herself, sleepy horny expression"
    },
    "soft_late_text": {
        "label": "🔥 Позднее сообщение",
        "rating": "soft18",
        "scene": "late night photo, lying on stomach in tiny panties only, ass up, looking back with slutty expression, hand pulling panties aside"
    },
    "soft_his_hoodie": {
        "label": "🔥 В его худи",
        "rating": "soft18",
        "scene": "wearing only oversized hoodie, nothing underneath, legs wide open, hoodie lifted, pussy visible, horny teasing expression"
    },
    "soft_dressing_room": {
        "label": "🔥 Примерочная",
        "rating": "soft18",
        "scene": "in dressing room, mirror selfie, pulling panties aside, fingers on clit, aroused expression, biting lip"
    },
    "soft_after_date": {
        "label": "🔥 После свидания",
        "rating": "soft18",
        "scene": "just came home after date, dress pulled down, bra off, sitting on bed touching herself, messy hair, satisfied horny face"
    },
    "soft_rain_shirt": {
        "label": "🔥 Мокрая рубашка",
        "rating": "soft18",
        "scene": "standing in rain in wet white shirt with no bra, completely see-through, hard nipples, hand between legs, aroused face"
    },
    "soft_mirror_selfie": {
        "label": "🔥 Зеркальное селфи",
        "rating": "soft18",
        "scene": "mirror selfie completely naked or in tiny thong, one leg up, spreading or touching pussy from behind, dirty look"
    },
}

MODE_TITLES = {
    "safe": "📸 Обычные сцены",
    "romantic": "❤️ Романтика",
    "soft18": "🔥 Ближе (18+)",
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
    return {k: v for k, v in PRESETS.items() if v.get("rating") == "safe"}


def rating_tail(rating: str) -> str:
    if rating == "romantic":
        return ROMANTIC_TAIL
    if rating == "soft18":
        return SOFT18_TAIL
    return QUALITY_TAIL


def build_prompt(persona_base: str, preset_key: str) -> str:
    preset = PRESETS.get(preset_key)
    if not preset:
        return f"{BASE_TRIGGERS}, {persona_base}, {QUALITY_TAIL}"
    return f"{BASE_TRIGGERS}, {persona_base}, {preset['scene']}, {rating_tail(preset.get('rating', 'safe'))}"
