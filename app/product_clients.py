"""Product-aware generation clients for AI Content Factory.

Two different jobs are intentionally separated:
1) clothing / dress -> virtual try-on, so the garment reference is actually worn
2) bottle / chocolate / cosmetics -> product integration, so the uploaded product is composited into a scene
"""
from __future__ import annotations

import logging
import os
from typing import Any

import fal_client

from app.config import settings

log = logging.getLogger(__name__)
os.environ["FAL_KEY"] = settings.fal_key


def _first_image_url(result: dict[str, Any]) -> str:
    images = result.get("images") or result.get("image") or []
    if isinstance(images, dict):
        url = images.get("url")
        if url:
            return url
    if isinstance(images, list) and images:
        first = images[0]
        if isinstance(first, dict) and first.get("url"):
            return first["url"]
        if isinstance(first, str):
            return first
    # Some fal endpoints return `output` or `result` variants.
    for key in ("output", "result", "url"):
        value = result.get(key)
        if isinstance(value, str):
            return value
        if isinstance(value, dict) and value.get("url"):
            return value["url"]
    raise RuntimeError(f"No image URL in fal result: {str(result)[:400]}")


async def generate_tryon(
    *,
    model_image_url: str,
    garment_image_url: str,
    category: str = "one-pieces",
    quality: str = "balanced",
) -> str:
    """Generate virtual try-on image with FASHN.

    fal-ai/fashn/tryon/v1.5 accepts `model_image` and `garment_image` URLs.
    Extra fields are optional; if fal changes/ignores them the required fields still work.
    """
    # Keep only the documented required fields. FASHN auto-detects garment type
    # (tops / bottoms / one-pieces) and works with flat-lay or on-model garment photos.
    arguments: dict[str, Any] = {
        "model_image": model_image_url,
        "garment_image": garment_image_url,
    }
    log.info("fal.ai try-on: model=%s category=%s", settings.tryon_model, category)
    try:
        result = await fal_client.subscribe_async(
            settings.tryon_model,
            arguments=arguments,
            with_logs=False,
        )
    except Exception as e:
        log.exception("fal.ai try-on failed")
        raise RuntimeError(f"try-on error: {str(e)[:300]}") from e
    return _first_image_url(result)


async def integrate_product(
    *,
    scene_image_url: str,
    product_image_url: str,
    prompt: str,
) -> str:
    """Blend a product image into an existing scene/background.

    Uses Qwen product integration endpoint. If it fails, caller should fall back to the base scene.
    """
    arguments: dict[str, Any] = {
        "image_urls": [scene_image_url, product_image_url],
        "prompt": prompt,
        "num_images": 1,
        "lora_scale": 1,
    }
    log.info("fal.ai product integrate: model=%s", settings.product_integration_model)
    try:
        result = await fal_client.subscribe_async(
            settings.product_integration_model,
            arguments=arguments,
            with_logs=False,
        )
    except Exception as e:
        log.exception("fal.ai product integration failed")
        raise RuntimeError(f"product integration error: {str(e)[:300]}") from e
    return _first_image_url(result)


async def product_lifestyle_shot(
    *,
    product_image_url: str,
    scene_description: str,
    placement: str = "bottom_center",
) -> str:
    """Fallback/alternate product-only lifestyle shot via Bria Product Shot."""
    arguments: dict[str, Any] = {
        "image_url": product_image_url,
        "scene_description": scene_description,
        "placement_type": "manual_placement",
        "manual_placement_selection": placement,
        "num_results": 1,
        "fast": True,
    }
    log.info("fal.ai Bria product shot: model=%s", settings.product_shot_model)
    try:
        result = await fal_client.subscribe_async(
            settings.product_shot_model,
            arguments=arguments,
            with_logs=False,
        )
    except Exception as e:
        log.exception("fal.ai product shot failed")
        raise RuntimeError(f"product shot error: {str(e)[:300]}") from e
    return _first_image_url(result)
