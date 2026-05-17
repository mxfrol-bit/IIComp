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
    "explicit sex scene, raw and vulgar, heavy moaning expression, ahegao elements, "
    "sweaty skin, messy hair, hard fucking, detailed penetration, wet pussy, "
    "creampie, cum on body, rough sex, dominant pose, realistic anatomy, "
    "cinematic erotic lighting, very explicit and dirty"
)

PRESETS: dict[str, dict] = {
    # ==================== ROMANTIC ====================
    "date_close_table": {
        "label": "🔥 Близко за столиком",
        "rating": "romantic",
        "scene": "sitting very close, intense eye contact, biting lower lip, leaning forward showing deep cleavage, hand on thigh, aroused expression"
    },
    "taxi_after_date": {
        "label": "🔥 Такси после свидания",
        "rating": "romantic",
        "scene": "back seat of taxi, skirt pulled up, sitting on his lap, hand between legs, aroused teasing face"
    },
    "doorway_goodnight": {
        "label": "🔥 У двери",
        "rating": "romantic",
        "scene": "in doorway, skirt hiked up, looking back horny, hand sliding down body"
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
        "scene": "tiny wet bikini, fabric stuck to pussy, hard nipples, camel toe, aroused expression"
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
        "scene": "completely naked or tiny thong, leg up, spreading ass or touching pussy from behind, dirty look"
    },

    # ==================== SEX SCENES (18+) ====================
    "sex_doggy": {
        "label": "🔞 Сзади (doggy)",
        "rating": "sex",
        "scene": "doggy style sex, taken from behind, back arched, ass up, hard pounding, sweaty skin, moaning face, hair pulled, very explicit"
    },
    "sex_riding": {
        "label": "🔞 Наездница (riding)",
        "rating": "sex",
        "scene": "cowgirl position, riding hard, bouncing breasts, hands on his chest, head thrown back in pleasure, explicit penetration"
    },
    "sex_missionary": {
        "label": "🔞 Миссионер",
        "rating": "sex",
        "scene": "missionary sex, legs spread wide, deep penetration, intense eye contact, moaning, hands gripping sheets, sweaty bodies"
    },
    "sex_blowjob": {
        "label": "🔞 Минет",
        "rating": "sex",
        "scene": "on knees giving blowjob, looking up with teary eyes, messy saliva, deepthroat, aroused submissive expression"
    },
    "sex_from_behind_standing": {
        "label": "🔞 Стоя сзади",
        "rating": "sex",
        "scene": "standing doggy against wall or table, skirt lifted, hard fucking from behind, hand on throat or hair, dirty expression"
    },
    "sex_creampie": {
        "label": "🔞 Кремпай",
        "rating": "sex",
        "scene": "after creampie, cum leaking out of pussy, legs spread, satisfied and used expression, messy and vulgar"
    },
    "sex_against_wall": {
        "label": "🔞 У стены",
        "rating": "sex",
        "scene": "lifted against the wall, legs wrapped around, hard deep fucking, intense kissing and moaning, very explicit"
    },
    "sex_prone_bone": {
        "label": "🔞 Prone bone",
        "rating": "sex",
        "scene": "lying flat on stomach, fucked from behind, ass squeezed, deep penetration, moaning into pillow, raw and vulgar"
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
        return {k: v for k, v in PRESETS.items() if v.get("rating
