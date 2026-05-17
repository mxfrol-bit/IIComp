"""Русские каталоги для AI Content Factory.

UI полностью на русском. Prompt-часть внутри сценариев оставлена на английском,
потому что fal/Flux/FASHN/Kling лучше держат качество и композицию на английских промптах.
"""

AGE_RANGES = {
    "18_22": "18–22",
    "23_26": "23–26",
    "27_30": "27–30",
    "31_35": "31–35",
    "36_40": "36–40",
}

HAIR_COLORS = {
    "brunette": "Брюнетка",
    "brown": "Шатенка",
    "blonde": "Блондинка",
    "dark": "Тёмные волосы",
    "ginger": "Рыжие",
    "black": "Чёрные волосы",
    "lightbrown": "Русые волосы",
    "platinum": "Платиновый блонд",
}

HAIR_LENGTHS = {
    "pixie": "Очень короткие",
    "short": "Короткие",
    "medium": "Средние",
    "long": "Длинные",
    "wavy": "Длинные волнистые",
    "curly": "Кудрявые",
}

APPEARANCE_TYPES = {
    "slavic": "Европейская / славянская",
    "nordic": "Северный типаж",
    "mediterranean": "Средиземноморская",
    "asian": "Азиатская",
    "latina": "Латиноамериканская",
    "mixed": "Смешанный типаж",
    "middle": "Восточный типаж",
    "afro": "Афро / тёмная кожа",
}

MODEL_STYLES = {
    "lifestyle": "Лайфстайл",
    "fashion": "Фэшн",
    "beauty": "Бьюти",
    "luxury": "Люкс / премиум",
    "sport": "Фитнес / wellness",
    "business": "Бизнес / эксперт",
    "street": "Стритстайл",
    "elegant": "Элегантная",
    "ugc": "UGC / блогер",
    "editorial": "Журнальная съёмка",
}

NICHES = {
    "fashion": "Одежда / fashion",
    "beauty": "Бьюти / уход",
    "lifestyle": "Лайфстайл-инфлюенсер",
    "fitness": "Фитнес / wellness",
    "travel": "Путешествия / отели",
    "luxury": "Люкс / премиум",
    "food": "Еда / напитки",
    "business": "Бизнес / эксперт",
    "ecom": "E-commerce / маркетплейсы",
    "ugc": "UGC-реклама",
}

PRODUCT_CATEGORIES = {
    "drink": "Напиток / бутылка",
    "food": "Еда / шоколад / снэк",
    "cosmetic": "Косметика / уход",
    "perfume": "Парфюм",
    "clothes": "Одежда / платье",
    "shoes": "Обувь",
    "jewelry": "Украшения",
    "accessory": "Аксессуар / сумка / очки",
    "gadget": "Гаджет / электроника",
    "home": "Интерьер / декор",
    "kids": "Детские товары",
    "pet": "Товары для животных",
    "other": "Другое",
}

# item tuple: (button_label_ru, prompt_en, aspect_ratio)
PHOTO_SCENARIOS = {
    "ig": {
        "title": "📱 Instagram / лайфстайл",
        "items": {
            "ig_cafe": ("Кафе у окна", "lifestyle Instagram photo in a cozy cafe by the window, natural daylight, casual premium look, authentic influencer content", "4:5"),
            "ig_morning": ("Утро с кофе", "morning lifestyle photo, model holding coffee, cozy kitchen, soft window light, natural phone photo", "4:5"),
            "ig_city": ("Прогулка по городу", "city walk lifestyle shot, urban street, natural movement, candid Instagram content", "4:5"),
            "ig_balcony": ("Балкон / терраса", "model on a balcony or terrace, relaxed lifestyle mood, soft daylight, premium casual aesthetic", "4:5"),
            "ig_car": ("В машине", "casual influencer photo inside a car, soft natural light, realistic phone camera", "9:16"),
            "ig_mirror": ("Зеркальное селфи", "mirror selfie, stylish outfit, clean apartment interior, authentic Instagram story look", "9:16"),
            "ig_book": ("С книгой", "model sitting with a book, calm intellectual lifestyle mood, warm interior", "4:5"),
            "ig_rooftop": ("Крыша / rooftop", "rooftop lifestyle photo, city skyline, golden hour, premium influencer vibe", "4:5"),
            "ig_home": ("Домашний кадр", "cozy apartment lifestyle photo, natural relaxed pose, soft daylight, influencer home content", "4:5"),
            "ig_phone": ("С телефоном", "model holding smartphone, casual social media vibe, realistic phone photography", "4:5"),
            "ig_evening": ("Вечерний город", "evening city lights, realistic influencer lifestyle photo, cinematic but natural", "4:5"),
            "ig_elevator": ("Лифт / подъезд", "premium elevator mirror shot, outfit check, authentic urban content", "9:16"),
        },
    },
    "fashion": {
        "title": "👗 Одежда / fashion",
        "items": {
            "fa_studio": ("Студия full body", "full body fashion studio shot, clean background, editorial pose, professional lookbook photography", "4:5"),
            "fa_walk": ("Идёт на камеру", "fashion walking shot, model walking toward camera, natural movement, street style campaign", "9:16"),
            "fa_fitroom": ("Примерочная", "fitting room fashion mirror photo, outfit check, premium boutique lighting", "9:16"),
            "fa_corridor": ("Люксовый коридор", "luxury hotel corridor fashion shot, elegant pose, cinematic lighting", "4:5"),
            "fa_seated": ("Сидячая поза", "fashion editorial sitting pose, outfit details visible, high-end magazine style", "4:5"),
            "fa_detail": ("Детали образа", "close shot of outfit details, fabric texture, accessories, editorial fashion crop", "1:1"),
            "fa_runway": ("Подиумный вайб", "runway inspired fashion campaign, confident model pose, dramatic but clean lighting", "9:16"),
            "fa_street": ("Стритстайл", "streetwear fashion content, urban background, candid style, natural camera", "4:5"),
            "fa_white": ("Белая циклорама", "full body lookbook shot on white cyclorama, catalog quality, clean studio light", "4:5"),
            "fa_editorial": ("Журнальный разворот", "high fashion editorial campaign, magazine cover composition, premium styling", "4:5"),
            "fa_outdoor": ("На улице в образе", "outdoor fashion campaign, natural walking pose, city background, outfit visible", "9:16"),
            "fa_lux": ("Luxury campaign", "luxury fashion campaign, premium interior, elegant confident pose", "4:5"),
        },
    },
    "beauty": {
        "title": "💄 Бьюти / уход",
        "items": {
            "be_close": ("Крупный бьюти-портрет", "beauty close-up portrait, glowing skin, clean makeup, soft commercial lighting", "4:5"),
            "be_skin": ("Уход за кожей", "skincare routine photo, model applying cream, clean bathroom aesthetic, natural beauty ad", "9:16"),
            "be_perfume": ("Парфюм", "perfume advertising photo, model holding perfume bottle near face, elegant luxury mood", "4:5"),
            "be_lip": ("Помада крупно", "lipstick beauty close-up, model applying lipstick, glossy editorial look", "4:5"),
            "be_vanity": ("У туалетного столика", "beauty vanity table scene, mirror lights, skincare products, elegant feminine mood", "4:5"),
            "be_spa": ("Spa / wellness", "spa wellness beauty content, robe, towel, calm luxury atmosphere, tasteful", "4:5"),
            "be_hair": ("Волосы / haircare", "haircare commercial photo, shiny hair movement, soft light, beauty influencer style", "4:5"),
            "be_bath": ("Ванная aesthetic", "clean bathroom beauty content, product near sink, model natural skincare routine", "9:16"),
            "be_glow": ("Glow skin", "glowing skin beauty ad, dewy makeup, premium softbox light, realistic texture", "4:5"),
            "be_mask": ("Маска для лица", "model with skincare face mask, clean beauty routine content, premium bathroom scene", "4:5"),
        },
    },
    "product": {
        "title": "📦 Товар / реклама",
        "items": {
            "pr_hand": ("Товар в руке", "native product placement, model holding the product naturally in hand, label visible, lifestyle advertising photo", "4:5"),
            "pr_table": ("Товар на столе", "product placed on a table near the model, cafe lifestyle composition, elegant native ad", "4:5"),
            "pr_reveal": ("Показывает товар", "model revealing the product to camera, clean ad composition, premium UGC look", "9:16"),
            "pr_unbox": ("Распаковка", "unboxing style product photo, model opening packaging, authentic UGC content", "9:16"),
            "pr_use": ("Использует товар", "model naturally using the product, clear product focus, realistic influencer ad", "9:16"),
            "pr_hero": ("Hero ad", "premium hero advertising composition, model and product both visible, clean brand campaign style", "4:5"),
            "pr_pack": ("Упаковка крупно", "close-up of product packaging with model in background, shallow depth of field, premium ad", "1:1"),
            "pr_story": ("UGC stories", "vertical Instagram story UGC frame, model talking to camera and showing product", "9:16"),
            "pr_flat": ("Flat lay + модель", "flat lay product composition with model hands visible, premium social ad", "1:1"),
            "pr_macro": ("Макро-деталь", "macro detail of product texture and packaging, model softly blurred in background", "1:1"),
            "pr_shelf": ("На полке / витрина", "product on premium shelf with model nearby, elegant retail display advertising", "4:5"),
            "pr_before": ("До/после подача", "before and after ad concept, product visible, clean premium comparison style", "4:5"),
        },
    },
    "food": {
        "title": "🍫 Еда / напитки",
        "items": {
            "fo_sip": ("Пробует напиток", "model tasting or sipping the drink, bottle visible, authentic lifestyle ad", "9:16"),
            "fo_choco": ("Шоколад / снэк", "model holding chocolate or snack, cozy lifestyle scene, appetizing native content", "4:5"),
            "fo_breakfast": ("Завтрак", "breakfast table lifestyle content with product, warm morning light, influencer style", "4:5"),
            "fo_picnic": ("Пикник", "picnic scene with product, natural outdoor light, relaxed lifestyle ad", "4:5"),
            "fo_rest": ("Ресторан", "restaurant table scene, model with food or drink product, premium social content", "4:5"),
            "fo_gym": ("После тренировки", "post workout snack or drink content, fitness lifestyle, product clearly visible", "9:16"),
            "fo_kitchen": ("На кухне", "kitchen lifestyle food ad, model preparing or showing product, natural home content", "4:5"),
            "fo_close": ("Аппетитный крупный кадр", "appetizing close-up product food shot, model hand interaction, premium ad", "1:1"),
        },
    },
    "travel": {
        "title": "🌍 Travel / отели",
        "items": {
            "tr_lobby": ("Лобби отеля", "hotel lobby lifestyle photo, model with product or outfit, premium travel influencer vibe", "4:5"),
            "tr_pool": ("У бассейна", "poolside lifestyle content, elegant resort look, product naturally included, tasteful", "9:16"),
            "tr_beach": ("Beach club", "beach club lifestyle ad, golden hour, relaxed premium travel aesthetic", "4:5"),
            "tr_airport": ("Аэропорт", "airport travel influencer shot, suitcase, product placement, clean modern look", "9:16"),
            "tr_sunset": ("Терраса на закате", "sunset terrace travel content, cinematic warm light, model and product composition", "4:5"),
            "tr_room": ("Номер отеля", "hotel room lifestyle shot, premium bed, product or outfit naturally included", "4:5"),
            "tr_breakfast": ("Завтрак в отеле", "hotel breakfast lifestyle content, elegant product placement, premium travel vibe", "4:5"),
        },
    },
    "market": {
        "title": "🛒 Маркетплейсы / карточки",
        "items": {
            "mk_white": ("Белый фон + модель", "clean e-commerce product with model on white background, marketplace main image style", "4:5"),
            "mk_inf": ("Инфографика без текста", "e-commerce visual, product and model composition, clean empty areas for later text overlay", "1:1"),
            "mk_set": ("Комплект / набор", "product bundle composition with model, clean marketplace catalog style", "1:1"),
            "mk_use": ("Сценарий использования", "marketplace lifestyle usage scene, model demonstrates the product, product clearly visible", "4:5"),
            "mk_compare": ("Премиум-выкладка", "premium product layout with model, clean catalog campaign style", "1:1"),
        },
    },
}

# item tuple: (button_label_ru, prompt_en)
VIDEO_SCENARIOS = {
    "ugc": {
        "title": "📱 UGC / Reels",
        "items": {
            "v_ugc_talk": ("говорит в камеру", "natural UGC video, model talks to camera, friendly expression, handheld phone style"),
            "v_ugc_reveal": ("показывает товар", "model reveals product to camera, small hand movement, label visible, authentic UGC"),
            "v_ugc_unbox": ("распаковка", "unboxing motion, opening package, showing product, vertical social video"),
            "v_ugc_try": ("пробует / тестирует", "model tries the product naturally, smiles, simple influencer review vibe"),
            "v_ugc_story": ("сторис-кадр", "Instagram story style, slight phone camera movement, model gestures naturally"),
            "v_ugc_before": ("до/после намёк", "before and after style product demonstration, natural transition motion"),
            "v_ugc_close": ("подносит к камере", "model brings product closer to camera, smooth natural hand motion, label focus"),
            "v_ugc_table": ("берёт со стола", "model picks up product from table and smiles, natural UGC review motion"),
        },
    },
    "fashion": {
        "title": "👗 Fashion-видео",
        "items": {
            "v_fa_walk": ("идёт на камеру", "fashion walk toward camera, outfit visible, smooth natural movement"),
            "v_fa_turn": ("поворот к камере", "model turns to camera, hair movement, confident fashion reel"),
            "v_fa_spin": ("поворот в образе", "slow outfit spin, showing dress or clothes, clean fashion content"),
            "v_fa_detail": ("детали образа", "slow camera move over outfit details, fabric, accessories, editorial style"),
            "v_fa_mirror": ("зеркальный outfit check", "mirror video, model adjusts outfit, realistic phone reel"),
            "v_fa_corr": ("luxury walk", "model walking through luxury corridor, cinematic fashion movement"),
            "v_fa_seat": ("садится / позирует", "model sits down naturally, fashion editorial movement, outfit visible"),
        },
    },
    "beauty": {
        "title": "💄 Бьюти-видео",
        "items": {
            "v_be_apply": ("наносит продукт", "beauty routine video, model applying skincare product, soft hand movement"),
            "v_be_perf": ("парфюм", "model sprays perfume softly, elegant close-up, luxury beauty ad"),
            "v_be_close": ("крупный портрет", "subtle close-up beauty video, blinking, soft smile, glowing skin"),
            "v_be_hair": ("движение волос", "hair movement, model touches hair, beauty commercial style"),
            "v_be_vanity": ("у зеркала", "model at vanity mirror, applying makeup, premium beauty content"),
            "v_be_spa": ("spa mood", "calm spa motion, robe, soft breathing, premium wellness ad"),
            "v_be_label": ("лейбл к камере", "beauty product label moves toward camera, model softly smiles in background"),
        },
    },
    "product": {
        "title": "📦 Товарное видео",
        "items": {
            "v_pr_hand": ("товар в руке", "model holds product in hand, slight rotation to show label, product ad"),
            "v_pr_table": ("берёт со стола", "model picks product from table, smooth hand movement, lifestyle ad"),
            "v_pr_pack": ("показывает упаковку", "close product packaging reveal, label facing camera, premium ad motion"),
            "v_pr_hero": ("hero reveal", "cinematic product reveal, slow zoom, model and product in premium composition"),
            "v_pr_use": ("использует товар", "model uses the product naturally, clear product focus, influencer ad"),
            "v_pr_label": ("лейбл крупно", "camera gently pushes toward product label, model softly in background"),
            "v_pr_shelf": ("витрина / shelf", "product on shelf, model reaches for it, premium retail ad motion"),
            "v_pr_macro": ("макро-движение", "macro product camera move, packaging detail, premium lighting"),
        },
    },
    "cinema": {
        "title": "🎬 Кино / премиум",
        "items": {
            "v_ci_zoom": ("slow zoom", "slow cinematic zoom in, subtle facial movement, premium commercial mood"),
            "v_ci_pan": ("панорама камеры", "gentle camera pan, realistic depth, fashion advertising mood"),
            "v_ci_light": ("движение света", "soft moving light, cinematic shadows, premium ad feeling"),
            "v_ci_wind": ("ветер / волосы", "subtle wind, hair movement, model looks at camera, cinematic realism"),
            "v_ci_reveal": ("dramatic reveal", "cinematic reveal movement, model turns slightly, product or outfit focus"),
            "v_ci_lens": ("рекламный объектив", "commercial lens movement, premium depth of field, smooth parallax"),
        },
    },
}

VIDEO_FORMATS = {
    "916": ("9:16 Reels / Stories", "9:16"),
    "45": ("4:5 Instagram post", "4:5"),
    "11": ("1:1 квадрат", "1:1"),
}

VIDEO_DURATIONS = {
    "5": "5 секунд",
    "10": "10 секунд",
    "15": "15 секунд",
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
