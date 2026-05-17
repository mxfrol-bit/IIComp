"""Prompt builders for AI Content Factory."""
from __future__ import annotations

from typing import Optional

from app.factory_catalog import PRODUCT_CATEGORIES

BASE_PHOTO_STYLE = (
    "professional commercial photography, realistic high-quality image, premium Instagram content, "
    "authentic influencer style, clean composition, natural skin texture, realistic hands, detailed product photography, "
    "no text artifacts, no watermark, no distorted label, tasteful, brand-safe"
)

NEGATIVE_STYLE = (
    "avoid: extra fingers, distorted hands, blurry face, duplicate person, strange anatomy, broken product, "
    "fake text, unreadable label, watermark, logo hallucination, low quality, explicit nudity"
)


def persona_text(model: dict) -> str:
    persona = model.get("persona_json") or model.get("persona") or {}
    if not isinstance(persona, dict):
        persona = {}
    parts = []
    for key in ("age", "hair_color", "hair_length", "appearance", "style", "niche"):
        val = persona.get(key)
        if val:
            parts.append(f"{key.replace('_', ' ')}: {val}")
    identity_note = persona.get("identity_note") or "same consistent face, same facial identity across all shots"
    parts.append(identity_note)
    return ", ".join(parts)


def product_text(product: Optional[dict]) -> str:
    if not product:
        return ""
    category = PRODUCT_CATEGORIES.get(product.get("category") or "", product.get("category") or "product")
    title = product.get("title") or "product"
    description = product.get("description") or ""
    return (
        f"Product to advertise: {title}. Product category: {category}. "
        f"Product description and visual details: {description}. "
        "Show the product naturally and clearly, keep the packaging shape believable, make it look like native advertising."
    )


def build_hero_prompt(model: dict) -> str:
    return (
        f"{BASE_PHOTO_STYLE}. Create a hero portrait for a virtual AI model named {model.get('name')}. "
        f"Model identity: {persona_text(model)}. "
        "Close-up portrait, soft daylight, clean premium background, confident but natural expression, "
        "usable as the fixed identity reference for future ad campaigns. "
        f"{NEGATIVE_STYLE}."
    )


def build_identity_pack_prompt(model: dict, view: str) -> str:
    return (
        f"{BASE_PHOTO_STYLE}. Same AI model identity as the hero portrait. {persona_text(model)}. "
        f"Create identity reference image: {view}. Neutral clean background, accurate face consistency, "
        "professional model digitals, no product, no heavy makeup, clear facial structure. "
        f"{NEGATIVE_STYLE}."
    )


def build_photo_prompt(model: dict, product: Optional[dict], scenario: dict) -> str:
    product_part = product_text(product)
    product_focus = "" if product else "No product placement, focus on model and content style."
    return (
        f"{BASE_PHOTO_STYLE}. Virtual AI model: {model.get('name')}. {persona_text(model)}. "
        f"Scene: {scenario['prompt']}. {product_part} {product_focus} "
        "The result must look like a ready-to-post Instagram or advertising asset. "
        f"{NEGATIVE_STYLE}."
    )


def build_video_prompt(content_gen: dict, product: Optional[dict], scenario: dict) -> str:
    product_part = product_text(product)
    return (
        f"{scenario['prompt']}. Keep the same person and same product from the starting image. "
        "Natural realistic motion, no face morphing, no product deformation, smooth social-media commercial video. "
        f"{product_part} Brand-safe, premium, native ad style."
    )
