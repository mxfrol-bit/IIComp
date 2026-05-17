"""Prompt builders for AI Content Factory."""
from __future__ import annotations

from typing import Optional

from app.factory_catalog import PRODUCT_CATEGORIES

BASE_PHOTO_STYLE = (
    "premium commercial photography for Instagram ads, realistic high-end influencer content, "
    "editorial lighting, natural skin texture, accurate hands, believable fabric and product materials, "
    "clean composition, native advertising aesthetic, expensive but authentic, brand-safe, no text artifacts, no watermark"
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
        "Show the product naturally and clearly, keep the packaging shape, fabric, color and label details believable, make it look like native advertising."
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
        "The result must look like a ready-to-post premium Instagram or advertising asset, not a raw AI render. "
        f"{NEGATIVE_STYLE}."
    )


def build_video_prompt(content_gen: dict, product: Optional[dict], scenario: dict) -> str:
    product_part = product_text(product)
    return (
        f"{scenario['prompt']}. Keep the same person and same product from the starting image. "
        "Natural realistic motion, no face morphing, no product deformation, smooth social-media commercial video. "
        f"{product_part} Brand-safe, premium, native ad style."
    )


def build_base_scene_for_product_prompt(model: dict, product: Optional[dict], scenario: dict) -> str:
    """Create a clean base scene where product will be integrated later.

    For clothing try-on we need the model visible enough for VTON; for other products we need
    a natural empty placement area so the product integration endpoint has somewhere to blend it.
    """
    category = (product or {}).get("category") or ""
    if category == "clothes":
        return (
            f"{BASE_PHOTO_STYLE}. Virtual AI model: {model.get('name')}. {persona_text(model)}. "
            f"Scene: {scenario['prompt']}. Full body or 3/4 body visible, standing naturally, clear torso and legs, "
            "simple plain neutral outfit suitable for virtual try-on replacement, realistic body proportions, "
            "clean lighting, no product object in hand. The image must be a good model reference for clothing try-on. "
            f"{NEGATIVE_STYLE}."
        )
    return (
        f"{BASE_PHOTO_STYLE}. Virtual AI model: {model.get('name')}. {persona_text(model)}. "
        f"Scene: {scenario['prompt']}. Leave a natural empty space for a product placement, "
        "model pose and composition suitable for native advertising, realistic lifestyle background, no fake product yet. "
        f"{NEGATIVE_STYLE}."
    )


def build_product_integration_prompt(product: dict, scenario: dict) -> str:
    category = PRODUCT_CATEGORIES.get(product.get("category") or "", product.get("category") or "product")
    title = product.get("title") or "product"
    desc = product.get("description") or ""
    return (
        f"Blend the uploaded product into the scene as realistic native advertising. Product: {title}. "
        f"Category: {category}. Details: {desc}. Scene target: {scenario['prompt']}. "
        "Keep the product shape, color, packaging and visual identity from the reference image. "
        "Correct perspective, scale, lighting and shadows. Preserve the real product silhouette and key visual details. Make it look natural, premium and ready for Instagram ads. "
        "Do not invent unreadable text, do not distort the product, do not remove the person from the scene."
    )


def clothing_tryon_category(product: Optional[dict]) -> str:
    """Map our product category/details to FASHN category."""
    if not product:
        return "one-pieces"
    text = f"{product.get('title','')} {product.get('description','')}".lower()
    if any(w in text for w in ("плать", "dress", "jumpsuit", "комбинез", "one piece", "one-piece")):
        return "one-pieces"
    if any(w in text for w in ("юбк", "брюк", "pants", "skirt", "shorts", "джинс")):
        return "bottoms"
    return "tops"
