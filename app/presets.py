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

    # ==================== SEX (жёсткий explicit) ====================
SEX_TAIL = (
    "explicit hardcore sex, raw penetration, visible pussy and cock, wet and glistening, "
    "detailed genitals, deep thrusting, sweaty skin, flushed face, moaning expression, "
    "ahegao elements, messy hair, intense eye contact or rolled eyes, realistic anatomy, "
    "cinematic erotic lighting, highly detailed, vulgar dirty atmosphere, raw and unfiltered"
)

PRESETS.update({
    "sex_doggy": {
        "label": "🔞 Сзади (doggy)",
        "rating": "sex",
        "scene": (
            "doggy style sex from behind, woman on all fours or bent over, ass up high, "
            "back deeply arched, man fucking her hard from behind, hands gripping her hips or waist tightly, "
            "intense deep penetration, her face in pleasure or ahegao, mouth open moaning, "
            "hair messy, sweaty skin, explicit and raw doggy style"
        )
    },
    "sex_from_behind_standing": {
        "label": "🔞 Стоя сзади",
        "rating": "sex",
        "scene": (
            "standing sex from behind, woman pressed against the wall or bent forward, "
            "man thrusting hard into her from behind, her hands flat on the wall, back arched, "
            "ass pushed back, skirt or clothes pulled down, intense penetration, "
            "gripping her hair or hips, explicit standing doggy, raw and vulgar"
        )
    },
    "sex_against_wall": {
        "label": "🔞 У стены",
        "rating": "sex",
        "scene": (
            "sex against the wall, woman with back or front against the wall, legs wrapped around him or one leg lifted, "
            "man fucking her standing up, deep penetration, hands holding her thighs or ass, "
            "intense thrusting, her head tilted back in pleasure, explicit wall sex, raw and passionate"
        )
    },
    "sex_riding": {
        "label": "🔞 Наездница",
        "rating": "sex",
        "scene": (
            "cowgirl / riding position, woman on top straddling him, riding his cock, "
            "bouncing up and down, hands on his chest or her own breasts, back arched, "
            "intense eye contact, moaning face, wet pussy visible, explicit riding sex, "
            "sweaty bodies, raw and vulgar cowgirl"
        )
    },
    "sex_missionary": {
        "label": "🔞 Миссионер",
        "rating": "sex",
        "scene": (
            "missionary sex position, woman lying on her back with legs spread wide or wrapped around him, "
            "man on top thrusting deep, intense penetration, hands holding her wrists or thighs, "
            "her back arched, moaning loudly, explicit missionary, eye contact, raw and passionate"
        )
    },
    "sex_blowjob": {
        "label": "🔞 Минет",
        "rating": "sex",
        "scene": (
            "explicit blowjob, woman on her knees or lying down, sucking cock deeply, "
            "mouth full, saliva dripping, hand stroking, looking up with submissive or aroused eyes, "
            "messy hair, wet lips, explicit oral sex, vulgar and detailed"
        )
    },
    "sex_creampie": {
        "label": "🔞 Кримпай",
        "rating": "sex",
        "scene": (
            "creampie sex, man cumming deep inside her, cum leaking out of pussy, "
            "thrusting during orgasm, her legs shaking or wrapped around him, "
            "intense pleasure expression, explicit creampie, cum dripping, raw and vulgar finish"
        )
    },
    "sex_reverse_cowgirl": {
        "label": "🔞 Наездница сзади",
        "rating": "sex",
        "scene": (
            "reverse cowgirl, woman riding on top facing away, ass towards him, "
            "bouncing on his cock, hands on his legs, back view, explicit penetration from behind while riding, "
            "sweaty skin, raw and vulgar reverse cowgirl"
        )
    },
})

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
