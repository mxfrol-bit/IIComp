"""Catalogs for AI Content Factory: model options, product categories,
photo scenarios and video scenarios.

Keys are intentionally short because Telegram callback_data is limited to 64 bytes.
"""

AGE_RANGES = {
    "20_24": "20–24",
    "25_29": "25–29",
    "30_34": "30–34",
    "35_40": "35–40",
}

HAIR_COLORS = {
    "brunette": "Брюнетка",
    "brown": "Шатенка",
    "blonde": "Блондинка",
    "dark": "Тёмные волосы",
    "ginger": "Рыжие",
    "black": "Чёрные волосы",
}

HAIR_LENGTHS = {
    "short": "Короткие",
    "medium": "Средние",
    "long": "Длинные",
    "wavy": "Длинные волнистые",
}

APPEARANCE_TYPES = {
    "slavic": "Европейская / славянская",
    "mediterranean": "Средиземноморская",
    "asian": "Азиатская",
    "latina": "Латиноамериканская",
    "mixed": "Смешанный типаж",
    "nordic": "Северный типаж",
}

MODEL_STYLES = {
    "lifestyle": "Lifestyle",
    "fashion": "Fashion",
    "beauty": "Beauty",
    "luxury": "Luxury",
    "sport": "Fitness / sport",
    "business": "Business",
    "street": "Streetwear",
    "elegant": "Elegant",
}

NICHES = {
    "fashion": "Fashion",
    "beauty": "Beauty / skincare",
    "lifestyle": "Lifestyle influencer",
    "fitness": "Fitness / wellness",
    "travel": "Travel / hotel",
    "luxury": "Luxury / premium",
    "food": "Food / drinks",
    "business": "Business / expert",
}

PRODUCT_CATEGORIES = {
    "drink": "Напиток / бутылка",
    "food": "Еда / шоколад / снэк",
    "cosmetic": "Косметика / уход",
    "perfume": "Парфюм",
    "clothes": "Одежда / платье",
    "jewelry": "Украшения",
    "accessory": "Аксессуар / сумка / очки",
    "gadget": "Гаджет",
    "home": "Интерьер / декор",
    "other": "Другое",
}

PHOTO_SCENARIOS = {
    "ig": {
        "title": "Instagram / lifestyle",
        "items": {
            "ig_cafe": ("Кафе у окна", "lifestyle Instagram photo in a cozy cafe by the window, natural daylight, casual premium look, authentic influencer content", "4:5"),
            "ig_morning": ("Утро с кофе", "morning lifestyle photo, model holding coffee, cozy kitchen, soft window light, natural phone photo", "4:5"),
            "ig_city": ("Прогулка по городу", "city walk lifestyle shot, urban street, natural movement, candid Instagram content", "4:5"),
            "ig_balcony": ("Балкон / терраса", "model on a balcony or terrace, relaxed lifestyle mood, soft daylight, premium casual aesthetic", "4:5"),
            "ig_car": ("В машине", "casual influencer photo inside a car, soft natural light, realistic phone camera", "9:16"),
            "ig_mirror": ("Mirror shot", "mirror selfie, stylish outfit, clean apartment interior, authentic Instagram story look", "9:16"),
            "ig_book": ("С книгой", "model sitting with a book, calm intellectual lifestyle mood, warm interior", "4:5"),
            "ig_rooftop": ("Rooftop", "rooftop lifestyle photo, city skyline, golden hour, premium influencer vibe", "4:5"),
        },
    },
    "fashion": {
        "title": "Fashion",
        "items": {
            "fa_studio": ("Студийный full body", "full body fashion studio shot, clean background, editorial pose, professional lookbook photography", "4:5"),
            "fa_walk": ("Walking shot", "fashion walking shot, model walking toward camera, natural movement, street style campaign", "9:16"),
            "fa_fitroom": ("Примерочная", "fitting room fashion mirror photo, outfit check, premium boutique lighting", "9:16"),
            "fa_corridor": ("Luxury corridor", "luxury hotel corridor fashion shot, elegant pose, cinematic lighting", "4:5"),
            "fa_seated": ("Sitting pose", "fashion editorial sitting pose, outfit details visible, high-end magazine style", "4:5"),
            "fa_detail": ("Детали образа", "close shot of outfit details, fabric texture, accessories, editorial fashion crop", "1:1"),
            "fa_runway": ("Runway vibe", "runway inspired fashion campaign, confident model pose, dramatic but clean lighting", "9:16"),
            "fa_street": ("Streetwear", "streetwear fashion content, urban background, candid style, natural camera", "4:5"),
        },
    },
    "beauty": {
        "title": "Beauty / skincare",
        "items": {
            "be_close": ("Beauty close-up", "beauty close-up portrait, glowing skin, clean makeup, soft commercial lighting", "4:5"),
            "be_skin": ("Skincare routine", "skincare routine photo, model applying cream, clean bathroom aesthetic, natural beauty ad", "9:16"),
            "be_perfume": ("Perfume ad", "perfume advertising photo, model holding perfume bottle near face, elegant luxury mood", "4:5"),
            "be_lip": ("Lipstick close-up", "lipstick beauty close-up, model applying lipstick, glossy editorial look", "4:5"),
            "be_vanity": ("Vanity table", "beauty vanity table scene, mirror lights, skincare products, elegant feminine mood", "4:5"),
            "be_spa": ("Spa mood", "spa wellness beauty content, robe, towel, calm luxury atmosphere, tasteful", "4:5"),
            "be_hair": ("Haircare", "haircare commercial photo, shiny hair movement, soft light, beauty influencer style", "4:5"),
        },
    },
    "product": {
        "title": "Product placement / ads",
        "items": {
            "pr_hand": ("Товар в руке", "native product placement, model holding the product naturally in hand, label visible, lifestyle advertising photo", "4:5"),
            "pr_table": ("Товар на столе", "product placed on a table near the model, cafe lifestyle composition, elegant native ad", "4:5"),
            "pr_reveal": ("Product reveal", "model revealing the product to camera, clean ad composition, premium UGC look", "9:16"),
            "pr_unbox": ("Unboxing", "unboxing style product photo, model opening packaging, authentic UGC content", "9:16"),
            "pr_use": ("Использует продукт", "model naturally using the product, clear product focus, realistic influencer ad", "9:16"),
            "pr_hero": ("Hero ad", "premium hero advertising composition, model and product both visible, clean brand campaign style", "4:5"),
            "pr_pack": ("Упаковка крупно", "close-up of product packaging with model in background, shallow depth of field, premium ad", "1:1"),
            "pr_story": ("Story UGC", "vertical Instagram story UGC frame, model talking to camera and showing product", "9:16"),
        },
    },
    "food": {
        "title": "Food / drinks",
        "items": {
            "fo_sip": ("Пробует напиток", "model tasting or sipping the drink, bottle visible, authentic lifestyle ad", "9:16"),
            "fo_choco": ("Шоколад / снэк", "model holding chocolate or snack, cozy lifestyle scene, appetizing native content", "4:5"),
            "fo_breakfast": ("Завтрак", "breakfast table lifestyle content with product, warm morning light, influencer style", "4:5"),
            "fo_picnic": ("Пикник", "picnic scene with product, natural outdoor light, relaxed lifestyle ad", "4:5"),
            "fo_rest": ("Ресторан", "restaurant table scene, model with food or drink product, premium social content", "4:5"),
        },
    },
    "travel": {
        "title": "Travel / hotel",
        "items": {
            "tr_lobby": ("Hotel lobby", "hotel lobby lifestyle photo, model with product or outfit, premium travel influencer vibe", "4:5"),
            "tr_pool": ("Poolside", "poolside lifestyle content, elegant resort look, product naturally included, tasteful", "9:16"),
            "tr_beach": ("Beach club", "beach club lifestyle ad, golden hour, relaxed premium travel aesthetic", "4:5"),
            "tr_airport": ("Airport vibe", "airport travel influencer shot, suitcase, product placement, clean modern look", "9:16"),
            "tr_sunset": ("Sunset terrace", "sunset terrace travel content, cinematic warm light, model and product composition", "4:5"),
        },
    },
}

VIDEO_SCENARIOS = {
    "ugc": {
        "title": "UGC / Reels",
        "items": {
            "v_ugc_talk": ("говорит в камеру", "natural UGC video, model talks to camera, friendly expression, handheld phone style"),
            "v_ugc_reveal": ("показывает товар", "model reveals product to camera, small hand movement, label visible, authentic UGC"),
            "v_ugc_unbox": ("unboxing", "unboxing motion, opening package, showing product, vertical social video"),
            "v_ugc_try": ("пробует / тестирует", "model tries the product naturally, smiles, simple influencer review vibe"),
            "v_ugc_story": ("сторис-кадр", "Instagram story style, slight phone camera movement, model gestures naturally"),
            "v_ugc_before": ("до/после намёк", "before and after style product demonstration, natural transition motion"),
        },
    },
    "fashion": {
        "title": "Fashion",
        "items": {
            "v_fa_walk": ("идёт на камеру", "fashion walk toward camera, outfit visible, smooth natural movement"),
            "v_fa_turn": ("поворот к камере", "model turns to camera, hair movement, confident fashion reel"),
            "v_fa_spin": ("outfit spin", "slow outfit spin, showing dress or clothes, clean fashion content"),
            "v_fa_detail": ("детали образа", "slow camera move over outfit details, fabric, accessories, editorial style"),
            "v_fa_mirror": ("mirror outfit check", "mirror video, model adjusts outfit, realistic phone reel"),
            "v_fa_corr": ("luxury walk", "model walking through luxury corridor, cinematic fashion movement"),
        },
    },
    "beauty": {
        "title": "Beauty",
        "items": {
            "v_be_apply": ("наносит продукт", "beauty routine video, model applying skincare product, soft hand movement"),
            "v_be_perf": ("парфюм", "model sprays perfume softly, elegant close-up, luxury beauty ad"),
            "v_be_close": ("beauty close-up", "subtle close-up beauty video, blinking, soft smile, glowing skin"),
            "v_be_hair": ("волосы", "hair movement, model touches hair, beauty commercial style"),
            "v_be_vanity": ("vanity routine", "model at vanity mirror, applying makeup, premium beauty content"),
            "v_be_spa": ("spa mood", "calm spa motion, robe, soft breathing, premium wellness ad"),
        },
    },
    "product": {
        "title": "Product Ads",
        "items": {
            "v_pr_hand": ("товар в руке", "model holds product in hand, slight rotation to show label, product ad"),
            "v_pr_table": ("берёт со стола", "model picks product from table, smooth hand movement, lifestyle ad"),
            "v_pr_pack": ("показывает упаковку", "close product packaging reveal, label facing camera, premium ad motion"),
            "v_pr_hero": ("hero reveal", "cinematic product reveal, slow zoom, model and product in premium composition"),
            "v_pr_use": ("использует товар", "model uses the product naturally, clear product focus, influencer ad"),
            "v_pr_label": ("лейбл крупно", "camera gently pushes toward product label, model softly in background"),
        },
    },
    "cinema": {
        "title": "Cinematic",
        "items": {
            "v_ci_zoom": ("slow zoom", "slow cinematic zoom in, subtle facial movement, premium commercial mood"),
            "v_ci_pan": ("pan camera", "gentle camera pan, realistic depth, fashion advertising mood"),
            "v_ci_light": ("движение света", "soft moving light, cinematic shadows, premium ad feeling"),
            "v_ci_wind": ("ветер / волосы", "subtle wind, hair movement, model looks at camera, cinematic realism"),
            "v_ci_reveal": ("dramatic reveal", "cinematic reveal movement, model turns slightly, product or outfit focus"),
        },
    },
}

VIDEO_FORMATS = {
    "916": ("9:16 Reels", "9:16"),
    "45": ("4:5 Instagram", "4:5"),
    "11": ("1:1 квадрат", "1:1"),
}

VIDEO_DURATIONS = {
    "5": "5 сек",
    "10": "10 сек",
    "15": "15 сек",
}


def get_photo_scenario(key: str):
    for cat in PHOTO_SCENARIOS.values():
        if key in cat["items"]:
            label, prompt, aspect = cat["items"][key]
            return {"label": label, "prompt": prompt, "aspect": aspect}
    return None


def get_video_scenario(key: str):
    for cat in VIDEO_SCENARIOS.values():
        if key in cat["items"]:
            label, prompt = cat["items"][key]
            return {"label": label, "prompt": prompt}
    return None
