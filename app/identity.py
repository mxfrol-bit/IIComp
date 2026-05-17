"""Identity helpers for AI Content Factory.

Goal: make every AI model visually different and more stable.
Seed alone is not enough, so each model gets a 'visual DNA' text anchor.
The DNA is stored inside persona_json and reused in every prompt.
"""
from __future__ import annotations

import random

FACE_SHAPES = [
    "овальное лицо с мягкой линией подбородка",
    "сердцевидное лицо с аккуратным подбородком",
    "узкое лицо с высокими скулами",
    "круглое лицо с мягкими щеками",
    "скульптурное лицо с выраженными скулами",
    "прямоугольное лицо с модельной линией челюсти",
]

EYES = [
    "светло-карие миндалевидные глаза",
    "зелёные глаза с немного приподнятыми внешними уголками",
    "серо-голубые глаза среднего размера",
    "тёмно-карие большие глаза",
    "янтарные глаза с мягким взглядом",
    "серые глаза с спокойным уверенным взглядом",
]

NOSES = [
    "ровный небольшой нос",
    "тонкий прямой нос",
    "мягкий округлый нос",
    "слегка вздёрнутый аккуратный нос",
    "длинный элегантный нос",
    "короткий модельный нос с мягкой переносицей",
]

LIPS = [
    "средние губы с чёткой верхней линией",
    "полные мягкие губы",
    "тонкие аккуратные губы",
    "выразительные губы с лёгкой асимметрией",
    "натуральные губы с мягким контуром",
]

SKIN = [
    "светлая кожа с натуральной текстурой",
    "оливковый подтон кожи",
    "фарфоровая кожа без пластика",
    "тёплый бежевый подтон кожи",
    "слегка загорелая кожа",
    "светлая кожа с едва заметными веснушками",
]

FEATURES = [
    "маленькая родинка у скулы",
    "лёгкие веснушки на носу",
    "очень ровные брови средней толщины",
    "выраженные густые брови",
    "мягкие ямочки при улыбке",
    "чистое лицо без заметных особых отметок",
    "небольшая родинка над губой",
]

CAMERA_SIGNATURES = [
    "объектив 50 мм, мягкая глубина резкости",
    "натуральная iPhone-съёмка, лёгкая перспектива телефона",
    "коммерческий портрет, мягкий fashion light",
    "журнальная съёмка, чистый премиальный свет",
]


def make_identity_dna(name: str, seed: int | None = None) -> dict:
    rng = random.Random(seed or random.randint(1, 2_000_000_000))
    data = {
        "face_shape": rng.choice(FACE_SHAPES),
        "eyes": rng.choice(EYES),
        "nose": rng.choice(NOSES),
        "lips": rng.choice(LIPS),
        "skin": rng.choice(SKIN),
        "feature": rng.choice(FEATURES),
        "camera_signature": rng.choice(CAMERA_SIGNATURES),
    }
    text = (
        f"Уникальное лицо модели {name}: {data['face_shape']}, {data['eyes']}, "
        f"{data['nose']}, {data['lips']}, {data['skin']}, {data['feature']}. "
        "Это не стандартное лицо из модели; сохранять эти черты во всех кадрах. "
        f"Визуальный якорь съёмки: {data['camera_signature']}."
    )
    data["identity_anchor_ru"] = text
    data["identity_anchor_en"] = (
        f"Unique fixed facial identity for model {name}: {data['face_shape']}, {data['eyes']}, "
        f"{data['nose']}, {data['lips']}, {data['skin']}, {data['feature']}. "
        "Do not use a generic default face. Preserve these exact facial traits across all shots. "
        f"Camera identity: {data['camera_signature']}."
    )
    return data
