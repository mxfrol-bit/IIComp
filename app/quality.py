"""Quality helpers for pro commercial content."""
from __future__ import annotations

from app.config import settings

NEGATIVE_TAIL = (
    "Avoid low quality, plastic skin, distorted fingers, deformed anatomy, duplicate faces, "
    "messy background, fake text, unreadable brand label, warped packaging, watermark, "
    "over-smoothed skin, noisy jpeg artifacts, explicit nudity."
)

SCENE_TAILS = {
    "portrait": "sharp eyes, real skin pores, premium portrait lens, controlled daylight, high-end model test",
    "product": "product is visually clear, correct perspective, believable shadows, packaging shape preserved, ad-ready composition",
    "fashion": "full outfit visible, editorial pose, garment shape preserved, fashion lookbook quality",
    "video": "stable face, stable product, subtle natural motion, no morphing, no flicker, commercial social media reel",
}


def enhance_prompt(prompt: str, kind: str = "product") -> str:
    """Add production-grade style tail without changing the user's scenario."""
    mode = (settings.photo_quality_mode or "pro").lower()
    if mode == "fast":
        return prompt
    tail = settings.prompt_quality_tail or ""
    scene_tail = SCENE_TAILS.get(kind, SCENE_TAILS["product"])
    if mode == "max":
        scene_tail += ", award-winning advertising photography, clean magazine layout, premium retouching, crisp details"
    return f"{prompt}. {tail}. {scene_tail}. {NEGATIVE_TAIL}"
